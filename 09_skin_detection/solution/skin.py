"""Phát hiện da theo ngưỡng màu của Kolkur et al. (2017), vector hoá bằng numpy.

Mọi hàm nhận ảnh RGB uint8 dạng (H, W, 3) và trả mask bool (H, W).
"""
import numpy as np


def to_float_channels(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rgb = rgb.astype(np.float64)
    return rgb[..., 0], rgb[..., 1], rgb[..., 2]


def rgb_to_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """H tính bằng độ [0, 360), S và V trong [0, 1]: đúng thang đo mà bài báo dùng.

    Chú ý: cv2.cvtColor(..., COLOR_RGB2HSV) với ảnh uint8 trả H trong [0, 180) và S trong [0, 255].
    """
    r, g, b = to_float_channels(rgb)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    delta = mx - mn
    safe = np.where(delta == 0, 1, delta)
    h = np.select(
        [delta == 0, mx == r, mx == g],
        [0.0, ((g - b) / safe) % 6, (b - r) / safe + 2],
        default=(r - g) / safe + 4,
    ) * 60
    s = np.where(mx == 0, 0, delta / np.where(mx == 0, 1, mx))
    return h, s, mx / 255


def rgb_to_ycbcr(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """YCbCr chuẩn ITU-R BT.601 dải đầy đủ (như JPEG và OpenCV), Cb và Cr lệch +128.

    Công thức 4–6 trong bài báo (Y = 0.299R + 0.287G + 0.11B, Cr = R - Y) có lỗi in và không có
    độ lệch 128, nhưng các ngưỡng Cr > 135, Cb > 85 chỉ có nghĩa với dạng chuẩn này.
    """
    r, g, b = to_float_channels(rgb)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    return y, cb, cr


def rgb_rule(rgb: np.ndarray) -> np.ndarray:
    """Luật RGB của Kovač et al. (2003). Điều kiện A > 15 luôn đúng với ảnh không trong suốt nên bỏ."""
    r, g, b = to_float_channels(rgb)
    return (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b) & (np.abs(r - g) > 15)


def hsv_rule(rgb: np.ndarray) -> np.ndarray:
    """Khoảng HSV của Sobottka & Pitas (1996)."""
    h, s, _ = rgb_to_hsv(rgb)
    return (h <= 50) & (s >= 0.23) & (s <= 0.68)


def ycbcr_rule(rgb: np.ndarray) -> np.ndarray:
    """Đa giác trên mặt phẳng Cb–Cr, cộng ngưỡng độ sáng Y > 80."""
    y, cb, cr = rgb_to_ycbcr(rgb)
    return ((cr > 135) & (cb > 85) & (y > 80)
            & (cr <= 1.5862 * cb + 20)
            & (cr >= 0.3448 * cb + 76.2069)
            & (cr >= -4.5652 * cb + 234.5652)
            & (cr <= -1.15 * cb + 301.75)
            & (cr <= -2.2857 * cb + 432.85))


def kolkur(rgb: np.ndarray) -> np.ndarray:
    """Luật đầy đủ của bài báo: RGB VÀ (HSV HOẶC YCbCr)."""
    return rgb_rule(rgb) & (hsv_rule(rgb) | ycbcr_rule(rgb))


RULES = {
    "RGB": rgb_rule,
    "HSV": hsv_rule,
    "YCbCr": ycbcr_rule,
    "RGB & HSV": lambda im: rgb_rule(im) & hsv_rule(im),
    "RGB & YCbCr": lambda im: rgb_rule(im) & ycbcr_rule(im),
    "Kolkur: RGB & (HSV | YCbCr)": kolkur,
}


def apply_mask(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Tô đen pixel không phải da, như hình kết quả trong bài báo."""
    return np.where(mask[..., None], rgb, 0).astype(np.uint8)
