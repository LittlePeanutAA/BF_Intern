"""Trả lời 10 câu hỏi của bài 07: in số liệu ra màn hình, lưu hình vào figures/ và bảng vào results/.

    python analyze.py
"""
from pathlib import Path

import matplotlib
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")  # chỉ lưu file, không mở cửa sổ
import matplotlib.pyplot as plt  # noqa: E402

from happiness import FACTORS, YEARS, combine, fill_regions, load_all, missing_summary  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG, OUT = ROOT / "figures", ROOT / "results"
LABELS = {"economy": "Kinh tế (GDP)", "family": "Gia đình", "health": "Sức khoẻ",
          "freedom": "Tự do", "trust": "Niềm tin (chính phủ)", "generosity": "Sự hào phóng",
          "dystopia_residual": "Phần dư Dystopia"}
pd.set_option("display.width", 140, "display.max_columns", 20, "display.precision", 3)


def section(title: str) -> None:
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=120)
    plt.close(fig)
    print(f"-> figures/{name}")


def q1_factors(df15: pd.DataFrame) -> None:
    section("Câu 1: yếu tố đóng góp nhiều nhất vào điểm hạnh phúc 2015")
    parts = FACTORS + ["dystopia_residual"]
    gap = (df15[parts].sum(axis=1) - df15["score"]).abs().max()
    print(f"Kiểm tra: score = tổng 6 yếu tố + phần dư, sai lệch lớn nhất {gap:.4f}")
    table = pd.DataFrame({
        "đóng_góp_tb": df15[parts].mean(),
        "tỷ_lệ_%": 100 * df15[parts].mean() / df15["score"].mean(),
        "tương_quan_với_score": df15[parts].corrwith(df15["score"]),
    }).sort_values("đóng_góp_tb", ascending=False)
    print(table)
    table.to_csv(OUT / "q1_factors_2015.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    table["đóng_góp_tb"].rename(LABELS).plot.barh(ax=axes[0], color="#4C72B0")
    axes[0].invert_yaxis()
    axes[0].set(title="Đóng góp trung bình vào điểm (2015)", xlabel="điểm")
    corr = table.loc[FACTORS, "tương_quan_với_score"].sort_values()
    corr.rename(LABELS).plot.barh(ax=axes[1], color="#55A868")
    axes[1].set(title="Tương quan với điểm hạnh phúc (2015)", xlabel="hệ số Pearson")
    save(fig, "q1_factors_2015.png")


def q2_aggregation(df15: pd.DataFrame) -> pd.DataFrame:
    section("Câu 2: gộp nhóm (aggregate) cho thấy gì")
    by_region = (df15.groupby("region")["score"]
                 .agg(countries="count", mean="mean", median="median", std="std", min="min", max="max")
                 .sort_values("mean", ascending=False))
    print(by_region)
    by_region.to_csv(OUT / "q2_score_by_region_2015.csv")
    profile = df15.groupby("region")[FACTORS].mean().loc[by_region.index]
    print("\nĐóng góp trung bình của từng yếu tố theo khu vực:")
    print(profile)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1, 1.2]})
    order = by_region.index
    sns.boxplot(data=df15, y="region", x="score", order=order, ax=axes[0], color="#DDDDDD")
    sns.stripplot(data=df15, y="region", x="score", order=order, ax=axes[0], size=3, color="#C44E52")
    axes[0].set(title="Phân bố điểm theo khu vực (2015)", ylabel="", xlabel="điểm hạnh phúc")
    profile.rename(columns=LABELS).plot.barh(stacked=True, ax=axes[1], colormap="tab10")
    axes[1].invert_yaxis()
    axes[1].set(title="Điểm được giải thích bởi từng yếu tố", xlabel="điểm", ylabel="")
    axes[1].legend(fontsize=8, loc="lower right")
    save(fig, "q2_region_aggregation_2015.png")
    return by_region


def q3_region_vs_world(df15: pd.DataFrame, by_region: pd.DataFrame) -> None:
    section("Câu 3: hạnh phúc theo khu vực so với toàn thế giới")
    world_mean = df15["score"].mean()
    weighted = (by_region["mean"] * by_region["countries"]).sum() / by_region["countries"].sum()
    print(f"Trung bình thế giới (mỗi nước 1 phiếu): {world_mean:.3f}")
    print(f"Trung bình của 10 khu vực (mỗi khu vực 1 phiếu): {by_region['mean'].mean():.3f}"
          f"  <- khác, vì các khu vực có số nước rất khác nhau")
    print(f"Trung bình khu vực có trọng số theo số nước: {weighted:.3f} (= trung bình thế giới)")
    diff = (by_region["mean"] - world_mean).rename("chênh_lệch_so_với_thế_giới")
    print(diff.round(3).to_string())

    world_corr = df15[FACTORS].corrwith(df15["score"]).rename("Thế giới")
    regional = {r: g[FACTORS].corrwith(g["score"]) for r, g in df15.groupby("region") if len(g) >= 8}
    corr = pd.concat([world_corr, pd.DataFrame(regional)], axis=1).T
    print("\nTương quan yếu tố–điểm trong từng khu vực (chỉ khu vực có >= 8 nước):")
    print(corr.round(2))
    corr.to_csv(OUT / "q3_factor_correlation_by_region_2015.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1, 1.3]})
    diff.sort_values().plot.barh(ax=axes[0], color=["#C44E52" if v < 0 else "#55A868" for v in diff.sort_values()])
    axes[0].axvline(0, color="black", lw=0.8)
    axes[0].set(title=f"Chênh lệch so với trung bình thế giới ({world_mean:.2f})", xlabel="điểm", ylabel="")
    sns.heatmap(corr.rename(columns=LABELS), annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=axes[1])
    axes[1].set(title="Tương quan yếu tố–điểm: thế giới và từng khu vực")
    save(fig, "q3_region_vs_world_2015.png")


def q4_merge_ways(frames: dict[int, pd.DataFrame]) -> None:
    section("Câu 4: các cách gộp DataFrame")
    a = frames[2015].dropna(subset=["score"])[["country", "score"]]
    b = frames[2016].dropna(subset=["score"])[["country", "score"]]
    print(f"2015 có {len(a)} nước, 2016 có {len(b)} nước, chung {len(set(a.country) & set(b.country))}")
    for how in ("inner", "left", "right", "outer"):
        m = a.merge(b, on="country", how=how, suffixes=("_2015", "_2016"))
        print(f"merge how={how:<5} -> {len(m)} dòng")
    print(f"concat theo dòng (axis=0) -> {len(pd.concat([a, b]))} dòng")
    print(f"concat theo cột (axis=1, căn theo index country) -> "
          f"{len(pd.concat([a.set_index('country'), b.set_index('country')], axis=1))} dòng")
    print(f"join (căn theo index) how=left -> {len(a.set_index('country').join(b.set_index('country'), suffixes=('', '_2016')))} dòng")


def q5_combine(frames: dict[int, pd.DataFrame]) -> pd.DataFrame:
    section("Câu 5: gộp 2015, 2016, 2017")
    combined = combine(frames)
    print(f"Dạng dài: {combined.shape[0]} dòng x {combined.shape[1]} cột; "
          f"số dòng theo năm {combined['year'].value_counts().sort_index().to_dict()}")
    print(combined.head(3))
    combined.to_csv(OUT / "happiness_2015_2017.csv", index=False)
    print("-> results/happiness_2015_2017.csv")
    return combined


def q6_change(combined: pd.DataFrame) -> None:
    section("Câu 6: hạnh phúc thế giới thay đổi thế nào 2015 -> 2017")
    # Chỉ so trên các nước có mặt cả 3 năm, để thay đổi không bị lẫn với thay đổi danh sách nước.
    present = combined.groupby("country")["year"].nunique()
    panel = combined[combined["country"].isin(present[present == len(YEARS)].index)]
    print(f"Số nước có mặt đủ 3 năm: {panel['country'].nunique()}")
    yearly = panel.groupby("year")[["score", *FACTORS]].mean()
    print(yearly)
    wide = panel.pivot(index="country", columns="year", values="score")
    wide["change"] = wide[2017] - wide[2015]
    print(f"\nĐiểm trung bình đổi {wide['change'].mean():+.3f}; "
          f"{(wide['change'] > 0).sum()} nước tăng, {(wide['change'] < 0).sum()} nước giảm")
    print("Tăng nhiều nhất:", wide["change"].nlargest(5).round(2).to_dict())
    print("Giảm nhiều nhất:", wide["change"].nsmallest(5).round(2).to_dict())
    region_year = panel.pivot_table(index="region", columns="year", values="score", aggfunc="mean")
    region_year.to_csv(OUT / "q6_region_by_year.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    region_year.T.plot(ax=axes[0], marker="o")
    axes[0].set(title="Điểm trung bình theo khu vực", xlabel="năm", ylabel="điểm", xticks=list(YEARS))
    axes[0].legend(fontsize=7)
    movers = pd.concat([wide["change"].nsmallest(8), wide["change"].nlargest(8)]).sort_values()
    movers.plot.barh(ax=axes[1], color=["#C44E52" if v < 0 else "#55A868" for v in movers])
    axes[1].set(title="Thay đổi điểm lớn nhất 2015 -> 2017", xlabel="điểm 2017 - điểm 2015", ylabel="")
    save(fig, "q6_change_2015_2017.png")


def q7_to_q9_missing(raw: dict[int, pd.DataFrame]) -> None:
    section("Câu 7-9: dữ liệu thiếu")
    full = pd.concat(raw.values(), ignore_index=True).sort_values(["year", "country"])
    summary = missing_summary(full)
    print(summary[summary["missing"] > 0])
    total = full.isna().to_numpy().mean() * 100
    print(f"\nTỷ lệ ô trống trên toàn bảng gộp (cả cột riêng từng năm): {total:.1f}%")
    common = full.drop(columns=["standard_error", "ci_low", "ci_high"])
    print(f"Chỉ tính các cột chung: {common.isna().to_numpy().mean() * 100:.1f}%")
    print(f"Số dòng còn lại nếu dropna() thẳng trên bảng gộp: {len(full.dropna())} / {len(full)}")
    print(f"Số dòng còn lại nếu chỉ bỏ dòng thiếu score: {len(full.dropna(subset=['score']))} / {len(full)}")

    empty_rows = full[full["score"].isna()]
    other = empty_rows.drop(columns=["country", "year", "region"]).notna().sum().sum()
    print(f"\nDòng thiếu score: {len(empty_rows)}; số ô có giá trị khác ngoài country/year/region: {other}")
    for year, countries in empty_rows.groupby("year")["country"]:
        print(f"  {year}: {', '.join(countries)}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.6, 1]})
    sns.heatmap(full.set_index(["year", "country"]).isna(), cbar=False, cmap=["#EEEEEE", "#C44E52"],
                yticklabels=False, ax=axes[0])
    per_year = len(full) / len(YEARS)
    axes[0].set(title="Ô trống (đỏ) trên bảng gộp 3 năm, mỗi hàng một nước-năm", ylabel="")
    axes[0].set_yticks([(i + 0.5) * per_year for i in range(len(YEARS))], YEARS, rotation=0)
    for i in range(1, len(YEARS)):
        axes[0].axhline(i * per_year, color="black", lw=1)
    sns.heatmap(full.drop(columns=["standard_error", "ci_low", "ci_high"]).isna().corr().fillna(0),
                cmap="Blues", vmin=0, vmax=1, ax=axes[1], annot=False)
    axes[1].set(title="Tương quan giữa vị trí ô trống của các cột")
    save(fig, "q7_missing_heatmap.png")


def main() -> None:
    FIG.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    raw = load_all()
    frames = fill_regions(raw)
    df15 = frames[2015].dropna(subset=["score"])
    q1_factors(df15)
    by_region = q2_aggregation(df15)
    q3_region_vs_world(df15, by_region)
    q4_merge_ways(frames)
    combined = q5_combine(frames)
    q6_change(combined)
    q7_to_q9_missing(raw)


if __name__ == "__main__":
    main()
