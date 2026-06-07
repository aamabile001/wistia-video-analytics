from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


CURATED_ROOT = Path("data/curated")


@st.cache_data
def load_parquet(name: str) -> pd.DataFrame:
    path = CURATED_ROOT / name
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

total_plays = int(fact["play_count"].fillna(0).sum()) if "play_count" in fact else 0
unique_visitors = fact["visitor_id"].nunique() if "visitor_id" in fact else 0
watch_time = float(fact["total_watch_time"].fillna(0).sum()) if "total_watch_time" in fact else 0.0

col1, col2, col3 = st.columns(3)
col1.metric("Total plays", f"{total_plays:,}")
col2.metric("Unique visitors", f"{unique_visitors:,}")
col3.metric("Watch time", f"{watch_time:,.1f}")

if {"date", "play_count"}.issubset(fact.columns):
    st.subheader("Daily plays")
    daily = fact.groupby("date", dropna=False)["play_count"].sum().reset_index()
    st.line_chart(daily, x="date", y="play_count")

if {"media_id", "play_count"}.issubset(fact.columns):
    st.subheader("Media performance")
    media_perf = fact.groupby("media_id", dropna=False)["play_count"].sum().reset_index()
    if not media.empty and {"media_id", "title"}.issubset(media.columns):
        media_perf = media_perf.merge(media[["media_id", "title"]], on="media_id", how="left")
    st.dataframe(media_perf.sort_values("play_count", ascending=False), use_container_width=True)

if not visitors.empty:
    st.subheader("Visitors")
    st.dataframe(visitors.head(100), use_container_width=True)
