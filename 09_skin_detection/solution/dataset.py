"""Đọc bộ dữ liệu Pratheepan đã tải bằng data/download.py."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "data" / "pratheepan"
FOLDERS = {"FacePhoto": "GroundT_FacePhoto", "FamilyPhoto": "GroundT_FamilyPhoto"}

# 6 ảnh trong hình 5 và bảng 1 của bài báo, đúng thứ tự hàng trong bảng.
# Tìm ra bằng cách khớp kích thước ảnh và số pixel da trong ground truth với các cột của bảng.
PAPER_TABLE = [
    # (tên file, tổng pixel, pixel da phát hiện, pixel da trong GT) theo bảng 1
    ("evangeline-lilly-face-wallpapers_1593_1024", 196_608, 54_885, 55_836),
    ("Afishingfamilygettogether", 176_418, 29_828, 23_089),
    ("sri-lankan-actress-Natasha-Perera-", 114_400, 20_497, 21_128),
    ("pg42RF", 108_600, 51_191, 49_420),
    ("w_sexy", 50_000, 19_328, 18_926),
    ("m_unsexy_gr", 128_000, 72_237, 47_359),
]


@dataclass(frozen=True)
class Sample:
    name: str
    group: str          # FacePhoto (1 người, cận mặt) hoặc FamilyPhoto (nhiều người, cảnh rộng)
    image: np.ndarray   # RGB uint8 (H, W, 3)
    truth: np.ndarray   # bool (H, W): True là da

    @property
    def pixels(self) -> int:
        return self.truth.size


def available() -> bool:
    return (ROOT / "Ground_Truth").is_dir()


def load_sample(image_path: Path, group: str) -> Sample:
    mask_path = ROOT / "Ground_Truth" / FOLDERS[group] / f"{image_path.stem}.png"
    image = np.asarray(Image.open(image_path).convert("RGB"))
    # Mask có viền khử răng cưa (giá trị 0..255), nên lấy ngưỡng ở giữa
    truth = np.asarray(Image.open(mask_path).convert("L")) > 127
    return Sample(image_path.stem, group, image, truth)


def load_all() -> list[Sample]:
    if not available():
        raise SystemExit("Chưa có dữ liệu. Chạy: python data/download.py")
    samples = []
    for group in FOLDERS:
        for path in sorted((ROOT / "Pratheepan_Dataset" / group).iterdir()):
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                samples.append(load_sample(path, group))
    return samples
