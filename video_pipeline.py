# ai/video_pipeline.py
import cv2
import os
import time
from ultralytics import YOLO

from ai.tracker import Tracker
from ai.face_tracker import FaceTracker
from ai.fall_pose_detector import HybridFallDetector
import ai.utils as utils
from ai.paths import RAW_CLIPS_DIR, SECURE_RAW_DIR


BASE = os.path.dirname(__file__)

person_model = YOLO(os.path.join(BASE, "models", "yolov8m.pt"))
face_model   = YOLO(os.path.join(BASE, "models", "yolov8n-face.pt"))
pose_model   = YOLO(os.path.join(BASE, "models", "yolov8m-pose.pt"))

tracker = Tracker()
face_tracker = FaceTracker()
fall_detector = HybridFallDetector()


def nms_safe(dets, iou_th=0.5):
    if not dets: return []
    dets = sorted(dets, key=lambda x: x[4], reverse=True)
    final = []

    while dets:
        best = dets.pop(0)
        new = []
        for d in dets:
            x1=max(best[0],d[0]); y1=max(best[1],d[1])
            x2=min(best[2],d[2]); y2=min(best[3],d[3])
            inter=max(0,x2-x1)*max(0,y2-y1)
            a1=(best[2]-best[0])*(best[3]-best[1])
            a2=(d[2]-d[0])*(d[3]-d[1])
            uni=a1+a2-inter
            iou=inter/uni if uni>0 else 0
            if iou < iou_th:
                new.append(d)
        dets=new
        final.append(best)
    return final


def process_video(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Error opening video:", source)
        return

    w,h = int(cap.get(3)), int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("output_redacted.mp4", fourcc, 15, (w,h))

    prev_gray=None

    fall_writer=None
    fall_frames_left=0
    fall_cooldown=0
    curr_fall_path=None

    while True:
        ok, frame = cap.read()
        if not ok: break

        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        flow_mag=0
        if prev_gray is not None:
            flow_mag=utils.compute_flow_magnitude(prev_gray,gray)
        prev_gray=gray.copy()

        # Person detection
        dets=[]
        pr = person_model(frame, conf=0.25, verbose=False)
        for b in pr[0].boxes:
            if int(b.cls[0]) != 0:
                continue
            conf=float(b.conf[0])
            x1,y1,x2,y2=b.xyxy[0].cpu().numpy().astype(float)
            dets.append([x1,y1,x2,y2,conf])
        dets=nms_safe(dets)
        person_boxes=[d[:4] for d in dets]

        # Tracking
        tracked=tracker.update(person_boxes)
        person_map={}

        for x1,y1,x2,y2,tid in tracked:
            x1=int(max(0,min(w,x1)))
            y1=int(max(0,min(h,y1)))
            x2=int(max(0,min(w,x2)))
            y2=int(max(0,min(h,y2)))
            box=(x1,y1,x2,y2)
            person_map[tid]=box
            utils.draw_box(frame, box, label=f"ID {tid}")

        # Pose
        pose_res = pose_model(frame, conf=0.25, verbose=False)

        # Face detection + redaction
        faces=[]
        fr=face_model(frame, conf=0.40, verbose=False)
        for r in fr:
            for b in r.boxes:
                x1,y1,x2,y2 = b.xyxy[0].cpu().numpy().astype(int)
                faces.append([x1,y1,x2,y2])

        tracked_faces=face_tracker.update(faces)
        for fid,(fx1,fy1,fx2,fy2) in tracked_faces.items():
            pw=int((fx2-fx1)*0.35)
            ph=int((fy2-fy1)*0.35)
            bx1=max(0,fx1-pw); by1=max(0,fy1-ph)
            bx2=min(w,fx2+pw); by2=min(h,fy2+ph)
            blur=utils.blur_region(frame,bx1,by1,bx2,by2)
            frame[by1:by2, bx1:bx2] = blur

        # Fall detection
        if fall_cooldown > 0:
            fall_cooldown -= 1
        else:
            for tid,box in person_map.items():
                # associated pose = just use highest‑confidence pose
                pose_data = pose_res[0]
                isfall = fall_detector.update(tid, pose_data, box, flow_mag)
                if isfall:
                    timestamp=int(time.time())
                    curr_fall_path=os.path.join(
                        RAW_CLIPS_DIR,
                        f"fall_{tid}_{timestamp}.mp4"
                    )
                    fall_writer=cv2.VideoWriter(curr_fall_path,fourcc,15,(w,h))
                    fall_frames_left=15
                    fall_cooldown=30
                    break

        if fall_frames_left>0:
            fall_writer.write(frame)
            fall_frames_left-=1

            if fall_frames_left<=0:
                fall_writer.release()
                final=os.path.join(
                    SECURE_RAW_DIR,
                    os.path.basename(curr_fall_path)
                )
                os.rename(curr_fall_path,final)

        out.write(frame)
        cv2.imshow("CivicShield Output",frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if fall_writer is not None:
        fall_writer.release()

    cap.release()
    out.release()
    cv2.destroyAllWindows()