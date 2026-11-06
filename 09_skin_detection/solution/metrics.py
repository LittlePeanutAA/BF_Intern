"""Đo chất lượng mask: so từng pixel với ground truth, và cách tính "theo số lượng" mà bảng 1 của bài báo dùng."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @classmethod
    def pixelwise(cls, pred: np.ndarray, truth: np.ndarray) -> "Confusion":
        """Cách đúng: một pixel là TP khi dự đoán là da VÀ ground truth cũng là da tại chính vị trí đó."""
        pred, truth = pred.astype(bool), truth.astype(bool)
        return cls(tp=int((pred & truth).sum()), fp=int((pred & ~truth).sum()),
                   tn=int((~pred & ~truth).sum()), fn=int((~pred & truth).sum()))

    @classmethod
    def from_counts(cls, detected: int, in_truth: int, total: int) -> "Confusion":
        """Cách bảng 1 của bài báo tính: chỉ so SỐ LƯỢNG pixel da, không quan tâm vị trí.

        Mọi hàng trong bảng 1 thoả đúng các công thức này (TP = min, FP hoặc FN = phần chênh lệch),
        tức là các con số ở đó chỉ đo "đoán đúng diện tích da", không đo "đoán đúng chỗ".
        """
        tp = min(detected, in_truth)
        return cls(tp=tp, fp=detected - tp, fn=in_truth - tp, tn=min(total - detected, total - in_truth))

    def __add__(self, other: "Confusion") -> "Confusion":
        return Confusion(self.tp + other.tp, self.fp + other.fp, self.tn + other.tn, self.fn + other.fn)

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    @property
    def iou(self) -> float:
        denom = self.tp + self.fp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    def as_dict(self) -> dict:
        return {"TP": self.tp, "FP": self.fp, "TN": self.tn, "FN": self.fn,
                "precision": self.precision, "recall": self.recall, "F1": self.f1,
                "IoU": self.iou, "accuracy": self.accuracy}
