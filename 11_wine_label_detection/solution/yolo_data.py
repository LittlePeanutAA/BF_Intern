"""Dựng dataset YOLO từ bản ghi trong DB.

    python solution/yolo_data.py --records records.jsonl --images raw/ --out wine_data/
    python solution/yolo_data.py --manifest manifest.jsonl --images raw/ --out wine_data/

`records.jsonl`: mỗi dòng là một ảnh, xuất từ DB, dạng
    {"image": "abc.jpg", "label_rect": {"top": 10, "left": 20, "bottom": 80, "right": 70},
     "variety_rect": {...} hoặc null, "vintage_rect": {...} hoặc null}

Kết quả (dựng trên ổ đĩa cục bộ của máy train, không phải trên Google Drive):
    wine_data/manifest.jsonl          box YOLO + nhóm ảnh trùng + split, dùng chung cho mọi bước
    wine_data/full/                   bước 1: label / variety / vintage trên ảnh gốc
    wine_data/label_crop/             bước 2: variety / vintage trong vùng nhãn đã cắt
"""
import argparse
import json
import shutil
from pathlib import Path

from annotations import SPLITS, assign_split, dhash, rect_to_box
from crops import box_to_crop, crop_rect

FULL_CLASSES = ("label", "variety", "vintage")
CROP_CLASSES = ("variety", "vintage")


def make_manifest(records: list[dict], images_dir: Path) -> list[dict]:
    """Đổi rect sang box YOLO, gom ảnh trùng theo dHash, gán split theo nhóm."""
    rows = []
    for rec in records:
        boxes = {k: rect_to_box(rec.get(f"{k}_rect")) for k in FULL_CLASSES}
        group = dhash(images_dir / rec["image"])
        rows.append({"image": rec["image"], **{f"{k}_box": v for k, v in boxes.items()},
                     "group": group, "split": assign_split(group)})
    return rows


def load_manifest(path: Path) -> list[dict]:
    """Manifest đã có sẵn box YOLO và khoá nhóm (ví dụ do dự án chính dựng). Split được tính lại bằng
    assign_split, để mọi dataset trong bài dùng cùng một quy tắc chia."""
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return [{"image": r["image"], **{f"{k}_box": r.get(f"{k}_box") for k in FULL_CLASSES},
             "group": r["group"], "split": assign_split(r["group"])} for r in rows]


def yolo_line(cls: int, box) -> str:
    return f"{cls} " + " ".join(f"{v:.6f}" for v in box)


def prepare(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for kind in ("images", "labels"):
        for split in SPLITS:
            (root / kind / split).mkdir(parents=True)


def write_data_yaml(root: Path, names: tuple[str, ...]) -> Path:
    # Đường dẫn tuyệt đối để train chạy được từ thư mục nào cũng được
    lines = [f"path: {root.resolve()}", *(f"{s}: images/{s}" for s in SPLITS), "names:"]
    lines += [f"  {i}: {name}" for i, name in enumerate(names)]
    path = root / "data.yaml"
    path.write_text("\n".join(lines) + "\n")
    return path


def write_full_dataset(rows: list[dict], images_dir: Path, root: Path) -> Path:
    prepare(root)
    for row in rows:
        lines = [yolo_line(cls, row[f"{name}_box"]) for cls, name in enumerate(FULL_CLASSES) if row[f"{name}_box"]]
        if not lines:
            continue
        shutil.copy2(images_dir / row["image"], root / "images" / row["split"] / row["image"])
        (root / "labels" / row["split"] / f"{Path(row['image']).stem}.txt").write_text("\n".join(lines) + "\n")
    return write_data_yaml(root, FULL_CLASSES)


def write_crop_dataset(rows: list[dict], images_dir: Path, root: Path, pad: float = 0.02) -> Path:
    """Vùng nhãn đã cắt, variety -> 0, vintage -> 1.

    Bỏ các vùng cắt không có box variety/vintage nào: thiếu box ở đây thường nghĩa là "chưa gán nhãn",
    không phải "nhãn không in chữ đó", nên không dùng làm mẫu âm được.
    """
    from PIL import Image

    prepare(root)
    for row in rows:
        if not row["label_box"]:
            continue
        with Image.open(images_dir / row["image"]) as img:
            img = img.convert("RGB")
            rect = crop_rect(row["label_box"], img.width, img.height, pad)
            lines = []
            for cls, name in enumerate(CROP_CLASSES):
                moved = box_to_crop(row[f"{name}_box"], rect, img.width, img.height) if row[f"{name}_box"] else None
                if moved:
                    lines.append(yolo_line(cls, moved))
            if not lines:
                continue
            stem = Path(row["image"]).stem
            img.crop(rect).save(root / "images" / row["split"] / f"{stem}.jpg", quality=95)
        (root / "labels" / row["split"] / f"{stem}.txt").write_text("\n".join(lines) + "\n")
    return write_data_yaml(root, CROP_CLASSES)


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--records", type=Path, help="bản ghi xuất từ DB, toạ độ theo %%")
    source.add_argument("--manifest", type=Path, help="manifest có sẵn box YOLO và cột group")
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.manifest:
        rows = load_manifest(args.manifest)
    else:
        records = [json.loads(line) for line in args.records.read_text().splitlines() if line.strip()]
        rows = make_manifest(records, args.images)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print({s: sum(r["split"] == s for r in rows) for s in SPLITS})
    print(write_full_dataset(rows, args.images, args.out / "full"))
    print(write_crop_dataset(rows, args.images, args.out / "label_crop"))


if __name__ == "__main__":
    main()
