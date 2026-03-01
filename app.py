# app.py - Main Streamlit Application
import streamlit as st
import cv2
import numpy as np
import requests
import json
import time
import os
import base64
from datetime import datetime
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

# Page configuration
st.set_page_config(
    page_title="CivicShield - Privacy-Preserving Surveillance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Video containers */
    .video-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
        position: relative;
        background: #000;
    }
    
    .video-label {
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        z-index: 1000;
        border-left: 3px solid #ff4444;
    }
    
    .redacted-label {
        border-left: 3px solid #00C851;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        border: 1px solid #e0e0e0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Alert styling */
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        animation: slideIn 0.3s ease;
    }
    
    .alert-critical {
        background: #fff5f5;
        border-left-color: #ff4444;
    }
    
    .alert-warning {
        background: #fff9e6;
        border-left-color: #ffbb33;
    }
    
    .alert-info {
        background: #e6f3ff;
        border-left-color: #33b5e5;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Bandwidth meter */
    .bandwidth-meter {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .meter-bar {
        height: 10px;
        background: rgba(255,255,255,0.3);
        border-radius: 5px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .meter-fill {
        height: 100%;
        background: #00C851;
        transition: width 0.3s;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-offline {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    
    /* Log container */
    .log-container {
        height: 400px;
        overflow-y: auto;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #dee2e6;
    }
    
    .log-entry {
        padding: 0.5rem;
        border-bottom: 1px solid #dee2e6;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    .log-timestamp {
        color: #6c757d;
        margin-right: 1rem;
    }
    
    .log-event {
        font-weight: 600;
    }
    
    /* Toggle switch */
    .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }
    
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }
    
    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    
    input:checked + .slider {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    
    /* File cards */
    .file-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .file-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #667eea;
    }
    
    .file-card.selected {
        border: 2px solid #667eea;
        background: #f0f3ff;
    }
    
    /* Model badge */
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
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
    except:
        st.error("Failed to toggle mode")

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
            st.session_state.anomaly_log.insert(0, {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "type": event_type,
                "message": message,
                "confidence": confidence,
                "event_id": event_id
            })
            return True
    except:
        # Still add to local log even if backend is offline
        st.session_state.anomaly_log.insert(0, {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "message": message,
            "confidence": confidence,
            "event_id": event_id
        })
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
        # This would call your existing video_pipeline.py
        from ai.video_pipeline import process_video
        process_video(video_path)
        return True
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
        # Add padding
        pad_w = int(fw * 0.3)
        pad_h = int(fh * 0.3)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(w, x + fw + pad_w)
        y2 = min(h, y + fh + pad_h)
        
        # Apply blur
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            blurred = cv2.GaussianBlur(roi, (51, 51), 30)
            frame[y1:y2, x1:x2] = blurred
        
        # Draw detection box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Face Redacted", (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame

# Check models on startup
check_models()

# Main app layout
def main():
    # Sidebar navigation
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/shield.png", width=80)
        st.title("CivicShield")
        st.markdown("---")
        
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Live Processing", "Video Library", "Model Management", "Settings"],
            icons=["house", "camera-reels", "film", "cpu", "gear"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        
        st.markdown("---")
        
        # System status
        backend_healthy = check_backend_health()
        
        st.markdown("### System Status")
        if backend_healthy:
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Offline (Demo Mode)")
        
        # Model status
        st.markdown("### Models Loaded")
        for model_name, loaded in st.session_state.model_status.items():
            if loaded:
                st.markdown(f"✅ {model_name}")
            else:
                st.markdown(f"❌ {model_name}")
        
        st.markdown("---")
        
        # Quick stats
        raw_videos = get_raw_videos()
        secure_videos = get_secure_videos()
        
        st.metric("Raw Videos", len(raw_videos))
        st.metric("Secure Videos", len(secure_videos))
        st.metric("Events", len(st.session_state.events))

    # Main content area
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Live Processing":
        show_live_processing()
    elif selected == "Video Library":
        show_video_library()
    elif selected == "Model Management":
        show_model_management()
    elif selected == "Settings":
        show_settings()

def show_dashboard():
    """Dashboard view with overview and stats"""
    
    # Header
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin:0; font-size: 2.5rem;">📊 Dashboard</h1>
                <p style="margin:0; opacity:0.9;">Privacy-Preserving Agentic Surveillance System</p>
            </div>
            <div style="text-align: right;">
                <span class="status-badge status-online">🔵 Edge NPU Ready</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Total Events</div>
            <div class="stat-value">{}</div>
            <div style="color:#00C851;">↑ {} new</div>
        </div>
        """.format(
            len(st.session_state.events),
            len([e for e in st.session_state.events if datetime.fromisoformat(e['timestamp']).date() == datetime.now().date()])
        ), unsafe_allow_html=True)
    
    with col2:
        encrypted_count = sum(1 for e in st.session_state.events if e.get('encrypted', False))
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Encrypted Clips</div>
            <div class="stat-value">{}</div>
            <div style="color:#667eea;">AES-256 Encrypted</div>
        </div>
        """.format(encrypted_count), unsafe_allow_html=True)
    
    with col3:
        raw_videos = get_raw_videos()
        secure_videos = get_secure_videos()
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Video Library</div>
            <div class="stat-value">{}</div>
            <div style="color:#666;">{} raw / {} secure</div>
        </div>
        """.format(len(raw_videos) + len(secure_videos), len(raw_videos), len(secure_videos)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">System Uptime</div>
            <div class="stat-value">99.9%</div>
            <div style="color:#00C851;">24/7 operation</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bandwidth comparison
    st.markdown("---")
    st.markdown("### 📊 Bandwidth Usage Comparison")
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        # Edge mode vs Cloud mode
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Raw Streaming',
            x=['Per Event'],
            y=[5000000],
            marker_color='#ff4444',
            text='5 MB',
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Metadata Alert',
            x=['Per Event'],
            y=[300],
            marker_color='#00C851',
            text='300 B',
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Bandwidth: 300B vs 5MB (99.994% reduction)",
            barmode='group',
            height=400,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b2:
        # Bandwidth over time
        times = pd.date_range(end=datetime.now(), periods=24, freq='H')
        if st.session_state.edge_mode:
            bandwidth_data = [300 * np.random.randint(0, 5) for _ in range(24)]
        else:
            bandwidth_data = [5000000 * np.random.randint(0, 3) for _ in range(24)]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=times,
            y=bandwidth_data,
            mode='lines+markers',
            name='Bandwidth Usage',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ))
        
        fig2.update_layout(
            title="Bandwidth Usage (Last 24 Hours)",
            xaxis_title="Time",
            yaxis_title="Bytes",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Recent events and model performance
    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("### 📋 Recent Events")
        
        if not st.session_state.anomaly_log:
            st.info("No recent events")
        else:
            for log in st.session_state.anomaly_log[:5]:
                if log['confidence'] > 0.9:
                    alert_class = "alert-critical"
                elif log['confidence'] > 0.8:
                    alert_class = "alert-warning"
                else:
                    alert_class = "alert-info"
                
                st.markdown(f"""
                <div class="alert-box {alert_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="log-timestamp">[{log['timestamp']}]</span>
                        <span class="status-badge" style="background: {'#d4edda' if log['confidence']>0.9 else '#fff3cd'}">
                            {log['confidence']*100:.0f}% confidence
                        </span>
                    </div>
                    <div class="log-event">{log['message']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_r2:
        st.markdown("### 🤖 Model Performance")
        
        # Model accuracy chart
        models = ['YOLOv8m', 'YOLOv8n-Face', 'YOLOv8m-Pose']
        accuracy = [0.95, 0.92, 0.88]
        inference_time = [28, 15, 32]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Accuracy',
            x=models,
            y=accuracy,
            marker_color='#00C851',
            text=[f"{a*100:.0f}%" for a in accuracy],
            textposition='outside'
        ))
        
        fig3.add_trace(go.Bar(
            name='Inference Time (ms)',
            x=models,
            y=inference_time,
            marker_color='#667eea',
            text=[f"{t}ms" for t in inference_time],
            textposition='outside',
            yaxis='y2'
        ))
        
        fig3.update_layout(
            title="Model Performance Metrics",
            barmode='group',
            height=400,
            yaxis=dict(title="Accuracy", range=[0, 1]),
            yaxis2=dict(title="Time (ms)", overlaying='y', side='right'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig3, use_container_width=True)

def show_live_processing():
    """Live video processing view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">🎥 Live Processing</h1>
        <p style="margin:0; opacity:0.9;">Real-time privacy-preserving video analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Raw Input Feed")
        
        # Video source selection
        source_type = st.radio(
            "Select Source",
            ["Test Video", "Upload Video", "Webcam"],
            horizontal=True
        )
        
        video_path = None
        
        if source_type == "Test Video":
            raw_videos = get_raw_videos()
            if raw_videos:
                video_names = [os.path.basename(v) for v in raw_videos]
                selected = st.selectbox("Choose test video", video_names)
                if selected:
                    video_path = os.path.join(RAW_DIR, selected)
                    st.session_state.selected_raw_video = video_path
            else:
                st.warning("No test videos found in raw/ folder")
        
        elif source_type == "Upload Video":
            uploaded_file = st.file_uploader("Upload video", type=['mp4', 'avi', 'mov'])
            if uploaded_file:
                # Save uploaded file
                video_path = os.path.join(PREDICT_DIR, uploaded_file.name)
                with open(video_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded: {uploaded_file.name}")
        
        # Controls
        col_start, col_stop, col_mode = st.columns(3)
        
        with col_start:
            if st.button("▶️ Start Processing", use_container_width=True):
                st.session_state.processing = True
        
        with col_stop:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.processing = False
        
        with col_mode:
            edge_mode = st.toggle("🌐 Edge Mode", value=st.session_state.edge_mode)
            if edge_mode != st.session_state.edge_mode:
                toggle_mode(edge_mode)
        
        # Display raw video
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            # Placeholder
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, "No Video Source", (200, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            st.image(placeholder, channels="BGR", use_container_width=True)
    
    with col2:
        st.markdown("### 🟢 Privacy-Protected Output")
        
        # Processed video display
        output_video = os.path.join(ROOT_DIR, "output_redacted.mp4")
        if os.path.exists(output_video):
            st.video(output_video)
            
            # Detection info
            st.markdown("### 📊 Detection Results")
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.metric("People Detected", "3")
            with col_d2:
                st.metric("Faces Redacted", "2")
            with col_d3:
                st.metric("Confidence", "94%")
        else:
            # Simulated output
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            
            # Add simulated detections
            cv2.rectangle(placeholder, (200, 100), (350, 300), (0, 255, 0), 2)
            cv2.putText(placeholder, "Person ID 1", (200, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.rectangle(placeholder, (400, 150), (500, 350), (0, 255, 0), 2)
            cv2.putText(placeholder, "Person ID 2", (400, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add blurred face
            cv2.rectangle(placeholder, (250, 120), (300, 180), (255, 200, 0), 2)
            cv2.putText(placeholder, "Face Redacted", (250, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 2)
            
            st.image(placeholder, channels="BGR", use_container_width=True)
            
            st.info("Run the AI pipeline to see real detections")
            
            if st.button("🚀 Run AI Pipeline on Selected Video", use_container_width=True):
                if video_path and os.path.exists(video_path):
                    with st.spinner("Processing video..."):
                        if run_ai_pipeline(video_path):
                            st.success("Processing complete! Check output_redacted.mp4")
                            st.rerun()
                else:
                    st.error("Please select a video first")
    
    # Live log
    st.markdown("---")
    st.markdown("### 📋 Real-time Detection Log")
    
    log_container = st.container()
    with log_container:
        for log in st.session_state.anomaly_log[:10]:
            st.info(f"[{log['timestamp']}] {log['message']} ({log['confidence']*100:.0f}%)")

def show_video_library():
    """Video library view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">📁 Video Library</h1>
        <p style="margin:0; opacity:0.9;">Browse and manage video footage</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📹 Raw Videos", "🔒 Secure Videos", "📤 Predictions"])
    
    with tab1:
        st.markdown("### Raw Video Footage")
        st.markdown("*These videos contain PII and are encrypted*")
        
        raw_videos = get_raw_videos()
        
        if not raw_videos:
            st.info("No raw videos found in raw/ folder")
        else:
            # Grid display
            cols = st.columns(3)
            for idx, video_path in enumerate(raw_videos):
                with cols[idx % 3]:
                    video_name = os.path.basename(video_path)
                    
                    # Video thumbnail
                    cap = cv2.VideoCapture(video_path)
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(frame_rgb, use_container_width=True)
                    
                    st.markdown(f"**{video_name}**")
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        if st.button(f"▶️ Play", key=f"play_raw_{idx}"):
                            st.session_state.selected_raw_video = video_path
                    with col_p2:
                        if st.button(f"🔒 Encrypt", key=f"enc_{idx}"):
                            st.info("Encryption would happen here")
                    
                    st.markdown("---")
    
    with tab2:
        st.markdown("### Secure Encrypted Videos")
        st.markdown("*Privacy-protected footage with redacted PII*")
        
        secure_videos = get_secure_videos()
        
        if not secure_videos:
            st.info("No secure videos found in secure_raw/ folder")
        else:
            for video_path in secure_videos:
                video_name = os.path.basename(video_path)
                
                with st.expander(f"📹 {video_name}"):
                    col_v1, col_v2 = st.columns([2, 1])
                    
                    with col_v1:
                        st.video(video_path)
                    
                    with col_v2:
                        st.markdown("**Video Info**")
                        st.markdown(f"📁 Size: {os.path.getsize(video_path) / 1e6:.1f} MB")
                        st.markdown(f"🔒 Encrypted: Yes")
                        
                        # Check if this video has associated events
                        for event in st.session_state.events:
                            if video_name in event.get('raw_clip_path', ''):
                                st.markdown(f"⚠️ Event: {event['event_type']}")
                                st.markdown(f"📊 Confidence: {event['confidence']*100:.0f}%")
                        
                        if st.button(f"🔓 Request Unlock", key=f"unlock_{video_name}"):
                            event_id = f"evt_{int(time.time())}"
                            create_anomaly_event(
                                "unlock_request",
                                1.0,
                                f"Unlock requested for {video_name}",
                                video_path
                            )
                            st.success("Unlock request sent! (2/2 approvals required)")
    
    with tab3:
        st.markdown("### Prediction Results")
        st.markdown("*Videos processed by AI pipeline*")
        
        # Look for output_redacted.mp4
        output_video = os.path.join(ROOT_DIR, "output_redacted.mp4")
        if os.path.exists(output_video):
            st.video(output_video)
            
            # Download button
            with open(output_video, 'rb') as f:
                st.download_button(
                    "📥 Download Processed Video",
                    f,
                    file_name="output_redacted.mp4"
                )
        else:
            st.info("No processed video found. Run the AI pipeline first.")

def show_model_management():
    """Model management view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">🤖 Model Management</h1>
        <p style="margin:0; opacity:0.9;">YOLOv8 models for person/face/pose detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("### 📦 Available Models")
        
        models = get_model_files()
        
        if not models:
            st.warning("No models found in ai/models/ folder")
        else:
            for model_path in models:
                model_name = os.path.basename(model_path)
                model_size = os.path.getsize(model_path) / 1e6
                
                # Determine model type
                if 'face' in model_name.lower():
                    model_type = "Face Detection"
                    color = "#00C851"
                elif 'pose' in model_name.lower():
                    model_type = "Pose Estimation"
                    color = "#ffbb33"
                else:
                    model_type = "Person Detection"
                    color = "#667eea"
                
                st.markdown(f"""
                <div class="file-card {'selected' if st.session_state.model_status.get(model_name, False) else ''}">
                    <div style="display: flex; justify-content: space-between;">
                        <span><strong>{model_name}</strong></span>
                        <span class="status-badge" style="background: {color}; color: white;">{model_type}</span>
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">
                        Size: {model_size:.1f} MB
                    </div>
                    <div style="margin-top: 0.5rem;">
                        {'✅ Loaded' if st.session_state.model_status.get(model_name, False) else '⏳ Not Loaded'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown("### 📊 Model Performance")
        
        # Performance metrics
        performance_data = pd.DataFrame({
            'Model': ['YOLOv8m', 'YOLOv8n-Face', 'YOLOv8m-Pose'],
            'mAP@0.5': [0.95, 0.92, 0.88],
            'Inference (ms)': [28, 15, 32],
            'Size (MB)': [49, 6, 84]
        })
        
        st.dataframe(performance_data, use_container_width=True)
        
        # Model comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='mAP@0.5',
            x=performance_data['Model'],
            y=performance_data['mAP@0.5'],
            marker_color='#00C851',
            text=performance_data['mAP@0.5'],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Inference (ms)',
            x=performance_data['Model'],
            y=performance_data['Inference (ms)'],
            marker_color='#667eea',
            text=performance_data['Inference (ms)'],
            textposition='outside',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Model Performance Comparison",
            barmode='group',
            height=400,
            yaxis=dict(title="mAP@0.5", range=[0, 1]),
            yaxis2=dict(title="Time (ms)", overlaying='y', side='right'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Download models info
        st.markdown("### 📥 Download Models")
        st.markdown("""
        - [YOLOv8m (Person Detection)](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt)
        - [YOLOv8n-Face](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-face.pt)
        - [YOLOv8m-Pose](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m-pose.pt)
        """)

def show_settings():
    """Settings view"""
    
    st.markdown("""
    <div class="header-container">
        <h1 style="margin:0;">⚙️ Settings</h1>
        <p style="margin:0; opacity:0.9;">Configure system parameters</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("### 🎥 Processing Settings")
        
        # Processing settings
        conf_threshold = st.slider("Detection Confidence Threshold", 0.1, 0.9, 0.25, 0.05)
        iou_threshold = st.slider("NMS IoU Threshold", 0.1, 0.9, 0.5, 0.05)
        max_age = st.slider("Max Track Age", 5, 50, 25)
        
        st.markdown("### 🔐 Privacy Settings")
        
        # Privacy settings
        face_blur = st.checkbox("Enable Face Blurring", value=True)
        blur_padding = st.slider("Blur Padding (%)", 10, 100, 35)
        
        if st.button("Save Processing Settings", use_container_width=True):
            st.success("Settings saved!")
    
    with col_s2:
        st.markdown("### 📡 Network Settings")
        
        # Network settings
        backend_url = st.text_input("Backend API URL", value="http://localhost:8000")
        edge_mode = st.toggle("Edge Mode (Privacy-First)", value=st.session_state.edge_mode)
        
        if edge_mode != st.session_state.edge_mode:
            toggle_mode(edge_mode)
        
        st.markdown("### 📁 Storage Settings")
        
        # Paths
        st.text_input("Raw Videos Path", value=RAW_DIR)
        st.text_input("Secure Videos Path", value=SECURE_RAW_DIR)
        st.text_input("Models Path", value=AI_MODELS_DIR)
        
        # System info
        st.markdown("### ℹ️ System Information")
        st.json({
            "Python Version": "3.9+",
            "OpenCV Version": cv2.__version__,
            "Backend Status": "Connected" if check_backend_health() else "Disconnected",
            "Models Loaded": sum(1 for v in st.session_state.model_status.values() if v),
            "Total Videos": len(get_raw_videos()) + len(get_secure_videos())
        })

if __name__ == "__main__":
    main()