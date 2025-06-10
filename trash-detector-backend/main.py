# main.py (FastAPI backend)
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import shutil
import uuid
import os
import cv2
import numpy as np

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev (optional)
        "https://trash-detector.vercel.app"  # Replace with your actual frontend URL"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("weights/best.pt")

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    # Save uploaded image
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run detection
    results = model(temp_filename)
    boxes = []
    for r in results:
        for box in r.boxes:
            boxes.append({
                "class": r.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": [float(x) for x in box.xyxy[0]]
            })

    os.remove(temp_filename)

    return { "detections": boxes }
