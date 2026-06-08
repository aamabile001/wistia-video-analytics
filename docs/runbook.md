# Runbook

## Prerequisites

- Python 3.10 or newer
- Java runtime for PySpark, with `JAVA_HOME` set
- AWS CLI
- Copied AWS files in `.aws/config` and `.aws/credentials`
- AWS profile named `wistia-project`
- Wistia token stored in local `.env` as `WISTIA_API_TOKEN`

## Daily Production Run

```powershell
python scripts/run_ingestion.py --media-ids gskhw4w4lm v08dlrgr7v --output-root data/raw
python scripts/run_local_pyspark_pipeline.py --raw-root data/raw --curated-root data/curated
```

If PySpark fails with `Java not found`, install a JDK and set `JAVA_HOME` before rerunning the transformation. On Windows, local PySpark can also fail if Hadoop native utilities such as `winutils.exe` are missing; install/configure the matching Hadoop Windows utilities before rerunning the PySpark job locally.

## Resumable Pagination

Wistia caps each page at 100 records. For high-volume media, run ingestion in chunks and reuse the same `run_id` so raw files land in the same partitioned run folder.

Continue visitor pages for one media ID:

```powershell
python scripts/run_ingestion.py --media-ids v08dlrgr7v --output-root data/raw --run-id 20260608T135031Z --skip-media --skip-events --visitor-start-page 1001 --max-pages 500
```

Continue event pages for one media ID:

```powershell
python scripts/run_ingestion.py --media-ids v08dlrgr7v --output-root data/raw --run-id 20260608T135031Z --skip-media --skip-visitors --event-start-page 376 --max-pages 500
```

After a resume chunk, rerun PySpark and resync S3 curated outputs:

```powershell
python scripts/run_local_pyspark_pipeline.py --raw-root data/raw --curated-root data/curated_spark
```

If the final page in a chunk still contains 100 records, the endpoint may have more data. Continue from the next page until a page returns fewer than 100 records or an empty response.

## Validation Checks

- Confirm each media ID has a raw media stats JSON file.
- Confirm visitor pages are written when visitor records exist.
- Confirm curated Parquet folders are present:
  - `data/curated/dim_media`
  - `data/curated/dim_visitor`
  - `data/curated/fact_media_engagement`
- Confirm Streamlit opens without errors.
- Run the Athena checks in `docs/athena_validation_queries.sql` after S3 curated data and Glue partitions are refreshed.
- Capture screenshots listed in `docs/screenshot_checklist.md` for final submission evidence.

## AWS Identity Check

```powershell
$env:AWS_SHARED_CREDENTIALS_FILE = "..\.aws\credentials"
$env:AWS_CONFIG_FILE = "..\.aws\config"
aws sts get-caller-identity --profile wistia-project
```
