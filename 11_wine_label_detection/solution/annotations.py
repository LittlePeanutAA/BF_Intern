"""Đổi toạ độ trong DB sang box YOLO, và chia train/val/test theo nhóm ảnh trùng."""
import hashlib
from pathlib import Path
from typing import Optional

Box = tuple[float, float, float, float]  # x_center, y_center, width, height, đều trong [0, 1]
SPLITS = ("train", "val", "test")


def rect_to_box(rect: Optional[dict]) -> Optional[Box]:
    """``{top, right, bottom, left}`` theo % ảnh (dạng lưu trong DB) -> box YOLO, cắt gọn trong ảnh.

    Trả None nếu thiếu, hỏng, hoặc box có diện tích 0. Trái/phải bị đảo thì tự sắp lại.
    """
    if not rect:
        return None
    try:
        left, right = sorted((float(rect["left"]), float(rect["right"])))
        top, bottom = sorted((float(rect["top"]), float(rect["bottom"])))
    except (KeyError, TypeError, ValueError):
        return None
    left, top = max(left, 0.0) / 100, max(top, 0.0) / 100
    right, bottom = min(right, 100.0) / 100, min(bottom, 100.0) / 100
    if right - left <= 0 or bottom - top <= 0:
        return None
    return ((left + right) / 2, (top + bottom) / 2, right - left, bottom - top)


def dhash(image_path: Path | str, size: int = 8) -> str:
    """Difference hash 64 bit: giống nhau với cùng một ảnh bị upload lại hoặc nén lại dưới tên khác."""
    from PIL import Image

    with Image.open(image_path) as img:
        gray = img.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
        px = list(gray.tobytes())
    bits = 0
    for row in range(size):
        for col in range(size):
            bits = (bits << 1) | (px[row * (size + 1) + col] > px[row * (size + 1) + col + 1])
    return f"{bits:0{size * size // 4}x}"


def assign_split(group: str, ratios: tuple[float, float, float] = (0.7, 0.15, 0.15), salt: str = "wine") -> str:
    """Split là hàm thuần của khoá nhóm: chạy lại bao nhiêu lần, hay dựng thêm dataset crop từ đó,
    một ảnh (và mọi bản trùng của nó) vẫn luôn ở cùng một tập. Không dùng random.shuffle.
    """
    if abs(sum(ratios) - 1) > 1e-6:
        raise ValueError(f"tổng tỉ lệ phải bằng 1, nhận {ratios}")
    u = int.from_bytes(hashlib.sha1(f"{salt}:{group}".encode()).digest()[:8], "big") / 2**64
    if u < ratios[0]:
        return "train"
    return "val" if u < ratios[0] + ratios[1] else "test"
