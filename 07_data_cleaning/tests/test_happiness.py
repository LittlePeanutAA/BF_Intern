import pandas as pd
import pytest

from happiness import COMMON, FACTORS, combine, fill_regions, load_all, load_year, missing_summary


@pytest.fixture(scope="module")
def raw():
    return load_all()


def test_columns_are_standardized(raw):
    for frame in raw.values():
        assert set(COMMON) <= set(frame.columns)
        assert len(frame) == 163


def test_somaliland_name_variants_are_merged(raw):
    somaliland = raw[2015][raw[2015]["country"].str.lower().str.startswith("somaliland")]
    assert somaliland["country"].tolist() == ["Somaliland Region"]
    assert somaliland["score"].notna().all()  # giữ dòng có số liệu, bỏ dòng trống


def test_score_is_sum_of_parts(raw):
    for frame in raw.values():
        f = frame.dropna(subset=["score"])
        assert (f[FACTORS + ["dystopia_residual"]].sum(axis=1) - f["score"]).abs().max() < 1e-3


def test_fill_regions_leaves_no_gap(raw):
    filled = fill_regions(raw)
    assert all(f["region"].notna().all() for f in filled.values())
    assert raw[2017]["region"].isna().all()  # không sửa dữ liệu gốc


def test_combine(raw):
    combined = combine(fill_regions(raw))
    assert list(combined.columns) == COMMON
    assert combined["year"].value_counts().to_dict() == {2015: 158, 2016: 157, 2017: 155}
    assert not combined.duplicated(["country", "year"]).any()
    assert combined[["score", *FACTORS]].notna().all().all()


def test_missing_summary():
    df = pd.DataFrame({"a": [1, None, None, 4], "b": [1, 2, 3, 4]})
    summary = missing_summary(df)
    assert summary.loc["a"].tolist() == [2, 50.0]
    assert summary.loc["b"].tolist() == [0, 0.0]


def test_unknown_column_is_rejected(tmp_path):
    (tmp_path / "wh_2015.csv").write_text("Country,Score2\nX,1\n")
    with pytest.raises(ValueError, match="cột lạ"):
        load_year(2015, tmp_path)
