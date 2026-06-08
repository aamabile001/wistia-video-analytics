# Known Limitations and Tradeoffs

This project is production-shaped, but the Wistia source data has a few practical constraints that are documented here for review and handoff.

## API Volume and Pagination

Wistia returns visitor and event records in 100-record pages. The project supports resumable pagination, but high-volume media can require many chunks. During the first production run, `v08dlrgr7v` still returned full 100-record pages at the recorded cap, so the run is documented as bounded and resumable rather than a complete historical backfill.

The runbook includes resume commands for continuing visitor and event pages until the endpoint returns fewer than 100 records or an empty page.

## Incremental Semantics

Raw payloads are partitioned by `run_id`, media ID, endpoint, and page. This preserves source evidence and makes reruns auditable. True source-side incremental filtering depends on the timestamp fields returned by each Wistia endpoint. If Wistia exposes a reliable event or visitor update timestamp for the account, the next improvement would be to add high-watermark filtering around that field.

## Local PySpark Runtime

The transformation is intentionally implemented in PySpark to meet the project requirement. Local Windows execution requires a configured JDK and Hadoop Windows utilities. This is documented in the runbook because environment setup can fail before application code runs.

## Dashboard Scope

The Streamlit dashboard reads curated local Parquet outputs. It is intended as a lightweight project reporting layer, not a hosted BI deployment. The same curated Parquet tables are available through AWS Glue and Athena for SQL validation.

## Data Completeness

Run evidence records row counts, S3 sync status, Glue partition counts, and notes for each run. The final submission should distinguish between:

- Daily production run evidence, which proves the pipeline operates successfully over time.
- Exhaustive historical backfill, which may require additional resumable chunks for high-volume media.

## Cost and Infrastructure

The AWS footprint is intentionally minimal: S3 plus Glue Data Catalog tables. No RDS instance is used or required for the project.
