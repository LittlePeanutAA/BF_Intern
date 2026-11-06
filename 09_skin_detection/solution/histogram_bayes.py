"""Mốc so sánh: bộ phân loại histogram màu của Jones & Rehg (2002), tài liệu [8] trong bài báo.

Thay vì đặt ngưỡng bằng tay, đếm trên dữ liệu có nhãn xem mỗi ô màu xuất hiện bao nhiêu lần ở pixel da
và ở pixel nền, rồi phân loại theo tỉ lệ P(màu | da) / P(màu | nền).
"""
import numpy as np


class HistogramBayes:
    def __init__(self, bins: int = 32):
        self.bins = bins
        self.shift = 8 - int(np.log2(bins))  # 256 mức -> `bins` mức bằng dịch bit

    def _index(self, rgb: np.ndarray) -> np.ndarray:
        q = rgb.astype(np.int64) >> self.shift
        return (q[..., 0] * self.bins + q[..., 1]) * self.bins + q[..., 2]

    def fit(self, images: list[np.ndarray], truths: list[np.ndarray]) -> "HistogramBayes":
        n = self.bins ** 3
        skin, other = np.zeros(n), np.zeros(n)
        for image, truth in zip(images, truths):
            idx = self._index(image)
            skin += np.bincount(idx[truth], minlength=n)
            other += np.bincount(idx[~truth], minlength=n)
        # Làm trơn Laplace: ô màu chưa gặp lần nào không bị gán xác suất 0 hay chia cho 0
        self.log_ratio = np.log((skin + 1) / (skin.sum() + n)) - np.log((other + 1) / (other.sum() + n))
        self.threshold = 0.0
        return self

    def score(self, image: np.ndarray) -> np.ndarray:
        return self.log_ratio[self._index(image)]

    def tune_threshold(self, images: list[np.ndarray], truths: list[np.ndarray]) -> float:
        """Chọn ngưỡng cho F1 cao nhất trên dữ liệu train (không bao giờ trên dữ liệu test)."""
        scores = np.concatenate([self.score(im).ravel() for im in images])
        labels = np.concatenate([t.ravel() for t in truths])
        order = np.argsort(-scores, kind="stable")
        tp = np.cumsum(labels[order])
        k = np.arange(1, len(order) + 1)
        f1 = 2 * tp / (k + labels.sum())
        self.threshold = float(scores[order][int(np.argmax(f1))])
        return self.threshold

    def predict(self, image: np.ndarray) -> np.ndarray:
        return self.score(image) >= self.threshold
