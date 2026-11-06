"""Minh hoạ rò rỉ dữ liệu: thêm lại các cột chỉ biết được sau khi cho vay thì mô hình "giỏi" bất thường.

    python leakage_demo.py
"""
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

from loans import TARGET, load_raw, select_target

raw = select_target(load_raw())
y = raw[TARGET]
honest = ["loan_amnt", "int_rate_num", "annual_inc", "dti"]
leaky = honest + ["total_rec_prncp", "recoveries", "last_pymnt_amnt"]
raw["int_rate_num"] = raw["int_rate"].str.rstrip("%").astype(float)
repaid_all = (raw["total_rec_prncp"] >= raw["loan_amnt"] - 1).astype(int)
print(f"Quy tắc 'đã trả đủ gốc' (total_rec_prncp >= loan_amnt) khớp nhãn {100 * (repaid_all == y).mean():.1f}%")

for name, cols in [("4 cột biết trước khi cho vay", honest), ("+ 3 cột rò rỉ", leaky)]:
    model = HistGradientBoostingClassifier(random_state=0)
    auc = cross_val_score(model, raw[cols], y, cv=5, scoring="roc_auc").mean()
    print(f"{name:<30} ROC AUC {auc:.3f}")
