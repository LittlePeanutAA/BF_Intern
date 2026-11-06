"""API detect nhãn rượu hai bước.

    STAGE1_WEIGHTS=runs/stage1/weights/best.pt STAGE2_WEIGHTS=runs/stage2/weights/best.pt \
        uvicorn api:app --app-dir solution --port 8000
    curl -F image=@chai.jpg localhost:8000/predict

Bước 1 tìm nhãn (và variety/vintage nếu có) trên ảnh gốc. Nếu có model bước 2, cắt nhãn tốt nhất ra,
detect variety/vintage trong đó và đổi toạ độ về ảnh gốc. Mọi box trả về theo pixel của ảnh gốc.
"""
import io
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from crops import crop_rect, xyxy_from_crop

MAX_UPLOAD = 10 * 1024 * 1024


@dataclass(frozen=True)
class Detection:
    name: str
    confidence: float
    xyxy: tuple[float, float, float, float]


class Detector(Protocol):
    def __call__(self, image: Image.Image) -> list[Detection]: ...


class YoloDetector:
    def __init__(self, weights: str, conf: float = 0.25):
        from ultralytics import YOLO

        self.model, self.conf = YOLO(weights), conf

    def __call__(self, image: Image.Image) -> list[Detection]:
        result = self.model.predict(image, conf=self.conf, verbose=False)[0]
        return [Detection(result.names[int(c)], float(p), tuple(map(float, b)))
                for b, p, c in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist(), result.boxes.cls.tolist())]


@dataclass
class TwoStage:
    stage1: Detector
    stage2: Detector | None = None
    pad: float = 0.02

    def __call__(self, image: Image.Image) -> list[Detection]:
        found = self.stage1(image)
        labels = [d for d in found if d.name == "label"]
        if self.stage2 is None or not labels:
            return found
        label = max(labels, key=lambda d: d.confidence)
        x1, y1, x2, y2 = label.xyxy
        w, h = image.width, image.height
        box = ((x1 + x2) / 2 / w, (y1 + y2) / 2 / h, (x2 - x1) / w, (y2 - y1) / h)
        rect = crop_rect(box, w, h, self.pad)
        inside = [Detection(d.name, d.confidence, xyxy_from_crop(d.xyxy, rect)) for d in self.stage2(image.crop(rect))]
        # Bước 2 thay kết quả variety/vintage của bước 1, vì trên vùng cắt chữ có nhiều pixel hơn
        return [label, *inside]


@lru_cache
def get_detector() -> Detector:
    stage1 = os.environ.get("STAGE1_WEIGHTS")
    if not stage1:
        raise RuntimeError("Cần biến môi trường STAGE1_WEIGHTS")
    stage2 = os.environ.get("STAGE2_WEIGHTS")
    return TwoStage(YoloDetector(stage1), YoloDetector(stage2) if stage2 else None)


app = FastAPI(title="Wine label detection")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict")
async def predict(image: UploadFile = File(...), detector: Detector = Depends(get_detector)) -> dict:
    data = await image.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "Ảnh lớn hơn 10 MB")
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(400, "File không phải ảnh") from None
    detections = detector(img)
    return {"width": img.width, "height": img.height,
            "detections": [{"class": d.name, "confidence": round(d.confidence, 4),
                            "bbox_xyxy": [round(v, 1) for v in d.xyxy]} for d in detections]}
