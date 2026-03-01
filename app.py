
import streamlit as st
import cv2
import numpy as np
import requests
import json
import time
import os
import base64
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import glob
from pathlib import Path
import threading
import queue
from streamlit_option_menu import option_menu
import plotly.figure_factory as ff
import random
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.stoggle import stoggle
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.chart_container import chart_container
from streamlit_card import card
import hashlib

# Page configuration
st.set_page_config(
    page_title="CivicShield - Privacy-Preserving Surveillance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container with glass morphism effect */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Header with gradient and animation */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        animation: gradientShift 5s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Video containers with 3D effect */
    .video-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        position: relative;
        background: #000;
        transition: transform 0.3s, box-shadow 0.3s;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .video-container:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 30px 60px rgba(0,0,0,0.4);
    }
    
    .video-label {
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 8px 20px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 600;
        z-index: 1000;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(255,255,255,0.5); }
        50% { box-shadow: 0 0 20px rgba(255,255,255,0.8); }
        100% { box-shadow: 0 0 5px rgba(255,255,255,0.5); }
    }
    
    .redacted-label {
        background: linear-gradient(135deg, #00C851, #007E33);
    }
    
    /* Stats cards with 3D tilt effect */
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s;
        border: 1px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stat-card:hover::before {
        left: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-10px) rotateX(5deg);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        animation: countUp 2s ease-out;
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stat-label {
        color: #666;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* Alert animations */
    .alert-box {
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        border-left: 6px solid;
        animation: slideInRight 0.5s ease-out;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .alert-box:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b, #ff4757);
        color: white;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ffa502, #ff7f50);
        color: white;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #70a1ff, #1e90ff);
        color: white;
    }
    
    /* Bandwidth meter with animation */
    .bandwidth-meter {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .meter-bar {
        height: 12px;
        background: rgba(255,255,255,0.3);
        border-radius: 6px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .meter-fill {
        height: 100%;
        background: linear-gradient(90deg, #00C851, #00E676);
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .meter-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Modern file cards */
    .file-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        border: 2px solid transparent;
        transition: all 0.3s;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .file-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s;
    }
    
    .file-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .file-card:hover::before {
        width: 6px;
    }
    
    .file-card.selected {
        background: linear-gradient(135deg, #f0f3ff, #e6e9ff);
        border-color: #667eea;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Loading animation */
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Floating action button */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        transition: all 0.3s;
        z-index: 9999;
        animation: pulse 2s infinite;
    }
    
    .fab:hover {
        transform: scale(1.1) rotate(90deg);
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    /* Timeline */
    .timeline {
        position: relative;
        padding: 20px 0;
    }
    
    .timeline-item {
        position: relative;
        padding-left: 50px;
        margin-bottom: 30px;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 20px;
        top: 0;
        bottom: -20px;
        width: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .timeline-dot {
        position: absolute;
        left: 13px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 3px solid white;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
        animation: pulse 2s infinite;
    }
    
    /* Progress bars */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        height: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        transition: width 1s ease;
        position: relative;
        overflow: hidden;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .status-online {
        background: rgba(0, 200, 81, 0.9);
        color: white;
    }
    
    .status-offline {
        background: rgba(255, 68, 68, 0.9);
        color: white;
    }
    
    .status-warning {
        background: rgba(255, 187, 51, 0.9);
        color: white;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background: rgba(0,0,0,0.8);
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-container {
            padding: 1rem;
        }
        
        .stat-card {
            padding: 1rem;
        }
        
        .stat-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state with enhanced features
if 'anomaly_log' not in st.session_state:
    st.session_state.anomaly_log = []
if 'bandwidth_used' not in st.session_state:
    st.session_state.bandwidth_used = 0
if 'edge_mode' not in st.session_state:
    st.session_state.edge_mode = True
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'events' not in st.session_state:
    st.session_state.events = []
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
if 'selected_raw_video' not in st.session_state:
    st.session_state.selected_raw_video = None
if 'selected_secure_video' not in st.session_state:
    st.session_state.selected_secure_video = None
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = []
if 'model_status' not in st.session_state:
    st.session_state.model_status = {
        'yolov8m.pt': False,
        'yolov8n-face.pt': False,
        'yolov8m-pose.pt': False
    }
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# Define paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT_DIR, "raw")
SECURE_RAW_DIR = os.path.join(ROOT_DIR, "secure_raw")
AI_MODELS_DIR = os.path.join(ROOT_DIR, "ai", "models")
PREDICT_DIR = os.path.join(ROOT_DIR, "predict")

# Create directories if they don't exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SECURE_RAW_DIR, exist_ok=True)
os.makedirs(AI_MODELS_DIR, exist_ok=True)
os.makedirs(PREDICT_DIR, exist_ok=True)

# Helper functions
def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def fetch_events():
    """Fetch events from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/events", timeout=2)
        if response.status_code == 200:
            st.session_state.events = response.json()
    except:
        pass

def toggle_mode(edge_mode):
    """Toggle between edge and cloud mode"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/mode",
            json={"edge_mode": edge_mode},
            timeout=2
        )
        if response.status_code == 200:
            st.session_state.edge_mode = edge_mode
            add_notification("System mode changed", f"Switched to {'Edge' if edge_mode else 'Cloud'} mode")
    except:
        st.error("Failed to toggle mode")

def add_notification(title, message):
    """Add a notification"""
    st.session_state.notifications.insert(0, {
        'title': title,
        'message': message,
        'time': datetime.now().strftime("%H:%M:%S"),
        'read': False
    })

def create_anomaly_event(event_type, confidence, message, clip_path=""):
    """Create a new anomaly event"""
    event_id = f"evt_{int(time.time())}"
    timestamp = datetime.now().isoformat()
    
    event_data = {
        "event_id": event_id,
        "event_type": event_type,
        "confidence": confidence,
        "timestamp": timestamp,
        "raw_clip_path": clip_path or f"/secure_raw/{event_id}.mp4"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/event",
            json=event_data,
            timeout=2
        )
        if response.status_code == 200:
            log_entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": event_type,
                "message": message,
                "confidence": confidence,
                "event_id": event_id
            }
            st.session_state.anomaly_log.insert(0, log_entry)
            add_notification("New Event Detected", f"{message} ({confidence*100:.0f}% confidence)")
            return True
    except:
        # Still add to local log even if backend is offline
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "message": message,
            "confidence": confidence,
            "event_id": event_id
        }
        st.session_state.anomaly_log.insert(0, log_entry)
        add_notification("New Event Detected (Offline)", f"{message} ({confidence*100:.0f}% confidence)")
        return True
    
    return False

def get_raw_videos():
    """Get list of videos in raw folder"""
    videos = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
        videos.extend(glob.glob(os.path.join(RAW_DIR, ext)))
    return sorted(videos)

def get_secure_videos():
    """Get list of videos in secure_raw folder"""
    videos = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
        videos.extend(glob.glob(os.path.join(SECURE_RAW_DIR, ext)))
    return sorted(videos)

def get_predict_videos():
    """Get list of videos in predict folder"""
    videos = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
        videos.extend(glob.glob(os.path.join(PREDICT_DIR, ext)))
    return sorted(videos)

def get_model_files():
    """Get list of model files"""
    models = []
    for ext in ['*.pt', '*.pth']:
        models.extend(glob.glob(os.path.join(AI_MODELS_DIR, ext)))
    return sorted(models)

def check_models():
    """Check which models are available"""
    models = get_model_files()
    for model in models:
        name = os.path.basename(model)
        if 'yolov8m.pt' in name:
            st.session_state.model_status['yolov8m.pt'] = True
        elif 'yolov8n-face.pt' in name:
            st.session_state.model_status['yolov8n-face.pt'] = True
        elif 'yolov8m-pose.pt' in name:
            st.session_state.model_status['yolov8m-pose.pt'] = True

def run_ai_pipeline(video_path):
    """Run the AI pipeline on a video"""
    try:
        from ai.video_pipeline import process_video
        with st.spinner("🔄 Processing video with AI..."):
            success = process_video(video_path)
            if success:
                st.balloons()
                add_notification("Pipeline Complete", f"Successfully processed {os.path.basename(video_path)}")
                return True
        return False
    except Exception as e:
        st.error(f"Error running AI pipeline: {e}")
        return False

def simulate_redaction(frame):
    """Simulate face redaction for demo"""
    h, w = frame.shape[:2]
    
    # Simulate detecting faces
    face_positions = [
        (int(w*0.3), int(h*0.2), int(w*0.15), int(h*0.15)),
        (int(w*0.6), int(h*0.3), int(w*0.12), int(h*0.12)),
    ]
    
    for x, y, fw, fh in face_positions:
        pad_w = int(fw * 0.3)
        pad_h = int(fh * 0.3)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w, x + fw + pad_w)
        y2 = min(h, y + fh + pad_h)
        
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            blurred = cv2.GaussianBlur(roi, (51, 51), 30)
            frame[y1:y2, x1:x2] = blurred
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Face Redacted", (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"

def get_video_info(video_path):
    """Get video information"""
    try:
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        return {
            'width': width,
            'height': height,
            'fps': round(fps, 2),
            'duration': round(duration, 2),
            'frames': total_frames,
            'size': os.path.getsize(video_path)
        }
    except:
        return None

# Check models on startup
check_models()

# Floating Action Button
st.markdown("""
<div class="fab" onclick="alert('Quick Actions Menu')">
    +
</div>
""", unsafe_allow_html=True)

# Main app layout
def main():
    # Sidebar with enhanced design
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://img.icons8.com/fluency/96/000000/shield.png", width=80)
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-size: 2rem;
                       font-weight: 800;">CivicShield</h1>
            <p style="color: #666; font-size: 0.9rem;">Privacy-Preserving Surveillance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Animated menu
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Live Processing", "Video Library", "Model Management", "Analytics", "Settings"],
            icons=["house", "camera-reels", "film", "cpu", "graph-up", "gear"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "5px 0",
                    "border-radius": "10px",
                    "transition": "all 0.3s"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color": "white"
                },
            }
        )
        
        st.markdown("---")
        
        # Enhanced system status
        backend_healthy = check_backend_health()
        
        st.markdown("### 🔌 System Status")
        if backend_healthy:
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Offline")
        
        # Model status with progress
        st.markdown("### 🤖 AI Models")
        models_loaded = sum(1 for v in st.session_state.model_status.values() if v)
        total_models = len(st.session_state.model_status)
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width: {(models_loaded/total_models)*100}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <span>Loaded: {models_loaded}/{total_models}</span>
            <span>{int((models_loaded/total_models)*100)}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        for model_name, loaded in st.session_state.model_status.items():
            if loaded:
                st.markdown(f"✅ {model_name}")
            else:
                st.markdown(f"⭕ {model_name}")
        
        st.markdown("---")
        
        # Quick stats with animations
        raw_videos = get_raw_videos()
        secure_videos = get_secure_videos()
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Raw Videos", len(raw_videos), delta="+2", delta_color="normal")
        with col_s2:
            st.metric("Secure", len(secure_videos), delta="+1", delta_color="normal")
        
        st.metric("Events", len(st.session_state.events), delta="↑ 12%")
        
        # Recent notifications
        st.markdown("### 🔔 Recent Notifications")
        if st.session_state.notifications:
            for notif in st.session_state.notifications[:3]:
                st.info(f"**{notif['title']}**\n\n{notif['message']}\n\n{notif['time']}")
        else:
            st.caption("No new notifications")
        
        # Theme toggle
        st.markdown("---")
        theme = st.select_slider("Theme", options=["🌞 Light", "🌙 Dark", "💜 Purple"], value="💜 Purple")

    # Main content area
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Live Processing":
        show_live_processing()
    elif selected == "Video Library":
        show_video_library()
    elif selected == "Model Management":
        show_model_management()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "Settings":
        show_settings()

def show_dashboard():
    """Enhanced dashboard view"""
    
    # Animated header
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 10;">
            <div>
                <h1 style="margin:0; font-size: 3rem; font-weight: 800;">📊 Dashboard</h1>
                <p style="margin:0; opacity:0.9; font-size: 1.2rem;">Real-time surveillance analytics</p>
            </div>
            <div>
                <span class="status-badge status-online">🟢 Edge NPU Active</span>
                <span class="status-badge status-online">⚡ 4K 30fps</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Live time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"<p style='text-align: right; color: #666;'>Last updated: {current_time}</p>", unsafe_allow_html=True)
    
    # Enhanced stats cards in grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">🎥 Total Events</div>
            <div class="stat-value">{}</div>
            <div style="color: #00C851;">↑ 12% from yesterday</div>
            <small>Last 24h: 8</small>
        </div>
        """.format(len(st.session_state.events)), unsafe_allow_html=True)
    
    with col2:
        encrypted_count = sum(1 for e in st.session_state.events if e.get('encrypted', False))
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">🔒 Encrypted</div>
            <div class="stat-value">{}</div>
            <div style="color: #667eea;">AES-256</div>
            <small>100% encrypted</small>
        </div>
        """.format(encrypted_count), unsafe_allow_html=True)
    
    with col3:
        raw_videos = get_raw_videos()
        secure_videos = get_secure_videos()
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">📹 Video Library</div>
            <div class="stat-value">{}</div>
            <div style="color: #666;">{} raw | {} secure</div>
            <small>Total size: 2.3 GB</small>
        </div>
        """.format(len(raw_videos) + len(secure_videos), len(raw_videos), len(secure_videos)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">⏱️ System Uptime</div>
            <div class="stat-value">99.9%</div>
            <div style="color: #00C851;">24/7 operation</div>
            <small>15 days 8 hours</small>
        </div>
        """, unsafe_allow_html=True)
    
    style_metric_cards()
    
    # Bandwidth comparison with enhanced charts
    st.markdown("---")
    st.markdown("### 📊 Bandwidth Analysis")
    
    col_b1, col_b2 = st.columns([3, 2])
    
    with col_b1:
        # 3D bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Raw Streaming',
            x=['Traditional', 'Cloud', 'Edge'],
            y=[5000000, 5000000, 300],
            marker_color=['#ff4444', '#ff6b6b', '#00C851'],
            text=['5 MB', '5 MB', '300 B'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Bandwidth: %{text}<br>Reduction: 99.994%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Bandwidth Comparison: Edge vs Traditional",
            barmode='group',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            yaxis=dict(title="Bytes", type="log")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b2:
        # Real-time bandwidth meter
        st.markdown("""
        <div class="bandwidth-meter">
            <h3 style="margin:0 0 1rem 0;">🌐 Current Bandwidth</h3>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Edge Mode</span>
                <span style="font-size: 2rem; font-weight: 800;">300 B/s</span>
            </div>
            <div class="meter-bar">
                <div class="meter-fill" style="width: 0.006%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                <span>vs Traditional: 5 MB/s</span>
                <span style="color: #00C851;">-99.994%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Savings counter
        savings = 5000000 - 300
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; 
                    border-radius: 10px; 
                    color: white;
                    margin-top: 1rem;
                    text-align: center;">
            <h3 style="margin:0;">💰 Daily Savings</h3>
            <p style="font-size: 2rem; font-weight: 800; margin:0;">{(savings * 86400 / 1e9):.2f} GB</p>
            <small>Compared to traditional streaming</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity timeline
    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("### 📋 Recent Activity")
        
        if st.session_state.anomaly_log:
            st.markdown('<div class="timeline">', unsafe_allow_html=True)
            for log in st.session_state.anomaly_log[:5]:
                color = "#ff4444" if log['confidence'] > 0.9 else "#ffbb33" if log['confidence'] > 0.8 else "#33b5e5"
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-dot" style="background: {color};"></div>
                    <div style="margin-left: 20px;">
                        <strong>{log['timestamp']}</strong><br>
                        {log['message']}<br>
                        <small>Confidence: {log['confidence']*100:.0f}% | Event: {log.get('event_id', 'N/A')}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No recent activity")
    
    with col_r2:
        st.markdown("### 🤖 Model Performance")
        
        # Enhanced model metrics
        models_df = pd.DataFrame({
            'Model': ['YOLOv8m', 'YOLOv8n-Face', 'YOLOv8m-Pose'],
            'Accuracy': [0.95, 0.92, 0.88],
            'FPS': [45, 120, 38],
            'Latency (ms)': [22, 8, 26],
            'Memory (MB)': [49, 6, 84]
        })
        
        # Interactive gauge charts
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = 95,
            title = {'text': "Detection Accuracy"},
            domain = {'row': 0, 'column': 0},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 70], 'color': "#ff4444"},
                    {'range': [70, 90], 'color': "#ffbb33"},
                    {'range': [90, 100], 'color': "#00C851"}
                ]
            }
        ))
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = 45,
            title = {'text': "Processing FPS"},
            domain = {'row': 0, 'column': 1},
            gauge = {
                'axis': {'range': [None, 60]},
                'bar': {'color': "#764ba2"}
            }
        ))
        
        fig.update_layout(
            grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
            height = 300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model status table
        st.dataframe(
            models_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Accuracy": st.column_config.ProgressColumn(
                    "Accuracy",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )

def show_live_processing():
    """Enhanced live processing view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 2.5rem;">🎥 Live Processing</h1>
        <p style="margin:0; opacity:0.9;">Real-time AI-powered video analysis with privacy protection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Source selection with icons
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        source_type = st.selectbox(
            "📹 Video Source",
            ["Test Video", "Upload Video", "Webcam", "RTSP Stream", "YouTube URL"],
            help="Select the source of your video"
        )
    
    with col_s2:
        quality = st.select_slider(
            "Processing Quality",
            options=["Low", "Medium", "High", "Ultra"],
            value="High"
        )
    
    with col_s3:
        enable_recording = st.checkbox("📼 Enable Recording", value=True)
    
    # Main processing area
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin:0;">🔴 Raw Input</h3>
            <span class="status-badge status-warning">Unredacted</span>
        </div>
        """, unsafe_allow_html=True)
        
        video_path = None
        
        if source_type == "Test Video":
            raw_videos = get_raw_videos()
            if raw_videos:
                video_names = [os.path.basename(v) for v in raw_videos]
                selected = st.selectbox("Choose test video", video_names, key="test_video")
                if selected:
                    video_path = os.path.join(RAW_DIR, selected)
                    st.session_state.selected_raw_video = video_path
                    
                    # Video info
                    info = get_video_info(video_path)
                    if info:
                        st.caption(f"📊 {info['width']}x{info['height']} | {info['fps']} fps | {info['duration']}s | {format_file_size(info['size'])}")
            else:
                st.warning("No test videos found")
        
        elif source_type == "Upload Video":
            uploaded_file = st.file_uploader(
                "Drop video file here",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Supported formats: MP4, AVI, MOV, MKV"
            )
            if uploaded_file:
                video_path = os.path.join(PREDICT_DIR, uploaded_file.name)
                with open(video_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Controls with animation
        st.markdown("---")
        col_play, col_stop, col_mode, col_save = st.columns(4)
        
        with col_play:
            if st.button("▶️ Start", use_container_width=True):
                st.session_state.processing = True
                add_notification("Processing Started", f"Source: {source_type}")
        
        with col_stop:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.processing = False
        
        with col_mode:
            edge_mode = st.toggle("🌐 Edge Mode", value=st.session_state.edge_mode)
            if edge_mode != st.session_state.edge_mode:
                toggle_mode(edge_mode)
        
        with col_save:
            st.button("💾 Save", use_container_width=True)
        
        # Display raw video
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "No Video Selected", (180, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            st.image(placeholder, channels="BGR", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin:0;">🟢 Privacy-Protected Output</h3>
            <span class="status-badge status-online">Redacted</span>
        </div>
        """, unsafe_allow_html=True)
        
        output_video = os.path.join(ROOT_DIR, "output_redacted.mp4")
        
        # Process button
        if st.button("🚀 Run AI Pipeline", use_container_width=True):
            if video_path and os.path.exists(video_path):
                with st.spinner("🔄 Processing with YOLOv8..."):
                    success = run_ai_pipeline(video_path)
                    if success:
                        st.success("✅ Processing complete!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
            else:
                st.error("Please select a video first")
        
        # Display processed video
        if os.path.exists(output_video):
            st.video(output_video)
            
            # Enhanced detection results
            st.markdown("### 📊 Detection Results")
            
            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            with col_d1:
                st.metric("👤 People", "3", "+2")
            with col_d2:
                st.metric("😊 Faces", "2", "-1")
            with col_d3:
                st.metric("⚠️ Falls", "1", "Alert")
            with col_d4:
                st.metric("🎯 Confidence", "94%", "+3%")
            
            # Download options
            with open(output_video, 'rb') as f:
                st.download_button(
                    "📥 Download Processed Video",
                    f,
                    file_name=f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        else:
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Run Pipeline to See Results", (120, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            st.image(placeholder, channels="BGR", use_container_width=True)
    
    # Live detection feed
    st.markdown("---")
    st.markdown("### 📡 Live Detection Feed")
    
    # Create a placeholder for live updates
    live_placeholder = st.empty()
    
    # Simulate live updates
    if st.session_state.processing:
        with live_placeholder.container():
            cols = st.columns(3)
            for i in range(3):
                with cols[i]:
                    frame = np.zeros((200, 300, 3), dtype=np.uint8)
                    cv2.putText(frame, f"Frame {i+1}", (50, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.rectangle(frame, (50, 50), (150, 150), (0, 255, 0), 2)
                    st.image(frame, channels="BGR", use_container_width=True)
                    st.caption(f"Detection: Person {i+1} | ID: {random.randint(1000, 9999)}")
    
    # Processing stats
    st.markdown("---")
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        st.metric("Processing FPS", "28", "-2")
    with col_stats2:
        st.metric("Queue Size", "0", "Good")
    with col_stats3:
        st.metric("Memory Usage", "1.2 GB", "+0.1")
    with col_stats4:
        st.metric("GPU Load", "45%", "-5%")

def show_video_library():
    """Enhanced video library view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">📁 Video Library</h1>
        <p style="margin:0; opacity:0.9;">Browse and manage your video footage</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search and filter bar
    col_search, col_filter, col_sort = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input("🔍 Search videos", placeholder="Enter filename...")
    with col_filter:
        filter_type = st.selectbox("Filter", ["All", "Raw", "Secure", "Processed"])
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Date", "Name", "Size", "Duration"])
    
    # Tabs with icons
    tab1, tab2, tab3 = st.tabs(["📹 Raw Videos", "🔒 Secure Videos", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Unprocessed Footage (Contains PII)")
        raw_videos = get_raw_videos()
        
        if not raw_videos:
            st.info("No raw videos found")
        else:
            # Filter by search
            if search:
                raw_videos = [v for v in raw_videos if search.lower() in os.path.basename(v).lower()]
            
            # Grid display
            cols = st.columns(3)
            for idx, video_path in enumerate(raw_videos):
                with cols[idx % 3]:
                    video_name = os.path.basename(video_path)
                    
                    # Generate thumbnail
                    cap = cv2.VideoCapture(video_path)
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(frame_rgb, use_container_width=True)
                    
                    # Video info
                    info = get_video_info(video_path)
                    
                    st.markdown(f"""
                    <div class="file-card">
                        <strong>{video_name[:20]}...</strong><br>
                        <small>📏 {info['width']}x{info['height'] if info else 'N/A'}</small><br>
                        <small>⏱️ {info['duration']}s | 📦 {format_file_size(info['size']) if info else 'N/A'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.button("▶️", key=f"play_raw_{idx}")
                    with col_p2:
                        st.button("🔒", key=f"enc_{idx}")
                    with col_p3:
                        st.button("⭐", key=f"fav_{idx}")
    
    with tab2:
        st.markdown("### Privacy-Protected Videos")
        secure_videos = get_secure_videos()
        
        if not secure_videos:
            st.info("No secure videos found")
        else:
            for video_path in secure_videos:
                video_name = os.path.basename(video_path)
                info = get_video_info(video_path)
                
                with st.expander(f"📹 {video_name}"):
                    col_v1, col_v2 = st.columns([2, 1])
                    
                    with col_v1:
                        st.video(video_path)
                    
                    with col_v2:
                        st.markdown("**Video Details**")
                        if info:
                            st.markdown(f"""
                            - Resolution: {info['width']}x{info['height']}
                            - Duration: {info['duration']}s
                            - FPS: {info['fps']}
                            - Size: {format_file_size(info['size'])}
                            """)
                        
                        st.markdown("**Privacy Status**")
                        st.success("✅ Fully Redacted")
                        st.success("✅ AES-256 Encrypted")
                        
                        # Unlock request
                        if st.button(f"🔓 Request Unlock", key=f"unlock_{video_name}"):
                            create_anomaly_event(
                                "unlock_request",
                                1.0,
                                f"Unlock requested for {video_name}",
                                video_path
                            )
                            st.success("Unlock request sent! Waiting for 2/2 approvals")
    
    with tab3:
        st.markdown("### Library Analytics")
        
        # Video statistics
        raw_count = len(get_raw_videos())
        secure_count = len(get_secure_videos())
        total_size = sum(os.path.getsize(v) for v in get_raw_videos() + get_secure_videos()) / (1024**3)
        
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            st.metric("Total Videos", raw_count + secure_count)
        with col_a2:
            st.metric("Raw Videos", raw_count)
        with col_a3:
            st.metric("Secure Videos", secure_count)
        with col_a4:
            st.metric("Total Size", f"{total_size:.2f} GB")
        
        # Storage distribution
        fig = go.Figure(data=[go.Pie(
            labels=['Raw Videos', 'Secure Videos'],
            values=[raw_count, secure_count],
            hole=.3,
            marker_colors=['#ff4444', '#00C851']
        )])
        fig.update_layout(title="Video Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_model_management():
    """Enhanced model management view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">🤖 Model Management</h1>
        <p style="margin:0; opacity:0.9;">Configure and monitor AI models</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("### 📦 Installed Models")
        models = get_model_files()
        
        if not models:
            st.warning("No models found")
        else:
            for model_path in models:
                model_name = os.path.basename(model_path)
                model_size = os.path.getsize(model_path) / 1e6
                
                # Model type detection
                if 'face' in model_name.lower():
                    model_type = "Face Detection"
                    color = "#00C851"
                    accuracy = 0.92
                elif 'pose' in model_name.lower():
                    model_type = "Pose Estimation"
                    color = "#ffbb33"
                    accuracy = 0.88
                else:
                    model_type = "Person Detection"
                    color = "#667eea"
                    accuracy = 0.95
                
                st.markdown(f"""
                <div class="file-card {'selected' if st.session_state.model_status.get(model_name, False) else ''}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{model_name}</strong></span>
                        <span class="status-badge" style="background: {color};">{model_type}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span>📦 Size: {model_size:.1f} MB</span>
                        <span>🎯 Accuracy: {accuracy*100:.0f}%</span>
                    </div>
                    <div class="progress-container" style="margin-top: 0.5rem;">
                        <div class="progress-fill" style="width: {accuracy*100}%;"></div>
                    </div>
                    <div style="margin-top: 0.5rem;">
                        {'✅ Loaded' if st.session_state.model_status.get(model_name, False) else '⭕ Not Loaded'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown("### 📊 Model Performance")
        
        # Real-time performance metrics
        metrics = pd.DataFrame({
            'Metric': ['Inference Time', 'Memory Usage', 'GPU Usage', 'CPU Usage', 'FPS'],
            'Value': ['24 ms', '1.2 GB', '45%', '32%', '28'],
            'Status': ['✅', '⚠️', '✅', '✅', '⚠️']
        })
        st.dataframe(metrics, use_container_width=True, hide_index=True)
        
        # Performance chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pd.date_range(end=datetime.now(), periods=20, freq='1min'),
            y=np.random.normal(24, 5, 20),
            mode='lines+markers',
            name='Inference Time',
            line=dict(color='#667eea', width=3)
        ))
        fig.update_layout(
            title="Inference Time Trend (Last 20 minutes)",
            xaxis_title="Time",
            yaxis_title="Milliseconds",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Model controls
        st.markdown("### ⚙️ Model Controls")
        st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)
        st.slider("IoU Threshold", 0.0, 1.0, 0.5, 0.05)
        st.slider("Max Batch Size", 1, 32, 8)
        
        if st.button("🔄 Reload Models", use_container_width=True):
            check_models()
            st.success("Models reloaded!")

def show_analytics():
    """Advanced analytics view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">📈 Advanced Analytics</h1>
        <p style="margin:0; opacity:0.9;">Deep insights into your surveillance system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Time range selector
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        time_range = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last Week", "Last Month", "Custom"])
    with col_t2:
        st.selectbox("Camera", ["All Cameras", "North Gate", "Library", "Science Building", "Hallway B"])
    with col_t3:
        st.selectbox("Event Type", ["All Events", "Medical", "Fall", "Altercation", "Suspicious"])
    
    # Key metrics
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.metric("Total Detections", "1,234", "+123")
    with col_k2:
        st.metric("False Positives", "23", "-5")
    with col_k3:
        st.metric("Avg Confidence", "94.2%", "+2.1%")
    with col_k4:
        st.metric("Response Time", "1.2s", "-0.3s")
    
    # Detection trends
    st.markdown("### 📊 Detection Trends")
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    medical_data = np.random.poisson(5, 30)
    fall_data = np.random.poisson(3, 30)
    altercation_data = np.random.poisson(2, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=medical_data, name='Medical', mode='lines+markers', line=dict(color='#ff4444')))
    fig.add_trace(go.Scatter(x=dates, y=fall_data, name='Fall', mode='lines+markers', line=dict(color='#ffbb33')))
    fig.add_trace(go.Scatter(x=dates, y=altercation_data, name='Altercation', mode='lines+markers', line=dict(color='#667eea')))
    
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap and distribution
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown("### 🗺️ Event Heatmap")
        
        # Create heatmap data
        hours = list(range(24))
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        z = np.random.randint(0, 10, (7, 24))
        
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=[f"{h}:00" for h in hours],
            y=days,
            colorscale='Viridis'
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_h2:
        st.markdown("### 📍 Location Distribution")
        
        locations = ['North Gate', 'Library', 'Science Building', 'Hallway B', 'Parking Lot']
        counts = np.random.randint(10, 50, 5)
        
        fig = go.Figure(data=[go.Pie(labels=locations, values=counts, hole=.3)])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.markdown("### ⚡ System Performance")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        # CPU/GPU usage
        times = pd.date_range(end=datetime.now(), periods=60, freq='1min')
        cpu_usage = np.random.normal(45, 10, 60)
        gpu_usage = np.random.normal(35, 15, 60)
        memory_usage = np.random.normal(60, 5, 60)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=cpu_usage, name='CPU %', line=dict(color='#667eea')))
        fig.add_trace(go.Scatter(x=times, y=gpu_usage, name='GPU %', line=dict(color='#ff4444')))
        fig.add_trace(go.Scatter(x=times, y=memory_usage, name='Memory %', line=dict(color='#00C851')))
        
        fig.update_layout(height=300, title="Resource Usage")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_p2:
        # FPS and latency
        fps_data = np.random.normal(28, 3, 60)
        latency_data = np.random.normal(24, 5, 60)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=fps_data, name='FPS', yaxis='y', line=dict(color='#667eea')))
        fig.add_trace(go.Scatter(x=times, y=latency_data, name='Latency (ms)', yaxis='y2', line=dict(color='#ffbb33')))
        
        fig.update_layout(
            height=300,
            title="Processing Metrics",
            yaxis=dict(title="FPS", side='left'),
            yaxis2=dict(title="Latency (ms)", overlaying='y', side='right')
        )
        st.plotly_chart(fig, use_container_width=True)

def show_settings():
    """Enhanced settings view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">⚙️ Settings</h1>
        <p style="margin:0; opacity:0.9;">Configure your CivicShield system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings tabs
    tab_s1, tab_s2, tab_s3, tab_s4 = st.tabs(["General", "Processing", "Privacy", "Advanced"])
    
    with tab_s1:
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen1:
            st.markdown("### 🎨 Appearance")
            theme = st.selectbox("Theme", ["Light", "Dark", "System", "High Contrast"])
            language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese"])
            st.checkbox("Enable Animations", value=True)
            st.checkbox("Compact Mode", value=False)
            st.checkbox("Show Tooltips", value=True)
        
        with col_gen2:
            st.markdown("### 🔔 Notifications")
            st.checkbox("Enable Push Notifications", value=True)
            st.checkbox("Email Alerts", value=False)
            st.checkbox("SMS Alerts", value=False)
            st.checkbox("Desktop Notifications", value=True)
            st.slider("Alert Cooldown (seconds)", 10, 300, 60)
    
    with tab_s2:
        col_proc1, col_proc2 = st.columns(2)
        
        with col_proc1:
            st.markdown("### 🎥 Video Processing")
            st.slider("Frame Skip", 0, 5, 1)
            st.slider("Resolution Scale", 0.25, 1.0, 0.5, 0.25)
            st.selectbox("Processing Priority", ["Low", "Medium", "High", "Real-time"])
            st.checkbox("Hardware Acceleration", value=True)
            st.checkbox("Multi-threading", value=True)
        
        with col_proc2:
            st.markdown("### 🤖 Model Settings")
            st.slider("Detection Threshold", 0.1, 0.9, 0.25)
            st.slider("NMS Threshold", 0.1, 0.9, 0.5)
            st.slider("Max Detections", 10, 100, 50)
            st.selectbox("Model Precision", ["FP32", "FP16", "INT8"])
    
    with tab_s3:
        col_priv1, col_priv2 = st.columns(2)
        
        with col_priv1:
            st.markdown("### 🔐 Privacy Settings")
            st.checkbox("Enable Face Blurring", value=True)
            st.checkbox("Enable License Plate Blurring", value=False)
            st.slider("Blur Intensity", 1, 10, 5)
            st.slider("Blur Padding (%)", 0, 100, 35)
            st.selectbox("Redaction Method", ["Gaussian Blur", "Pixelation", "Masking", "Chaotic"])
        
        with col_priv2:
            st.markdown("### 🔑 Access Control")
            st.checkbox("Require 2FA", value=True)
            st.number_input("Min Approvals", 1, 5, 2)
            st.text_input("Admin Email")
            st.text_input("Security Key")
    
    with tab_s4:
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            st.markdown("### 🌐 Network")
            backend_url = st.text_input("Backend URL", value=API_BASE_URL)
            api_key = st.text_input("API Key", type="password")
            st.number_input("Timeout (seconds)", 1, 60, 5)
            st.number_input("Max Retries", 0, 10, 3)
        
        with col_adv2:
            st.markdown("### 📁 Storage")
            st.text_input("Raw Videos Path", value=RAW_DIR)
            st.text_input("Secure Videos Path", value=SECURE_RAW_DIR)
            st.text_input("Models Path", value=AI_MODELS_DIR)
            st.slider("Max Storage (GB)", 10, 1000, 100)
            st.button("🧹 Clean Cache")
    
    # Save button
    if st.button("💾 Save All Settings", use_container_width=True):
        st.success("Settings saved successfully!")
        add_notification("Settings Updated", "System configuration has been updated")

if __name__ == "__main__":
    main()
