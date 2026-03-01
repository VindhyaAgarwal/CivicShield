# ai/paths.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

RAW_CLIPS_DIR = os.path.join(ROOT_DIR, "raw")
SECURE_RAW_DIR = os.path.join(ROOT_DIR, "secure_raw")

os.makedirs(RAW_CLIPS_DIR, exist_ok=True)
os.makedirs(SECURE_RAW_DIR, exist_ok=True)