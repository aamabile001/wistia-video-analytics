# Walkthrough Script

## 1. Business Objective

This project ingests Wistia video analytics for the assigned media IDs, processes media and visitor engagement data, and publishes curated analytics for marketing insight.

Assigned media IDs:

- `gskhw4w4lm`
- `v08dlrgr7v`

## 2. Architecture

The pipeline uses AWS:

- Python ingestion pulls Wistia API data.
- Raw JSON lands in S3 under a run-based folder structure.
- PySpark transforms raw data into curated Parquet.
- Curated Parquet lands in S3.
- Glue tables expose the data model for query.
- Streamlit reads curated outputs for dashboarding.

## 3. API Ingestion

Endpoints used:

- `GET /v1/medias/{media_id}.json`
- `GET /v1/stats/medias/{media_id}.json`
- `GET /v1/stats/visitors.json?media_id={media_id}`
- `GET /v1/stats/events.json?media_id={media_id}`

Credentials are loaded from `.env` and are not committed.

## 4. Transformation

PySpark creates:

- `dim_media`
- `dim_visitor`
- `fact_media_engagement`

The fact table is partitioned by `date`.

## 5. Production Run Evidence

Show `docs/run_evidence.md` and the S3/Glue outputs. Explain that the Wistia visitor/event endpoints are high-volume, so ingestion supports resumable pagination.

## 6. Tradeoffs

- Raw JSON is retained for auditability.
- Curated Parquet supports efficient analytics.
- Pagination can be resumed by page and run ID.
- Timestamp-based incremental filtering is a future enhancement pending confirmed Wistia filter support.
