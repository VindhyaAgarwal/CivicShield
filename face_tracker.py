# ai/face_tracker.py
import numpy as np

class FaceTracker:
    def __init__(self, max_age=12, iou_threshold=0.30):
        self.tracks={}
        self.max_age=max_age
        self.iou_threshold=iou_threshold
        self.next_face_id=1

    def _iou(self,a,b):
        x1=max(a[0],b[0]); y1=max(a[1],b[1])
        x2=min(a[2],b[2]); y2=min(a[3],b[3])
        inter=max(0,x2-x1)*max(0,y2-y1)
        a_area=(a[2]-a[0])*(a[3]-a[1])
        b_area=(b[2]-b[0])*(b[3]-b[1])
        union=a_area+b_area-inter
        return inter/union if union>0 else 0

    def update(self, dets):
        updated={}
        used_det=set()
        used_tracks=set()
        ids=list(self.tracks.keys())

        for tid in ids:
            best_iou=0; best_idx=None
            for i,d in enumerate(dets):
                if i in used_det: continue
                iou=self._iou(self.tracks[tid][0],d)
                if iou>best_iou and iou>self.iou_threshold:
                    best_iou=iou; best_idx=i

            if best_idx is not None:
                updated[tid]=(dets[best_idx],0)
                used_det.add(best_idx)
                used_tracks.add(tid)

        for i,d in enumerate(dets):
            if i not in used_det:
                updated[self.next_face_id]=(d,0)
                self.next_face_id+=1

        for tid in ids:
            if tid not in used_tracks:
                box,age=self.tracks[tid]
                age+=1
                if age<=self.max_age:
                    updated[tid]=(box,age)

        self.tracks=updated
        return {tid:v[0] for tid,v in self.tracks.items()}