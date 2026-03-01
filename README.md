# CivicShield : Privacy‑Preserving Agentic Surveillance & Anomaly Router

A decentralized, edge-native surveillance architecture that replaces continuous video streaming with intelligent, privacy-first anomaly routing.

---

## Overview

Modern surveillance systems continuously stream raw video to centralized servers, creating severe privacy, security, and bandwidth challenges. This project redesigns surveillance architecture by shifting intelligence to the edge and transmitting only semantic alerts instead of raw footage.

The system performs:

• Real-time human detection  
• Instant face and identity redaction  
• Multimodal contextual reasoning  
• Anomaly detection  
• Text-based alert routing  
• Secure event logging  

The core principle:

> **We do not stream video. We route intelligence.**

---

## Problem Statement

Traditional surveillance systems suffer from:

- Continuous transmission of raw biometric data
- High bandwidth and storage costs
- Increased cybersecurity attack surface
- Regulatory compliance risks
- Context-blind motion-based detection

This project solves the conflict between surveillance capability and privacy preservation.

---

## System Architecture

Camera Feed  
↓  
Edge Device Processing  
↓  
Real-Time Redaction  
↓  
Vision-Language Semantic Reasoning  
↓  
Anomaly Detection  
↓  
Text-Based Alert Generation  
↓  
Central Dashboard  

No raw video leaves the device during normal operation.

---

## Key Features

### 1. Edge-Native Processing
All detection and reasoning occur locally on the edge device.

### 2. Real-Time Redaction
Faces and human identities are blurred before storage or transmission.

### 3. Vision-Language Understanding
A lightweight Vision-Language Model interprets scene context.

### 4. Semantic Anomaly Routing
Only structured text alerts are transmitted.

### 5. Bandwidth Efficiency
Reduces transmission from megabytes/sec to a few hundred bytes/event.

### 6. Secure Backend
- Event logging
- File encryption
- Dual-approval unlock system
- Bandwidth simulation mode

---

## Technology Stack

- Python
- OpenCV
- GStreamer
- YOLOv8 (INT8 optimized)
- Vision-Language Model (Gemma-class)
- Ryzen AI 1.7 Runtime
- AMD Quark Optimization
- FastAPI
- SQLite
- AES/Fernet Encryption

---

## Project Structure


---

## How It Works

1. The camera feed enters the edge pipeline.
2. YOLO detects humans and faces.
3. Faces are blurred immediately.
4. The Vision-Language layer interprets scene context.
5. If an anomaly is detected:
   - A short text alert is generated.
   - Metadata is sent to backend.
6. Backend:
   - Logs event
   - Encrypts associated clip
   - Stores metadata in SQLite

---

## Running the Backend

### Windows / macOS / Linux

### 1. Install dependencies
`
pip install fastapi uvicorn sqlalchemy cryptography
`

### 2. Navigate to project root
`
cd project-root
`


### 3. Start server
`
uvicorn backend.main:app --reload
`

Open:
`
http://127.0.0.1:8000/docs
`

---

## Running the AI Edge Pipeline

### Install dependencies
`
pip install ultralytics opencv-python numpy
`

### Run
`
python -m ai.video_pipeline
`

Press `Q` to exit.

---

## API Endpoints

### POST /event
Stores anomaly event and encrypts clip.

### GET /events
Returns all logged events.

### POST /request-unlock
Requires dual approval to decrypt clip.

### GET /unlock-status/{event_id}
Returns encryption status.

### GET /mode
Returns edge/cloud mode and bandwidth usage.

---

## Security Design

- Raw video never transmitted by default
- Clips encrypted using Fernet (AES)
- Dual approval required for decryption
- Metadata-only central logging
- Edge mode reduces network exposure

---

## Scalability

Each edge node operates independently.

Central dashboard aggregates only metadata.

This enables:

- Campus-scale deployment
- Smart city expansion
- Industrial monitoring
- Low-connectivity environments

---

## Prototype Demonstration

The demo includes:

- Split-screen view (raw vs redacted)
- Real-time anomaly log
- Bandwidth comparison simulation
- Secure clip storage

---

## Impact

This architecture:

- Protects biometric identity
- Reduces cloud dependency
- Cuts bandwidth costs drastically
- Improves anomaly detection accuracy
- Aligns with modern privacy regulations
- Demonstrates responsible AI deployment

---

## Future Improvements

- Full Gemma VLM integration on NPU
- INT8 quantization for all models
- Hardware UART alarm integration
- Distributed multi-node deployment
- Web-based monitoring dashboard

---

## License

For academic and prototype demonstration purposes.

---

## Core Philosophy

Traditional systems stream everything.

This system streams only meaning.

Privacy and intelligence are no longer mutually exclusive.
