# ai/utils.py
import cv2
import numpy as np

def blur_region(frame, x1, y1, x2, y2):
    h, w = frame.shape[:2]

    # clamp bounds
    x1 = max(0, min(w - 1, x1))
    y1 = max(0, min(h - 1, y1))
    x2 = max(0, min(w - 1, x2))
    y2 = max(0, min(h - 1, y2))

    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return frame[y1:y2, x1:x2]

    blurred = cv2.GaussianBlur(roi, (51, 51), 30)
    return blurred


def draw_box(frame, box, color=(255, 200, 0), label=None):
    x1, y1, x2, y2 = box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    if label:
        cv2.putText(frame, label, (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def compute_flow_magnitude(prev_gray, curr_gray):
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, curr_gray, None,
        0.5, 3, 15, 3, 5, 1.2, 0
    )
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    return float(np.mean(mag))