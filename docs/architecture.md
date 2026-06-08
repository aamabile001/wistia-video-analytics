# Architecture

## Chosen Platform

AWS is the target cloud platform.

## Components

- **Python ingestion job**: Authenticates with Wistia using `WISTIA_API_TOKEN`, calls media and visitor stats endpoints, handles pagination, and writes raw JSON.
- **Amazon S3 raw zone**: Stores immutable API payloads partitioned by run ID, media ID, and page.
- **PySpark transformation job**: Reads raw JSON and writes curated Parquet tables.
- **Amazon S3 curated zone**: Stores dimensional model outputs.
- **AWS Glue Data Catalog / Athena**: Provides queryable table metadata for curated Parquet.
- **Streamlit dashboard**: Reads curated Parquet for reporting.
- **GitHub Actions**: Runs linting and tests on every push and pull request.

## Production Run Plan

Run ingestion and transformation once per day for 7 consecutive days. Each run gets a UTC `run_id` so raw payloads are traceable.

## Incremental Strategy

The ingestion layer preserves each run's raw payloads and supports incremental extension through date and page parameters. Once the exact Wistia visitor payload is validated with the real token, incremental filtering should use the most reliable available timestamp field, such as `created_at`, `updated_at`, or event receipt timestamp.

## Wistia API Findings

- Media metadata is pulled from the Wistia Data API.
- Media aggregate stats are pulled from the Wistia Stats API.
- Media stats by date are pulled from the modern Stats API.
- Visitor-level records are pulled from `GET /v1/stats/visitors.json?media_id={media_id}`.
- Event-level records are pulled from `GET /v1/stats/events.json?media_id={media_id}`.

## Tradeoffs

- Raw JSON is retained to make schema drift auditable.
- Parquet is used for curated outputs because it is efficient for Spark and Athena.
- Streamlit is used for project-friendly reporting without requiring paid BI setup.
- Bearer authentication is used because it matches current Wistia examples and the requirement document's sample code.
