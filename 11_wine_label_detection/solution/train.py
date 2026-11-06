"""Train một bước của detector, rồi đo đúng một lần trên tập test bằng weights tốt nhất.

    python solution/train.py --config solution/configs/stage1_full.yaml \
        --data wine_data/full/data.yaml --project runs --name stage1_yolov8s
    python solution/train.py --config solution/configs/stage2_label_crop.yaml \
        --data wine_data/label_crop/data.yaml --project runs --name stage2_yolov8s imgsz=800

Cặp `key=value` thêm vào cuối sẽ ghi đè config.
"""
import argparse
from pathlib import Path

import yaml


def parse_override(text: str):
    key, _, value = text.partition("=")
    return key, yaml.safe_load(value)


def main() -> None:
    from ultralytics import YOLO

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--project", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("overrides", nargs="*", type=parse_override)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text()) or {}
    cfg.update(dict(args.overrides))
    model = YOLO(cfg.pop("model"))
    # Truyền thẳng config vào train(**cfg): key sai tên sẽ báo lỗi ngay, không bị bỏ qua trong im lặng
    model.train(data=str(args.data), project=args.project, name=args.name, exist_ok=False, **cfg)

    best = YOLO(Path(model.trainer.save_dir) / "weights" / "best.pt")
    metrics = best.val(data=str(args.data), split="test", imgsz=cfg.get("imgsz", 640),
                       project=args.project, name=f"{args.name}_test")
    # Mảng theo class được đánh chỉ số theo vị trí trong ap_class_index, không phải theo id class
    for j, cls in enumerate(metrics.box.ap_class_index):
        print(f"test {metrics.names[int(cls)]:10s} P={metrics.box.p[j]:.3f} R={metrics.box.r[j]:.3f} "
              f"mAP50={metrics.box.ap50[j]:.3f} mAP50-95={metrics.box.ap[j]:.3f}")


if __name__ == "__main__":
    main()
