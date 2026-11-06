"""Huấn luyện và đánh giá mô hình dự đoán khoản vay được trả đủ.

    python train.py              # in kết quả, lưu hình vào ../figures
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from loans import CATEGORICAL, load_dataset, numeric_columns, split_xy

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
SEED = 42
SKEWED = ["annual_inc", "revol_bal"]  # lệch phải rất mạnh: lấy log trước khi chuẩn hoá cho mô hình tuyến tính


def preprocessor(numeric: list[str], scale: bool) -> ColumnTransformer:
    """Điền thiếu + mã hoá. Nằm TRONG pipeline nên chỉ học từ tập train của mỗi lần fit."""
    if scale:
        num = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
        log = make_pipeline(SimpleImputer(strategy="median"), FunctionTransformer(np.log1p), StandardScaler())
        parts = [("num", num, [c for c in numeric if c not in SKEWED]), ("log", log, SKEWED)]
    else:  # mô hình cây không cần chuẩn hoá hay lấy log
        parts = [("num", SimpleImputer(strategy="median", add_indicator=True), numeric)]
    parts.append(("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL))
    return ColumnTransformer(parts)


def models(numeric: list[str]) -> dict:
    return {
        "Baseline (luôn đoán 'trả đủ')": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": make_pipeline(
            preprocessor(numeric, scale=True),
            LogisticRegression(class_weight="balanced", max_iter=2000)),
        "Random Forest": make_pipeline(
            preprocessor(numeric, scale=False),
            RandomForestClassifier(n_estimators=300, min_samples_leaf=20, class_weight="balanced_subsample",
                                   n_jobs=-1, random_state=SEED)),
        "Gradient Boosting": make_pipeline(
            preprocessor(numeric, scale=False),
            HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
                                           class_weight="balanced", random_state=SEED)),
    }


def portfolio_table(y_true: pd.Series, p_paid: np.ndarray, approve: list[float],
                    int_rate: pd.Series | None = None) -> pd.DataFrame:
    """Nhà đầu tư chỉ cho vay x% khoản có xác suất trả đủ cao nhất: tỷ lệ vỡ nợ trong danh mục là bao nhiêu?"""
    order = np.argsort(-p_paid, kind="stable")
    y = y_true.to_numpy()[order]
    rows = []
    for share in approve:
        k = max(1, int(round(share * len(y))))
        row = {"cho_vay_%": round(100 * share), "số_khoản": k,
               "tỷ_lệ_vỡ_nợ_%": round(100 * (1 - y[:k].mean()), 2),
               "ngưỡng_xác_suất": round(float(p_paid[order][k - 1]), 3)}
        if int_rate is not None:
            row["lãi_suất_tb_%"] = round(float(int_rate.to_numpy()[order][:k].mean()), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    FIG.mkdir(exist_ok=True)
    df = load_dataset()
    X, y = split_xy(df)
    numeric = numeric_columns(df)
    print(f"{len(df):,} khoản vay, {X.shape[1]} đặc trưng; tỷ lệ vỡ nợ {100 * (1 - y.mean()):.2f}%")

    # Giữ riêng 20% làm tập test, chỉ dùng MỘT lần ở cuối. Chọn mô hình bằng cross-validation trên 80% còn lại.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    print("\n== ROC AUC, 5-fold cross-validation trên tập train")
    fitted, cv_scores = {}, {}
    for name, model in models(numeric).items():
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
        cv_scores[name] = scores.mean()
        print(f"{name:<30} {scores.mean():.4f} ± {scores.std():.4f}")
        fitted[name] = model.fit(X_train, y_train)

    print("\n== Tập test (chưa từng dùng khi chọn mô hình)")
    probs = {name: m.predict_proba(X_test)[:, 1] for name, m in fitted.items()}
    # Mốc so sánh quan trọng: lãi suất do LendingClub đặt đã phản ánh rủi ro.
    # Xếp hạng chỉ bằng lãi suất (thấp = an toàn) đạt được bao nhiêu?
    rate = X_test["int_rate"].to_numpy()
    probs["Chỉ dùng lãi suất"] = 1 - (rate - rate.min()) / (rate.max() - rate.min())
    for name, p in probs.items():
        print(f"{name:<30} ROC AUC {roc_auc_score(y_test, p):.4f}")

    best = max((n for n in cv_scores if not n.startswith("Baseline")), key=cv_scores.get)
    print(f"\n== Danh mục cho vay theo '{best}' (tỷ lệ vỡ nợ khi cho vay tất cả: {100 * (1 - y_test.mean()):.2f}%)")
    table = portfolio_table(y_test, probs[best], [0.1, 0.25, 0.5, 0.75, 1.0], X_test["int_rate"])
    print(table.to_string(index=False))
    print("\n== Cùng bảng nhưng chỉ xếp theo lãi suất")
    print(portfolio_table(y_test, probs["Chỉ dùng lãi suất"], [0.1, 0.25, 0.5, 0.75, 1.0],
                          X_test["int_rate"]).to_string(index=False))

    # --- Hình ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name, p in probs.items():
        fpr, tpr, _ = roc_curve(y_test, p)
        axes[0].plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y_test, p):.3f})")
    axes[0].set(title="Đường ROC trên tập test", xlabel="tỷ lệ khoản VỠ NỢ bị duyệt nhầm (FPR)",
                ylabel="tỷ lệ khoản TRẢ ĐỦ được duyệt (TPR)")
    axes[0].legend(fontsize=8)
    shares = np.linspace(0.02, 1, 50)
    for name, p in probs.items():
        if name.startswith("Baseline"):
            continue
        curve = portfolio_table(y_test, p, list(shares))
        axes[1].plot(curve["cho_vay_%"], curve["tỷ_lệ_vỡ_nợ_%"], label=name)
    axes[1].axhline(100 * (1 - y_test.mean()), color="gray", ls="--", label="cho vay tất cả")
    axes[1].set(title="Chọn lọc càng chặt, danh mục càng an toàn", xlabel="% khoản vay được duyệt (xếp theo mô hình)",
                ylabel="% vỡ nợ trong các khoản được duyệt")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "roc_and_portfolio.png", dpi=120)
    plt.close(fig)

    imp = permutation_importance(fitted[best], X_test, y_test, scoring="roc_auc", n_repeats=5,
                                 random_state=SEED, n_jobs=-1)
    importance = pd.Series(imp.importances_mean, index=X_test.columns).sort_values()
    print("\n== Mức quan trọng (AUC giảm khi xáo trộn cột), top 8")
    print(importance.sort_values(ascending=False).head(8).round(4).to_string())
    fig, ax = plt.subplots(figsize=(7, 5))
    importance.plot.barh(ax=ax, color="#4C72B0")
    ax.set(title=f"Permutation importance ({best})", xlabel="AUC giảm khi xáo trộn cột")
    fig.tight_layout()
    fig.savefig(FIG / "feature_importance.png", dpi=120)
    plt.close(fig)
    print("\n-> figures/roc_and_portfolio.png, figures/feature_importance.png")


if __name__ == "__main__":
    main()
