"""Đo toàn bộ pipeline trên ảnh gốc của tập test: đúng thứ API trả về cho người dùng.

    python solution/eval_pipeline.py --manifest wine_data/manifest.jsonl --images raw/ \
        --stage1 runs/stage1/weights/best.pt --stage2 runs/stage2/weights/best.pt

mAP của từng bước đo trên dataset riêng của bước đó (bước 2 đo trên vùng cắt từ box nhãn THẬT),
nên chưa tính lỗi dây chuyền khi bước 1 cắt nhãn lệch. Script này so box cuối cùng với ground truth
trên ảnh gốc, cho bước 1 đứng riêng và cho cả hai bước.
"""
import argparse
import json
from pathlib import Path

from PIL import Image

from api import TwoStage, YoloDetector

CLASSES = ("label", "variety", "vintage")


def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def to_xyxy(box, w: int, h: int):
    x, y, bw, bh = box
    return (x - bw / 2) * w, (y - bh / 2) * h, (x + bw / 2) * w, (y + bh / 2) * h


def score(predict, rows: list[dict], images: Path, threshold: float = 0.5) -> dict:
    """Mỗi class: chỉ lấy box tin cậy nhất (mỗi nhãn chai có một dòng variety và một dòng vintage).
    TP: có ground truth và box khớp IoU >= threshold. FP: có dự đoán nhưng sai chỗ hoặc ảnh không có GT.
    FN: có GT nhưng không dự đoán hoặc dự đoán sai chỗ."""
    counts = {c: {"tp": 0, "fp": 0, "fn": 0} for c in CLASSES}
    for row in rows:
        with Image.open(images / row["image"]) as img:
            img = img.convert("RGB")
            found = predict(img)
            for cls in CLASSES:
                preds = sorted((d for d in found if d.name == cls), key=lambda d: -d.confidence)
                truth = row[f"{cls}_box"]
                if truth is None:
                    # GT thiếu thường là "chưa gán nhãn", nên dự đoán ở đây không tính là FP
                    continue
                hit = preds and iou(preds[0].xyxy, to_xyxy(truth, img.width, img.height)) >= threshold
                counts[cls]["tp" if hit else "fn"] += 1
                if preds and not hit:
                    counts[cls]["fp"] += 1
    result = {}
    for cls, c in counts.items():
        p = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0
        r = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0
        result[cls] = {**c, "precision": round(p, 3), "recall": round(r, 3)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--stage1", required=True)
    parser.add_argument("--stage2", required=True)
    parser.add_argument("--split", default="test")
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text().splitlines() if line.strip()]
    rows = [r for r in rows if r["split"] == args.split]
    stage1, stage2 = YoloDetector(args.stage1), YoloDetector(args.stage2)
    report = {"images": len(rows),
              "stage1_only": score(TwoStage(stage1), rows, args.images),
              "two_stage": score(TwoStage(stage1, stage2), rows, args.images)}
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
