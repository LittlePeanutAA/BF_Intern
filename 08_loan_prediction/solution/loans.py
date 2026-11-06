"""Đọc và làm sạch dữ liệu khoản vay LendingClub 2007–2011 để dự đoán khoản vay có được trả đủ hay không."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "loans_2007.csv"
TARGET = "paid"  # 1 = Fully Paid, 0 = Charged Off

# Cột đề bài yêu cầu bỏ, nhóm theo lý do.
LEAKAGE = [  # chỉ biết được SAU khi đã cho vay: dùng là "nhìn trước tương lai"
    "funded_amnt", "funded_amnt_inv", "issue_d", "out_prncp", "out_prncp_inv", "total_pymnt",
    "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
    "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "last_credit_pull_d",
]
IDENTIFIERS = ["id", "member_id", "url"]               # không liên quan khả năng trả nợ
REDUNDANT = ["grade", "sub_grade",                     # LendingClub suy ra int_rate từ grade
             "title"]                                  # chữ tự do, trùng ý với purpose
NEEDS_WORK = ["emp_title", "zip_code", "earliest_cr_line", "desc", "pub_rec_bankruptcies"]
HIGH_CARDINALITY = ["addr_state"]                      # 51 giá trị: dễ học vẹt, và vùng miền là biến nhạy cảm
DROP = LEAKAGE + IDENTIFIERS + REDUNDANT + NEEDS_WORK + HIGH_CARDINALITY

CATEGORICAL = ["home_ownership", "verification_status", "purpose"]
EMP_LENGTH = {"< 1 year": 0, "1 year": 1, **{f"{i} years": i for i in range(2, 10)}, "10+ years": 10}


def load_raw(path: Path = DATA) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def select_target(df: pd.DataFrame) -> pd.DataFrame:
    """Chỉ giữ khoản vay đã kết thúc (Fully Paid / Charged Off) và tạo cột nhãn 0/1.

    Bỏ 'Current', 'Late…' (chưa biết kết cục) và 'Does not meet the credit policy…'
    (khoản vay theo chính sách cũ, không còn được cấp nữa)."""
    df = df[df["loan_status"].isin(["Fully Paid", "Charged Off"])].copy()
    df[TARGET] = (df["loan_status"] == "Fully Paid").astype(int)
    return df.drop(columns="loan_status")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Bỏ cột theo DROP và cột hằng số, đổi chuỗi về số, chuẩn hoá giá trị phân loại."""
    df = df.drop(columns=[c for c in DROP if c in df])

    df["term"] = df["term"].str.extract(r"(\d+)", expand=False).astype(int)          # " 36 months" -> 36
    for col in ("int_rate", "revol_util"):                                          # "10.65%" -> 10.65
        df[col] = pd.to_numeric(df[col].str.rstrip("%"), errors="coerce")
    df["emp_length"] = df["emp_length"].map(EMP_LENGTH)                              # NaN giữ lại, pipeline xử lý

    # Dữ liệu có lỗi nhập liệu: "RENt", "NOT VERIFIED", " Not Verified", "INDIViDUAL"…
    for col in [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]:
        df[col] = df[col].str.strip().str.lower()
    df["home_ownership"] = df["home_ownership"].replace({"none": "other"})  # 3 dòng "none": gộp vào nhóm hiếm

    # Bỏ cột chỉ có một giá trị (sau khi đã chuẩn hoá, ví dụ application_type toàn "individual").
    constant = [c for c in df if c != TARGET and df[c].nunique(dropna=True) <= 1]
    return df.drop(columns=constant)


def load_dataset(path: Path = DATA) -> pd.DataFrame:
    return clean(select_target(load_raw(path)))


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    return df.drop(columns=TARGET), df[TARGET]


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.select_dtypes(include=np.number).columns if c != TARGET]
