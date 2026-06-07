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

If PySpark fails with `Java not found`, install a JDK and set `JAVA_HOME` before rerunning the transformation.

## Validation Checks

- Confirm each media ID has a raw media stats JSON file.
- Confirm visitor pages are written when visitor records exist.
- Confirm curated Parquet folders are present:
  - `data/curated/dim_media`
  - `data/curated/dim_visitor`
  - `data/curated/fact_media_engagement`
- Confirm Streamlit opens without errors.

## AWS Identity Check

```powershell
$env:AWS_SHARED_CREDENTIALS_FILE = "C:\path\to\project\.aws\credentials"
$env:AWS_CONFIG_FILE = "C:\path\to\project\.aws\config"
aws sts get-caller-identity --profile wistia-project
```
