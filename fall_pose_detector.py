# ai/fall_pose_detector.py

import numpy as np
import math

def extract_keypoints(res):
    """Extract keypoints safely from YOLO pose result."""
    if res is None or res.keypoints is None:
        return None

    try:
        kpts = res.keypoints[0].xy.cpu().numpy()
        conf = res.keypoints[0].conf.cpu().numpy()
    except Exception:
        return None

    # Require enough keypoints (should be 17 for YOLO-Pose)
    if kpts is None or len(kpts) < 12:
        return None

    keypoints = []
    for i in range(len(kpts)):
        try:
            x = float(kpts[i][0])
            y = float(kpts[i][1])
            c = float(conf[i])
            keypoints.append((x, y, c))
        except:
            return None

    return keypoints


def compute_torso_angle(k):
    """Compute torso angle from keypoints."""
    L_sh, R_sh = k[5], k[6]     # shoulders
    L_hp, R_hp = k[11], k[12]   # hips

    sx = (L_sh[0] + R_sh[0]) / 2
    sy = (L_sh[1] + R_sh[1]) / 2
    hx = (L_hp[0] + R_hp[0]) / 2
    hy = (L_hp[1] + R_hp[1]) / 2

    dx = hx - sx
    dy = hy - sy

    ang = abs(math.degrees(math.atan2(dy, dx)))
    return min(ang, 180 - ang)  # angle normalized


def com(box):
    """Center of mass (center of person box)."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


class HybridFallDetector:
    def __init__(self):
        self.history = {}

    def init_track(self, tid, com_y):
        self.history[tid] = {
            "prev_com_y": com_y,
            "com_drop_accum": 0,
            "prev_head_y": None,
            "head_velocity_accum": 0,
            "torso_angle_list": [],
            "motion_burst": 0,
            "still_frames": 0,
            "fall_confirmed": False
        }

    def update(self, tid, pose_res, box, flow_mag):
        """Hybrid rule-based + pose-based fall detection."""

        x1, y1, x2, y2 = box
        _, cy = com(box)

        if tid not in self.history:
            self.init_track(tid, cy)

        h = self.history[tid]

        # Optical flow sudden movement
        h["motion_burst"] = flow_mag

        # ======================================================
        # SAFE KEYPOINT EXTRACTION (NO CRASHES)
        # ======================================================
        if pose_res is None or pose_res.keypoints is None:
            k = None
        else:
            k = extract_keypoints(pose_res)

        # ======================================================
        # IF POSE AVAILABLE → USE POSE SIGNALS
        # ======================================================
        if k is not None:

            # Torso angle
            angle = compute_torso_angle(k)
            h["torso_angle_list"].append(angle)
            if len(h["torso_angle_list"]) > 7:
                h["torso_angle_list"] = h["torso_angle_list"][-7:]

            # Head velocity
            head_y = k[0][1]
            if h["prev_head_y"] is not None:
                v = abs(head_y - h["prev_head_y"])
                h["head_velocity_accum"] = (
                    0.8 * h["head_velocity_accum"] + 0.2 * v
                )
            h["prev_head_y"] = head_y

        # ======================================================
        # COM DROP (body goes down suddenly)
        # ======================================================
        if h["prev_com_y"] is not None:
            drop = cy - h["prev_com_y"]
            if drop > 3:
                h["com_drop_accum"] += drop
        h["prev_com_y"] = cy

        # ======================================================
        # STILLNESS (person not moving after fall)
        # ======================================================
        if flow_mag < 0.3:
            h["still_frames"] += 1
        else:
            h["still_frames"] = 0

        # ======================================================
        # FALL SCORING
        # ======================================================
        torso_mean = (
            np.mean(h["torso_angle_list"])
            if h["torso_angle_list"] else 90
        )

        score = (
            (h["motion_burst"] > 2.0) +
            (h["com_drop_accum"] > 30) +
            (h["head_velocity_accum"] > 3) +
            (torso_mean < 35) +
            (h["still_frames"] > 10)
        )

        # Fall confirmed
        if score >= 3 and not h["fall_confirmed"]:
            h["fall_confirmed"] = True
            return True

        return False