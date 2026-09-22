import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "titanic.csv"
IMAGE_PATH = BASE_DIR / "titanic-survival-pie.png"
SEX_IMAGE_PATH = BASE_DIR / "titanic-survival-by-sex.png"
SEX_PCLASS_IMAGE_PATH = BASE_DIR / "titanic-survival-by-sex-pclass.png"
KOREAN_FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"


def load_survival_counts() -> Counter[str]:
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return Counter(row["Survived"] for row in rows)


def load_survival_counts_by_sex() -> dict[str, Counter[str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        counts_by_sex: dict[str, Counter[str]] = {}
        for row in rows:
            counts_by_sex.setdefault(row["Sex"], Counter())[row["Survived"]] += 1
        return counts_by_sex


def load_survival_counts_by_sex_and_pclass() -> dict[tuple[str, str], Counter[str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        counts: dict[tuple[str, str], Counter[str]] = {}
        for row in rows:
            group = (row["Sex"], row["Pclass"])
            counts.setdefault(group, Counter())[row["Survived"]] += 1
        return counts


def create_chart() -> None:
    counts = load_survival_counts()
    labels = ["사망", "생존"]
    values = [counts["0"], counts["1"]]
    colors = ["#6B7280", "#2F855A"]
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=KOREAN_FONT).get_name()

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 12},
    )
    ax.set_title("타이타닉 승객 생존 여부", fontsize=16, pad=18)
    ax.axis("equal")

    fig.savefig(IMAGE_PATH, dpi=150, bbox_inches="tight")
    print(f"차트 저장 완료: {IMAGE_PATH}")
    print(f"사망: {counts['0']}명, 생존: {counts['1']}명")


def create_sex_chart() -> None:
    counts_by_sex = load_survival_counts_by_sex()
    labels = ["사망", "생존"]
    colors = ["#6B7280", "#2F855A"]
    sex_labels = {"male": "남성", "female": "여성"}
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=KOREAN_FONT).get_name()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for ax, sex in zip(axes, ("male", "female")):
        values = [counts_by_sex[sex]["0"], counts_by_sex[sex]["1"]]
        total = sum(values)
        ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct=lambda percentage: f"{percentage:.1f}%\n({round(percentage * total / 100):,}명)",
            startangle=90,
            counterclock=False,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 11},
        )
        ax.set_title(f"{sex_labels[sex]} 승객 (총 {total}명)", fontsize=15, pad=18)
        ax.axis("equal")

    fig.suptitle("성별 생존 여부 비교", fontsize=18)
    fig.savefig(SEX_IMAGE_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"성별 차트 저장 완료: {SEX_IMAGE_PATH}")
    for sex in ("male", "female"):
        counts = counts_by_sex[sex]
        print(f"{sex_labels[sex]}: 사망 {counts['0']}명, 생존 {counts['1']}명")


def create_sex_pclass_chart() -> None:
    counts = load_survival_counts_by_sex_and_pclass()
    labels = ["사망", "생존"]
    colors = ["#6B7280", "#2F855A"]
    sex_labels = {"male": "남성", "female": "여성"}
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=KOREAN_FONT).get_name()

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for row_index, sex in enumerate(("male", "female")):
        for column_index, pclass in enumerate(("1", "2", "3")):
            ax = axes[row_index, column_index]
            group_counts = counts[(sex, pclass)]
            values = [group_counts["0"], group_counts["1"]]
            total = sum(values)
            ax.pie(
                values,
                labels=labels,
                colors=colors,
                autopct=lambda percentage: f"{percentage:.1f}%\n({round(percentage * total / 100):,}명)",
                startangle=90,
                counterclock=False,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
                textprops={"fontsize": 10},
            )
            ax.set_title(f"{sex_labels[sex]} · {pclass}등석 (총 {total}명)", fontsize=13, pad=14)
            ax.axis("equal")
            print(
                f"{sex_labels[sex]} {pclass}등석: "
                f"사망 {group_counts['0']}명, 생존 {group_counts['1']}명"
            )

    fig.suptitle("성별·객실 등급별 생존 여부 비교", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(SEX_PCLASS_IMAGE_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"성별·객실 등급 차트 저장 완료: {SEX_PCLASS_IMAGE_PATH}")


if __name__ == "__main__":
    create_chart()
    create_sex_chart()
    create_sex_pclass_chart()