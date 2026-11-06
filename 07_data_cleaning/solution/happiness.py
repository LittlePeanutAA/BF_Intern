"""Đọc, chuẩn hoá và gộp dữ liệu World Happiness 2015–2017."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
YEARS = (2015, 2016, 2017)

# Tên cột mỗi năm đặt một kiểu: đưa hết về snake_case chung.
RENAME = {
    "Country": "country", "Region": "region", "Year": "year",
    "Happiness Rank": "rank", "Happiness.Rank": "rank",
    "Happiness Score": "score", "Happiness.Score": "score",
    "Economy (GDP per Capita)": "economy", "Economy..GDP.per.Capita.": "economy",
    "Family": "family",
    "Health (Life Expectancy)": "health", "Health..Life.Expectancy.": "health",
    "Freedom": "freedom",
    "Trust (Government Corruption)": "trust", "Trust..Government.Corruption.": "trust",
    "Generosity": "generosity",
    "Dystopia Residual": "dystopia_residual", "Dystopia.Residual": "dystopia_residual",
    # Cột chỉ có ở một năm: độ bất định của điểm, mỗi năm báo cáo một kiểu.
    "Standard Error": "standard_error",
    "Lower Confidence Interval": "ci_low", "Upper Confidence Interval": "ci_high",
    "Whisker.low": "ci_low", "Whisker.high": "ci_high",
}
FACTORS = ["economy", "family", "health", "freedom", "trust", "generosity"]
COMMON = ["country", "region", "year", "rank", "score", *FACTORS, "dystopia_residual"]


def load_year(year: int, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Đọc một năm, đổi tên cột, chuẩn hoá tên nước. Giữ nguyên các dòng thiếu dữ liệu."""
    df = pd.read_csv(data_dir / f"wh_{year}.csv").rename(columns=RENAME)
    unknown = set(df.columns) - set(RENAME.values())
    if unknown:
        raise ValueError(f"wh_{year}.csv có cột lạ: {sorted(unknown)}")
    df["country"] = df["country"].str.strip()
    # "Somaliland region" (2015) và "Somaliland Region" (2016) là cùng một nơi.
    df["country"] = df["country"].replace({"Somaliland region": "Somaliland Region"})
    # Sau khi gộp tên, một nước có thể xuất hiện hai lần (một dòng có số liệu, một dòng trống):
    # giữ dòng có số liệu.
    df = (df.assign(_has=df["score"].notna()).sort_values("_has", ascending=False, kind="stable")
            .drop_duplicates("country").drop(columns="_has").sort_index())
    if "region" not in df:  # 2017 không có cột region
        df.insert(1, "region", pd.NA)
    df["year"] = year
    return df


def load_all(data_dir: Path = DATA_DIR) -> dict[int, pd.DataFrame]:
    return {y: load_year(y, data_dir) for y in YEARS}


def fill_regions(frames: dict[int, pd.DataFrame]) -> dict[int, pd.DataFrame]:
    """Region của một nước không đổi theo năm: lấy từ bất kỳ năm nào có thông tin."""
    lookup = (pd.concat([f[["country", "region"]] for f in frames.values()])
              .dropna().drop_duplicates("country").set_index("country")["region"])
    out = {}
    for year, f in frames.items():
        f = f.copy()
        f["region"] = f["region"].fillna(f["country"].map(lookup))
        out[year] = f
    return out


def combine(frames: dict[int, pd.DataFrame], observed_only: bool = True) -> pd.DataFrame:
    """Gộp các năm thành dạng dài (mỗi dòng một nước một năm), chỉ giữ các cột chung.

    observed_only=True bỏ các dòng nước không có trong báo cáo năm đó (score trống)."""
    combined = pd.concat([f[COMMON] for f in frames.values()], ignore_index=True)
    if observed_only:
        combined = combined.dropna(subset=["score"])
    return combined.sort_values(["year", "rank"]).reset_index(drop=True)


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Số ô trống và tỷ lệ % theo từng cột."""
    n = df.isna().sum()
    return pd.DataFrame({"missing": n, "percent": (100 * n / len(df)).round(2)})
