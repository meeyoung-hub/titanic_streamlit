from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Titanic 생존 분석",
    page_icon="⚓",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent / "titanic" / "titanic.csv"
    data = pd.read_csv(data_path)
    data["Age"] = pd.to_numeric(data["Age"], errors="coerce")
    data["Fare"] = pd.to_numeric(data["Fare"], errors="coerce")
    data["SurvivedLabel"] = data["Survived"].map({0: "사망", 1: "생존"})
    data["SexLabel"] = data["Sex"].map({"male": "남성", "female": "여성"})
    return data


data = load_data()

st.title("Titanic 생존 분석")
st.caption("승객의 성별, 객실 등급, 나이에 따른 생존 패턴을 탐색해 보세요.")

with st.sidebar:
    st.header("필터")
    selected_sex = st.multiselect(
        "성별",
        options=["female", "male"],
        default=["female", "male"],
        format_func=lambda value: {"female": "여성", "male": "남성"}[value],
    )
    selected_class = st.multiselect(
        "객실 등급",
        options=[1, 2, 3],
        default=[1, 2, 3],
        format_func=lambda value: f"{value}등석",
    )
    age_range = st.slider(
        "나이 범위",
        min_value=0,
        max_value=80,
        value=(0, 80),
    )

filtered = data[
    data["Sex"].isin(selected_sex)
    & data["Pclass"].isin(selected_class)
    & data["Age"].fillna(-1).between(age_range[0], age_range[1])
].copy()

total = len(filtered)
survivors = int(filtered["Survived"].sum())
survival_rate = survivors / total * 100 if total else 0

metric_columns = st.columns(4)
metric_columns[0].metric("필터 결과 승객", f"{total:,}명")
metric_columns[1].metric("생존자", f"{survivors:,}명")
metric_columns[2].metric("생존율", f"{survival_rate:.1f}%")
metric_columns[3].metric("평균 요금", f"{filtered['Fare'].mean():.2f}" if total else "-")

if filtered.empty:
    st.warning("선택한 조건에 맞는 승객이 없습니다. 필터를 조정해 주세요.")
else:
    chart_column, class_column = st.columns(2)

    with chart_column:
        st.subheader("성별 생존율")
        sex_survival = (
            filtered.groupby("SexLabel")["Survived"]
            .mean()
            .mul(100)
            .rename("생존율")
            .reindex(["여성", "남성"])
            .dropna()
        )
        st.bar_chart(sex_survival, y="생존율", color="#2F855A", height=320)

    with class_column:
        st.subheader("객실 등급별 생존율")
        class_survival = (
            filtered.groupby("Pclass")["Survived"]
            .mean()
            .mul(100)
            .rename("생존율")
            .rename(index=lambda value: f"{value}등석")
        )
        st.bar_chart(class_survival, y="생존율", color="#D97706", height=320)

    st.subheader("성별·객실 등급별 생존율")
    comparison = (
        filtered.pivot_table(
            index="Pclass",
            columns="SexLabel",
            values="Survived",
            aggfunc="mean",
        )
        .mul(100)
        .rename(index=lambda value: f"{value}등석")
        .reindex(columns=["여성", "남성"])
    )
    st.dataframe(comparison.style.format("{:.1f}%"), use_container_width=True)

with st.expander("필터링된 승객 데이터 보기"):
    visible_columns = [
        "PassengerId",
        "SurvivedLabel",
        "Pclass",
        "Name",
        "SexLabel",
        "Age",
        "Fare",
        "Embarked",
    ]
    st.dataframe(
        filtered[visible_columns].rename(
            columns={
                "PassengerId": "승객 번호",
                "SurvivedLabel": "생존 여부",
                "Pclass": "객실 등급",
                "Name": "이름",
                "SexLabel": "성별",
                "Age": "나이",
                "Fare": "요금",
                "Embarked": "탑승 항구",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )