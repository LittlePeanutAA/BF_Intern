"""Bước 2 của detector hai bước: cắt vùng nhãn, đổi box variety/vintage sang toạ độ của vùng cắt và ngược lại.

Lý do: box nhãn được detect gần như hoàn hảo (mAP50 khoảng 0,99), còn dòng chữ variety thì nhỏ.
Cắt nhãn ra rồi mới detect thì cùng `imgsz` nhưng dòng chữ có nhiều pixel hơn hẳn.
"""
from typing import Optional

from annotations import Box

Rect = tuple[int, int, int, int]  # x1, y1, x2, y2 theo pixel


def crop_rect(label_box: Box, width: int, height: int, pad: float = 0.0) -> Rect:
    """Hình chữ nhật pixel của box nhãn, nới thêm `pad` (tỉ lệ theo kích thước box), không vượt ra ngoài ảnh."""
    x, y, w, h = label_box
    w, h = w * (1 + 2 * pad), h * (1 + 2 * pad)
    x1 = max(0, int(round((x - w / 2) * width)))
    y1 = max(0, int(round((y - h / 2) * height)))
    x2 = min(width, int(round((x + w / 2) * width)))
    y2 = min(height, int(round((y + h / 2) * height)))
    return x1, y1, x2, y2


def box_to_crop(box: Box, rect: Rect, width: int, height: int, min_visible: float = 0.6) -> Optional[Box]:
    """Box trên ảnh gốc -> box trong vùng cắt.

    Box bị cắt gọn theo vùng cắt, và chỉ giữ nếu ít nhất `min_visible` diện tích còn nằm trong.
    Notebook cũ bỏ mọi box chạm mép vùng cắt, nên âm thầm làm mất chữ in sát mép nhãn.
    """
    x1, y1, x2, y2 = rect
    cw, ch = x2 - x1, y2 - y1
    if cw <= 0 or ch <= 0:
        return None
    x, y, w, h = box
    bx1, by1, bx2, by2 = (x - w / 2) * width, (y - h / 2) * height, (x + w / 2) * width, (y + h / 2) * height
    area = (bx2 - bx1) * (by2 - by1)
    if area <= 0:
        return None
    ix1, iy1, ix2, iy2 = max(bx1, x1), max(by1, y1), min(bx2, x2), min(by2, y2)
    if ix2 <= ix1 or iy2 <= iy1 or (ix2 - ix1) * (iy2 - iy1) / area < min_visible:
        return None
    return ((ix1 + ix2) / 2 - x1) / cw, ((iy1 + iy2) / 2 - y1) / ch, (ix2 - ix1) / cw, (iy2 - iy1) / ch


def xyxy_from_crop(xyxy: tuple[float, float, float, float], rect: Rect) -> tuple[float, float, float, float]:
    """Box pixel (x1, y1, x2, y2) trong vùng cắt -> box pixel trên ảnh gốc. Dùng khi suy luận."""
    return xyxy[0] + rect[0], xyxy[1] + rect[1], xyxy[2] + rect[0], xyxy[3] + rect[1]
