#!/usr/bin/env python3
"""
YOLOv8 Real-Time Object Detection
Optimized for NVIDIA Jetson Thor
"""

import os
import cv2
import yaml
import asyncio
from typing import List, Dict
from pathlib import Path

from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from ultralytics import YOLO
import base64

# Configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Override with environment variables
MODEL_NAME = os.getenv('MODEL_NAME', config['model']['name'])
CONFIDENCE = float(os.getenv('CONFIDENCE', config['model']['confidence']))
VIDEO_SOURCE = os.getenv('VIDEO_SOURCE', config['video']['source'])
USE_TENSORRT = os.getenv('USE_TENSORRT', 'true').lower() == 'true'

# Initialize FastAPI
app = FastAPI(title="Jetson Computer Vision API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load YOLO model
print(f"Loading {MODEL_NAME} model...")
model = YOLO(f'{MODEL_NAME}.pt')

# Export to TensorRT if enabled
if USE_TENSORRT:
    print("Exporting to TensorRT...")
    model.export(format='engine', half=True)
    model = YOLO(f'{MODEL_NAME}.engine')

print("Model loaded successfully!")

# Video capture
cap = None

def get_video_capture():
    """Initialize video capture"""
    global cap
    if cap is None or not cap.isOpened():
        source = VIDEO_SOURCE
        if source.isdigit():
            source = int(source)
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {source}")
        
        # Set resolution
        width, height = map(int, os.getenv('RESOLUTION', '1920x1080').split('x'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, int(os.getenv('FPS', 30)))
    
    return cap

def detect_objects(frame: np.ndarray) -> List[Dict]:
    """Run object detection on frame"""
    results = model(frame, conf=CONFIDENCE, verbose=False)[0]
    
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        
        detections.append({
            'bbox': [x1, y1, x2, y2],
            'confidence': conf,
            'class': results.names[cls],
            'class_id': cls
        })
    
    return detections

def draw_detections(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
    """Draw bounding boxes on frame"""
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        label = f"{det['class']} {det['confidence']:.2f}"
        
        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    return frame

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve web interface"""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "model": MODEL_NAME}

@app.get("/video_feed")
async def video_feed():
    """Stream video with detections"""
    def generate():
        cap = get_video_capture()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = detect_objects(frame)
            
            # Draw detections
            frame = draw_detections(frame, detections)
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return StreamingResponse(generate(), 
                           media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/api/detect")
async def detect_api(file: UploadFile = File(...)):
    """API endpoint for image detection"""
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Detect objects
    detections = detect_objects(frame)
    
    return {
        "detections": detections,
        "count": len(detections),
        "model": MODEL_NAME
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time detections"""
    await websocket.accept()
    cap = get_video_capture()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = detect_objects(frame)
            
            # Send detections
            await websocket.send_json({
                "detections": detections,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")