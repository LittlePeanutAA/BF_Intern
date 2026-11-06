import numpy as np
import pandas as pd
import pytest

from loans import DROP, LEAKAGE, TARGET, clean, load_dataset, select_target
from train import portfolio_table


@pytest.fixture(scope="module")
def data():
    return load_dataset()


def test_only_finished_loans(data):
    assert len(data) == 38_782
    assert set(data[TARGET]) == {0, 1}
    assert round(1 - data[TARGET].mean(), 4) == 0.1453


def test_no_leakage_or_dropped_columns(data):
    assert not set(DROP) & set(data.columns)
    assert "loan_status" not in data


def test_types(data):
    assert data["term"].isin([36, 60]).all()
    assert data["int_rate"].between(5, 25).all()
    assert data["revol_util"].dropna().between(0, 100).all()
    assert data["emp_length"].dropna().between(0, 10).all()


def test_dirty_categories_are_normalized(data):
    assert set(data["home_ownership"]) == {"rent", "mortgage", "own", "other"}
    assert set(data["verification_status"]) == {"not verified", "verified", "source verified"}
    assert "application_type" not in data  # chỉ còn một giá trị sau khi chuẩn hoá


def test_clean_on_handmade_rows():
    raw = pd.DataFrame({
        "loan_status": ["Fully Paid", "Charged Off", "Fully Paid", "Current"],
        "term": [" 36 months", " 60 months", " 36 months", " 36 months"],
        "int_rate": ["10.65%", "15.27%", "7.00%", "9.00%"],
        "revol_util": ["83.7%", None, "1%", "5%"],
        "emp_length": ["10+ years", "< 1 year", None, "1 year"],
        "home_ownership": ["RENt", " own", "NONE", "RENT"],
        "verification_status": [" Not Verified", "VERIFIED", "Verified", "Verified"],
        "purpose": ["car", "Car ", "CAR", "car"],
        "total_pymnt": [1.0, 2.0, 3.0, 4.0],   # cột rò rỉ, phải bị bỏ
        "loan_amnt": [1000.0, 2000.0, 3000.0, 4000.0],
    })
    out = clean(select_target(raw))
    assert out[TARGET].tolist() == [1, 0, 1]
    assert out["term"].tolist() == [36, 60, 36]
    assert out["int_rate"].tolist() == [10.65, 15.27, 7.0]
    assert out["revol_util"].iloc[0] == 83.7 and pd.isna(out["revol_util"].iloc[1])
    assert out["emp_length"].iloc[:2].tolist() == [10, 0] and pd.isna(out["emp_length"].iloc[2])
    assert out["home_ownership"].tolist() == ["rent", "own", "other"]
    assert out["verification_status"].tolist() == ["not verified", "verified", "verified"]
    assert "total_pymnt" not in out and "purpose" not in out  # purpose thành hằng số "car"


def test_leakage_columns_really_leak():
    """Kiểm chứng lý do bỏ cột: total_rec_prncp gần như cho biết luôn kết quả."""
    raw = select_target(pd.read_csv(
        __import__("loans").DATA, usecols=["loan_status", "loan_amnt", "total_rec_prncp"], low_memory=False))
    repaid_all = (raw["total_rec_prncp"] >= raw["loan_amnt"] - 1).astype(int)
    assert (repaid_all == raw[TARGET]).mean() > 0.95
    assert "total_rec_prncp" in LEAKAGE


def test_portfolio_table():
    y = pd.Series([1, 1, 0, 1, 0])
    p = np.array([0.9, 0.8, 0.7, 0.6, 0.1])
    table = portfolio_table(y, p, [0.4, 1.0])
    assert table["số_khoản"].tolist() == [2, 5]
    assert table["tỷ_lệ_vỡ_nợ_%"].tolist() == [0.0, 40.0]
