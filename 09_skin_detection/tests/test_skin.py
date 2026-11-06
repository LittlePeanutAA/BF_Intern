import colorsys

import numpy as np
import pytest

import dataset
from dataset import PAPER_TABLE
from histogram_bayes import HistogramBayes
from metrics import Confusion
from skin import hsv_rule, kolkur, rgb_rule, rgb_to_hsv, rgb_to_ycbcr, ycbcr_rule


def pixel(r, g, b):
    return np.array([[[r, g, b]]], dtype=np.uint8)


def test_hsv_matches_colorsys():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, (20, 20, 3), dtype=np.uint8)
    h, s, v = rgb_to_hsv(img)
    for (i, j) in [(0, 0), (3, 7), (19, 19), (10, 2)]:
        eh, es, ev = colorsys.rgb_to_hsv(*(img[i, j] / 255))
        assert h[i, j] == pytest.approx(eh * 360) and s[i, j] == pytest.approx(es) and v[i, j] == pytest.approx(ev)


def test_ycbcr_reference_values():
    y, cb, cr = rgb_to_ycbcr(np.array([[[128, 128, 128], [255, 0, 0]]], dtype=np.uint8))
    assert (y[0, 0], cb[0, 0], cr[0, 0]) == pytest.approx((128, 128, 128))  # màu xám: không có sắc độ
    assert (y[0, 1], cb[0, 1], cr[0, 1]) == pytest.approx((76.245, 84.97, 255.5), abs=0.01)


def test_rules_on_typical_colors():
    skin = pixel(224, 172, 140)   # màu da sáng
    assert rgb_rule(skin)[0, 0] and hsv_rule(skin)[0, 0] and ycbcr_rule(skin)[0, 0] and kolkur(skin)[0, 0]
    for other in [(30, 90, 200), (60, 160, 60), (128, 128, 128), (255, 255, 255), (0, 0, 0)]:
        assert not kolkur(pixel(*other))[0, 0], other


def test_or_between_hsv_and_ycbcr():
    # Màu da tối và bão hoà: S = 0.70 > 0.68 nên HSV loại, nhưng vẫn nằm trong vùng YCbCr nên luật đầy đủ chấp nhận
    p = pixel(100, 80, 30)
    assert rgb_rule(p)[0, 0] and not hsv_rule(p)[0, 0] and ycbcr_rule(p)[0, 0] and kolkur(p)[0, 0]


def test_pixelwise_confusion():
    pred = np.array([[1, 1, 0, 0]], dtype=bool)
    truth = np.array([[1, 0, 1, 0]], dtype=bool)
    c = Confusion.pixelwise(pred, truth)
    assert (c.tp, c.fp, c.tn, c.fn) == (1, 1, 1, 1)
    assert c.precision == c.recall == c.f1 == 0.5 and c.iou == pytest.approx(1 / 3)


def test_shifted_mask_same_count_scores_perfect_in_paper_method():
    """Mask dự đoán lệch hoàn toàn khỏi vùng da nhưng cùng diện tích: cách của bài báo vẫn cho 100%."""
    truth = np.zeros((10, 10), dtype=bool)
    truth[:5] = True
    pred = ~truth
    by_count = Confusion.from_counts(int(pred.sum()), int(truth.sum()), truth.size)
    assert by_count.accuracy == 1.0 and by_count.precision == 1.0
    assert Confusion.pixelwise(pred, truth).accuracy == 0.0


@pytest.mark.parametrize("row", range(6))
def test_paper_table_is_count_based(row):
    """Mọi hàng TP/FP/TN/FN của bảng 1 được suy ra đúng từ ba cột đếm (tổng, phát hiện, trong GT)."""
    paper_tp_fp_tn_fn = [(54885, 0, 140772, 951), (23089, 6739, 146590, 0), (20497, 0, 93272, 631),
                         (49420, 1771, 57409, 0), (18926, 402, 30672, 0), (47359, 24878, 55763, 0)]
    _, total, detected, in_truth = PAPER_TABLE[row]
    c = Confusion.from_counts(detected, in_truth, total)
    assert (c.tp, c.fp, c.tn, c.fn) == paper_tp_fp_tn_fn[row]


def test_histogram_bayes_learns_two_colors():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[:, :5] = (220, 170, 140)
    img[:, 5:] = (40, 80, 200)
    truth = np.zeros((10, 10), dtype=bool)
    truth[:, :5] = True
    model = HistogramBayes().fit([img], [truth])
    model.tune_threshold([img], [truth])
    assert (model.predict(img) == truth).all()


@pytest.mark.skipif(not dataset.available(), reason="chưa tải Pratheepan (python data/download.py)")
def test_dataset_matches_paper_images():
    samples = {s.name: s for s in dataset.load_all()}
    assert len(samples) == 78
    for name, total, _, in_truth in PAPER_TABLE[:5]:
        assert samples[name].pixels == total and samples[name].truth.sum() == in_truth
