# ai/tracker.py
import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter


class Track:
    def __init__(self, box, track_id):
        self.id = track_id
        self.lost_frames = 0

        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([
            [1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0],
            [0,0,1,0,0,0,1],
            [0,0,0,1,0,0,0],
            [0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0],
            [0,0,0,0,0,0,1],
        ])
        self.kf.H = np.array([
            [1,0,0,0,0,0,0],
            [0,1,0,0,0,0,0],
            [0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0],
        ])

        self.kf.P *= 10
        self.kf.R *= 0.01

        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        w  = (box[2] - box[0])
        h  = (box[3] - box[1])

        self.kf.x[:4] = np.array([cx, cy, w, h]).reshape(4,1)

    def predict(self):
        self.kf.predict()

    def update(self, det_box):
        cx = (det_box[0] + det_box[2]) / 2
        cy = (det_box[1] + det_box[3]) / 2
        w  = det_box[2] - det_box[0]
        h  = det_box[3] - det_box[1]
        self.kf.update([cx,cy,w,h])


class Tracker:
    def __init__(self, max_age=25, iou_threshold=0.25):
        self.tracks = {}
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self.next_id = 1

    def _iou(self, a, b):
        x1=max(a[0],b[0]); y1=max(a[1],b[1])
        x2=min(a[2],b[2]); y2=min(a[3],b[3])
        inter=max(0,x2-x1)*max(0,y2-y1)
        area_a=(a[2]-a[0])*(a[3]-a[1])
        area_b=(b[2]-b[0])*(b[3]-b[1])
        union=area_a+area_b-inter
        return inter/union if union>0 else 0

    def update(self, detections):
        if len(self.tracks)==0:
            for d in detections:
                self.tracks[self.next_id] = Track(d, self.next_id)
                self.next_id += 1
            return self._output()

        ids=list(self.tracks.keys())
        preds=[]
        for tid in ids:
            self.tracks[tid].predict()
            cx,cy,w,h = self.tracks[tid].kf.x[:4].reshape(-1)
            preds.append([cx-w/2, cy-h/2, cx+w/2, cy+h/2])

        if len(detections)==0:
            for tid in ids:
                self.tracks[tid].lost_frames += 1
            self._cleanup()
            return self._output()

        iou_matrix=np.zeros((len(detections),len(preds)))
        for d,det in enumerate(detections):
            for t,pb in enumerate(preds):
                iou_matrix[d,t] = self._iou(det,pb)

        rows,cols = linear_sum_assignment(-iou_matrix)
        used_det=set(); used_tid=set()

        for r,c in zip(rows,cols):
            if iou_matrix[r,c] >= self.iou_threshold:
                tid = ids[c]
                self.tracks[tid].update(detections[r])
                used_det.add(r)
                used_tid.add(tid)

        for i,d in enumerate(detections):
            if i not in used_det:
                self.tracks[self.next_id] = Track(d,self.next_id)
                self.next_id += 1

        for tid in ids:
            if tid not in used_tid:
                self.tracks[tid].lost_frames += 1

        self._cleanup()
        return self._output()

    def _cleanup(self):
        dead=[tid for tid,tr in self.tracks.items() if tr.lost_frames>self.max_age]
        for tid in dead:
            del self.tracks[tid]

    def _output(self):
        out=[]
        for tid,tr in self.tracks.items():
            cx,cy,w,h = tr.kf.x[:4].reshape(-1)
            out.append([cx-w/2, cy-h/2, cx+w/2, cy+h/2, tid])
        return out