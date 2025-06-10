from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()

# Allow Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev. Restrict in prod.
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("weights/best.pt")

@app.post("/detect/")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    results = model(image)
    result = results[0]

    detections = []
    for box in result.boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        detections.append({
            "class": result.names[int(cls)],
            "confidence": round(conf, 2),
            "box": [x1, y1, x2, y2]
        })

    return {"detections": detections}
