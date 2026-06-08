from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st


CURATED_ROOT = Path("data/curated")
SPARK_CURATED_ROOT = Path("data/curated_spark")
DEFAULT_START_DATE = date(2026, 1, 1)
DEFAULT_END_DATE = date(2026, 6, 30)


@st.cache_data
def load_parquet(name: str) -> pd.DataFrame:
    root = SPARK_CURATED_ROOT if (SPARK_CURATED_ROOT / name).exists() else CURATED_ROOT
    path = root / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


st.set_page_config(page_title="Wistia Video Analytics", layout="wide")
st.title("Wistia Video Analytics")

fact = load_parquet("fact_media_engagement")
media = load_parquet("dim_media")
visitors = load_parquet("dim_visitor")

if fact.empty:
    st.info("No curated engagement data found. Run ingestion and the PySpark pipeline first.")
    st.stop()

if "date" in fact.columns:
    fact["date"] = pd.to_datetime(fact["date"], errors="coerce").dt.date
    dates = sorted(date for date in fact["date"].dropna().unique())
    if dates:
        default_start = max(dates[0], DEFAULT_START_DATE)
        default_end = min(dates[-1], DEFAULT_END_DATE)
        if default_start > default_end:
            default_start, default_end = dates[0], dates[-1]
        selected_dates = st.date_input(
            "Date range",
            value=(default_start, default_end),
            min_value=dates[0],
            max_value=dates[-1],
        )
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
            fact = fact[(fact["date"] >= start_date) & (fact["date"] <= end_date)]

total_plays = int(fact["play_count"].fillna(0).sum()) if "play_count" in fact.columns else 0
unique_visitors = fact["visitor_id"].dropna().nunique() if "visitor_id" in fact.columns else 0
watch_time = (
    float(fact["total_watch_time"].fillna(0).sum()) if "total_watch_time" in fact.columns else 0.0
)
avg_watched = (
    float(fact["watched_percent"].dropna().mean()) if "watched_percent" in fact.columns else 0.0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total plays", f"{total_plays:,}")
col2.metric("Unique visitors", f"{unique_visitors:,}")
col3.metric("Watch time", f"{watch_time:,.0f}s")
col4.metric("Avg watched", f"{avg_watched:.1%}")

if {"date", "play_count"}.issubset(fact.columns):
    st.subheader("Daily plays")
    daily = fact.groupby("date", dropna=False)["play_count"].sum().reset_index()
    st.line_chart(daily, x="date", y="play_count")

if {"media_id", "play_count"}.issubset(fact.columns):
    st.subheader("Media performance")
    media_perf = fact.groupby("media_id", dropna=False)["play_count"].sum().reset_index()
    if not media.empty and {"media_id", "title"}.issubset(media.columns):
        media_perf = media_perf.merge(media[["media_id", "title"]], on="media_id", how="left")
    st.dataframe(media_perf.sort_values("play_count", ascending=False), width="stretch")

if not visitors.empty:
    st.subheader("Visitor geography")
    if "country" in visitors.columns:
        countries = (
            visitors["country"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("country")
            .reset_index(name="visitors")
        )
        st.dataframe(countries.head(25), width="stretch")

    st.subheader("Visitor sample")
    st.dataframe(visitors.head(100), width="stretch")

st.subheader("Engagement sample")
st.dataframe(fact.head(100), width="stretch")
