"""Đánh giá luật của bài báo trên toàn bộ Pratheepan và so với bảng 1 của bài báo.

    python data/download.py
    python solution/evaluate.py      # in kết quả, ghi results/*.csv và figures/*.png
"""
import csv
import time
from pathlib import Path

import matplotlib
import numpy as np

from dataset import PAPER_TABLE, Sample, load_all
from histogram_bayes import HistogramBayes
from metrics import Confusion
from skin import RULES, apply_mask, kolkur, rgb_to_ycbcr

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
FIG, RES = HERE / "figures", HERE / "results"
SEED = 0


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(row: dict) -> dict:
    return {k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()}


def check_paper_table(by_name: dict[str, Sample]) -> list[dict]:
    """Câu 2: chạy lại đúng 6 ảnh của bảng 1, đo theo cả hai cách."""
    print("== Bảng 1 của bài báo, tính lại")
    print(f"{'ảnh':<5}{'pixel da (bài báo)':>20}{'(chúng tôi)':>13}"
          f"{'acc bài báo':>13}{'acc từng pixel':>16}{'precision':>11}{'recall':>8}")
    rows = []
    for i, (name, total, detected, in_truth) in enumerate(PAPER_TABLE, 1):
        sample = by_name[name]
        assert sample.pixels == total
        pred = kolkur(sample.image)
        paper = Confusion.from_counts(detected, in_truth, total)
        ours = Confusion.pixelwise(pred, sample.truth)
        print(f"{i:<5}{detected:>20,}{int(pred.sum()):>13,}"
              f"{100 * paper.accuracy:>12.1f}%{100 * ours.accuracy:>15.1f}%"
              f"{100 * ours.precision:>10.1f}%{100 * ours.recall:>7.1f}%")
        rows.append(fmt({"row": i, "image": name, "paper_detected": detected, "our_detected": int(pred.sum()),
                         "gt_skin_paper": in_truth, "gt_skin_ours": int(sample.truth.sum()),
                         "paper_accuracy": paper.accuracy, **{f"ours_{k}": v for k, v in ours.as_dict().items()}}))
    return rows


def evaluate_rules(samples: list[Sample]) -> tuple[list[dict], dict[str, list[float]]]:
    """Câu 4: mọi luật trên toàn bộ 78 ảnh. Cộng dồn confusion của mọi pixel (micro-average)."""
    rows, per_image_f1 = [], {}
    for name, rule in RULES.items():
        totals = {"all": Confusion(0, 0, 0, 0), "FacePhoto": Confusion(0, 0, 0, 0),
                  "FamilyPhoto": Confusion(0, 0, 0, 0)}
        f1s = []
        for s in samples:
            c = Confusion.pixelwise(rule(s.image), s.truth)
            totals["all"] += c
            totals[s.group] += c
            f1s.append(c.f1)
        per_image_f1[name] = f1s
        for group, c in totals.items():
            rows.append(fmt({"method": name, "subset": group, **c.as_dict()}))
    return rows, per_image_f1


def cross_validate_histogram(samples: list[Sample], folds: int = 5) -> tuple[list[np.ndarray], list[float]]:
    """Mốc học từ dữ liệu, chia theo ẢNH (không theo pixel) để ảnh test hoàn toàn chưa thấy khi train."""
    order = np.random.default_rng(SEED).permutation(len(samples))
    preds: list[np.ndarray] = [None] * len(samples)  # type: ignore[list-item]
    thresholds = []
    for k in range(folds):
        test = set(order[k::folds].tolist())
        train = [samples[i] for i in range(len(samples)) if i not in test]
        model = HistogramBayes().fit([s.image for s in train], [s.truth for s in train])
        thresholds.append(model.tune_threshold([s.image for s in train], [s.truth for s in train]))
        for i in test:
            preds[i] = model.predict(samples[i].image)
    return preds, thresholds


def figure_examples(samples: list[Sample], preds: dict[str, list[np.ndarray]], picks: list[int]) -> None:
    cols = ["Ảnh gốc", "Ground truth", *preds]
    fig, axes = plt.subplots(len(picks), len(cols), figsize=(3 * len(cols), 2.6 * len(picks)))
    for r, i in enumerate(picks):
        s = samples[i]
        panels = [s.image, s.truth, *(apply_mask(s.image, p[i]) for p in preds.values())]
        for c, (title, img) in enumerate(zip(cols, panels)):
            ax = axes[r, c]
            ax.imshow(img, cmap="gray" if img.ndim == 2 else None)
            ax.set_xticks([]), ax.set_yticks([])
            if r == 0:
                ax.set_title(title, fontsize=10)
            if c >= 2:
                f1 = Confusion.pixelwise(list(preds.values())[c - 2][i], s.truth).f1
                ax.set_xlabel(f"F1 = {f1:.2f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "examples.png", dpi=90)
    plt.close(fig)


def figure_cbcr(samples: list[Sample]) -> None:
    """Mật độ pixel da / nền trên mặt phẳng Cb–Cr, kèm vùng đa giác mà luật YCbCr chấp nhận."""
    hists = {"Pixel da": np.zeros((100, 100)), "Pixel nền": np.zeros((100, 100))}
    edges = np.arange(60, 161), np.arange(100, 201)
    for s in samples:
        _, cb, cr = rgb_to_ycbcr(s.image)
        for key, sel in zip(hists, (s.truth, ~s.truth)):
            hists[key] += np.histogram2d(cb[sel], cr[sel], bins=edges)[0]
    cb_grid, cr_grid = np.meshgrid(np.arange(60, 160) + 0.5, np.arange(100, 200) + 0.5)
    polygon = ((cr_grid > 135) & (cb_grid > 85)
               & (cr_grid <= 1.5862 * cb_grid + 20) & (cr_grid >= 0.3448 * cb_grid + 76.2069)
               & (cr_grid >= -4.5652 * cb_grid + 234.5652) & (cr_grid <= -1.15 * cb_grid + 301.75)
               & (cr_grid <= -2.2857 * cb_grid + 432.85))
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharex=True, sharey=True)
    for ax, (title, h) in zip(axes, hists.items()):
        inside = h.T[polygon].sum() / h.sum()
        ax.imshow(np.log1p(h.T), origin="lower", extent=(60, 160, 100, 200), cmap="magma", aspect="auto")
        ax.contour(cb_grid, cr_grid, polygon, levels=[0.5], colors="cyan", linewidths=1.5)
        ax.set(title=f"{title}: {100 * inside:.0f}% nằm trong vùng", xlabel="Cb")
    axes[0].set_ylabel("Cr")
    fig.suptitle("Vùng YCbCr của bài báo (viền xanh) trên toàn bộ pixel Pratheepan, thang màu log")
    fig.tight_layout()
    fig.savefig(FIG / "cbcr_plane.png", dpi=100)
    plt.close(fig)


def figure_f1_distribution(f1: list[float], hist_f1: list[float], paper_idx: list[int]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.linspace(0, 1, 21)
    ax.hist(f1, bins=bins, alpha=0.6, label="Luật Kolkur")
    ax.hist(hist_f1, bins=bins, alpha=0.6, label="Histogram Bayes (CV)")
    for j, i in enumerate(paper_idx):
        ax.axvline(f1[i], color="crimson", lw=1.2, ls="--", label="6 ảnh trong bài báo" if j == 0 else None)
    ax.set(title="F1 từng ảnh trên 78 ảnh Pratheepan", xlabel="F1 của ảnh", ylabel="số ảnh")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "f1_per_image.png", dpi=100)
    plt.close(fig)


def main() -> None:
    FIG.mkdir(exist_ok=True)
    RES.mkdir(exist_ok=True)
    samples = load_all()
    by_name = {s.name: s for s in samples}
    print(f"{len(samples)} ảnh, {sum(s.pixels for s in samples) / 1e6:.1f} triệu pixel, "
          f"{100 * sum(s.truth.sum() for s in samples) / sum(s.pixels for s in samples):.1f}% là da\n")

    write_csv(RES / "paper_table.csv", check_paper_table(by_name))

    start = time.perf_counter()
    for s in samples:
        kolkur(s.image)
    elapsed = time.perf_counter() - start
    print(f"\nTốc độ (numpy): {elapsed / sum(s.pixels for s in samples) * 1e6 * 1e3:.1f} ms cho mỗi megapixel")

    rule_rows, rule_f1 = evaluate_rules(samples)
    hist_preds, thresholds = cross_validate_histogram(samples)
    hist_rows, hist_f1 = [], []
    totals = {"all": Confusion(0, 0, 0, 0), "FacePhoto": Confusion(0, 0, 0, 0), "FamilyPhoto": Confusion(0, 0, 0, 0)}
    for s, p in zip(samples, hist_preds):
        c = Confusion.pixelwise(p, s.truth)
        totals["all"] += c
        totals[s.group] += c
        hist_f1.append(c.f1)
    for group, c in totals.items():
        hist_rows.append(fmt({"method": "Histogram Bayes (5-fold CV theo ảnh)", "subset": group, **c.as_dict()}))
    rows = rule_rows + hist_rows
    write_csv(RES / "all_images.csv", rows)

    print("\n== Toàn bộ 78 ảnh, cộng dồn mọi pixel")
    print(f"{'phương pháp':<40}{'precision':>10}{'recall':>8}{'F1':>7}{'IoU':>7}{'accuracy':>10}")
    for r in rows:
        if r["subset"] == "all":
            print(f"{r['method']:<40}{r['precision']:>10.3f}{r['recall']:>8.3f}{r['F1']:>7.3f}"
                  f"{r['IoU']:>7.3f}{r['accuracy']:>10.3f}")
    print("\n== Theo nhóm ảnh (F1)")
    for method in ["Kolkur: RGB & (HSV | YCbCr)", "Histogram Bayes (5-fold CV theo ảnh)"]:
        f1 = {r["subset"]: r["F1"] for r in rows if r["method"] == method}
        print(f"{method:<40} FacePhoto {f1['FacePhoto']:.3f}   FamilyPhoto {f1['FamilyPhoto']:.3f}")
    print(f"Ngưỡng log-ratio chọn trên từng fold: {np.round(thresholds, 2).tolist()}")

    kf1 = rule_f1["Kolkur: RGB & (HSV | YCbCr)"]
    names = [s.name for s in samples]
    paper_idx = [names.index(n) for n, *_ in PAPER_TABLE]
    rank = np.argsort(np.argsort(-np.array(kf1)))
    print("\n== 6 ảnh của bài báo đứng thứ mấy trong 78 ảnh (xếp theo F1 của luật Kolkur, 1 = tốt nhất)")
    print(sorted(int(rank[i]) + 1 for i in paper_idx), f"; F1 trung vị của 78 ảnh: {np.median(kf1):.3f}",
          f"; của 6 ảnh: {np.median([kf1[i] for i in paper_idx]):.3f}")
    write_csv(RES / "per_image.csv", [fmt({"image": s.name, "group": s.group, "kolkur_F1": kf1[i],
                                           "histogram_F1": hist_f1[i], "in_paper": i in paper_idx})
                                      for i, s in enumerate(samples)])

    order = np.argsort(kf1)
    picks = [paper_idx[0], int(order[len(order) // 2]), int(order[2])]  # ảnh bài báo, ảnh trung vị, ảnh kém
    kolkur_preds = [kolkur(s.image) for s in samples]
    figure_examples(samples, {"Luật Kolkur": kolkur_preds, "Histogram Bayes": hist_preds}, picks)
    figure_cbcr(samples)
    figure_f1_distribution(kf1, hist_f1, paper_idx)
    print("\n-> results/*.csv, figures/examples.png, figures/cbcr_plane.png, figures/f1_per_image.png")


if __name__ == "__main__":
    main()
