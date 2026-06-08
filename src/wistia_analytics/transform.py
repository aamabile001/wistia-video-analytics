from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.column import Column
from pyspark.sql.types import ArrayType, StringType, StructField, StructType


def create_spark(app_name: str = "wistia-video-analytics") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def _read_json_if_exists(spark: SparkSession, path: Path) -> DataFrame | None:
    if not path.exists():
        return None
    files = list(path.rglob("*.json"))
    if not files:
        return None
    return spark.read.option("multiLine", True).json(str(path))


def _has_field(schema: StructType, path: str) -> bool:
    current = schema
    for part in path.split("."):
        if not isinstance(current, StructType):
            return False
        field = next((item for item in current.fields if item.name == part), None)
        if field is None:
            return False
        current = field.dataType
    return True


def _col_or_null(df: DataFrame, name: str) -> Column:
    if _has_field(df.schema, name):
        return F.col(name)
    return F.lit(None)


def _first_available(df: DataFrame, *names: str) -> Column:
    return F.coalesce(*[_col_or_null(df, name) for name in names])


def _first_available_string(df: DataFrame, *names: str) -> Column:
    return F.coalesce(*[_col_or_null(df, name).cast("string") for name in names])


def build_dim_media(media_df: DataFrame) -> DataFrame:
    return media_df.select(
        _first_available_string(media_df, "media_id", "payload.hashed_id", "payload.id", "hashed_id", "id")
        .alias("media_id"),
        _first_available_string(media_df, "payload.name", "payload.title", "title", "name").alias("title"),
        _first_available_string(media_df, "payload.url", "payload.embed_url", "url", "embed_url").alias("url"),
        F.lit(None).cast("string").alias("channel"),
        _first_available(media_df, "payload.created", "payload.created_at", "created_at", "created")
        .cast("timestamp")
        .alias("created_at"),
    ).dropDuplicates(["media_id"])


def normalize_payload_records(df: DataFrame) -> DataFrame:
    payload_field = next((field for field in df.schema.fields if field.name == "payload"), None)
    if payload_field is not None and isinstance(payload_field.dataType, ArrayType):
        exploded = df.select(
            F.col("media_id").cast("string").alias("_envelope_media_id"),
            F.col("run_id").cast("string").alias("_envelope_run_id"),
            F.explode_outer("payload").alias("record"),
        )
        element_type = payload_field.dataType.elementType
        if isinstance(element_type, StructType):
            record_fields = [field.name for field in element_type.fields]
            columns = []
            if "media_id" not in record_fields:
                columns.append(F.col("_envelope_media_id").alias("media_id"))
            if "run_id" not in record_fields:
                columns.append(F.col("_envelope_run_id").alias("run_id"))
            columns.extend(F.col(f"record.`{name}`").alias(name) for name in record_fields)
            return exploded.select(*columns)
        return exploded.select(
            F.col("_envelope_media_id").alias("media_id"),
            F.col("_envelope_run_id").alias("run_id"),
            F.col("record").alias("value"),
        )
    return df


def normalize_visitor_records(visitor_df: DataFrame) -> DataFrame:
    if _has_field(visitor_df.schema, "payload.visitors"):
        return visitor_df.select(
            F.col("media_id").cast("string").alias("media_id"),
            F.explode_outer("payload.visitors").alias("visitor"),
        ).select("media_id", "visitor.*")
    return normalize_payload_records(visitor_df)


def build_dim_visitor(visitor_df: DataFrame) -> DataFrame:
    visitor_records = visitor_df.select(
        _first_available_string(visitor_df, "visitor_key", "visitor_id", "id", "visitor_identity")
        .alias("visitor_id"),
        _first_available_string(visitor_df, "ip", "ip_address").alias("ip_address"),
        _first_available_string(visitor_df, "country", "country_name").alias("country"),
    ).where(F.col("visitor_id").isNotNull())
    return visitor_records.groupBy("visitor_id").agg(
        F.first("ip_address", ignorenulls=True).alias("ip_address"),
        F.first("country", ignorenulls=True).alias("country"),
    )


def build_fact_media_engagement(visitor_df: DataFrame) -> DataFrame:
    return visitor_df.select(
        _first_available_string(visitor_df, "media_id", "media_hashed_id").alias("media_id"),
        _first_available_string(visitor_df, "visitor_key", "visitor_id", "id").alias("visitor_id"),
        F.to_date(
            F.coalesce(_first_available(visitor_df, "created_at", "received_at"), F.current_timestamp())
        ).alias("date"),
        F.coalesce(_first_available(visitor_df, "play_count", "plays"), F.lit(1))
        .cast("long")
        .alias("play_count"),
        _first_available(visitor_df, "play_rate", "percent_played").cast("double").alias("play_rate"),
        _first_available(visitor_df, "total_watch_time", "time_watched").cast("double").alias(
            "total_watch_time"
        ),
        _first_available(visitor_df, "watched_percent", "percent_watched").cast("double").alias(
            "watched_percent"
        ),
    ).where(F.col("visitor_id").isNotNull())


def build_fact_event_engagement(event_df: DataFrame) -> DataFrame:
    return event_df.select(
        _first_available_string(event_df, "media_id", "media_hashed_id").alias("media_id"),
        _first_available_string(event_df, "visitor_key", "visitor_id", "visitor_identity").alias(
            "visitor_id"
        ),
        F.to_date(
            F.coalesce(_first_available(event_df, "received_at", "created_at"), F.current_timestamp())
        ).alias("date"),
        F.lit(1).cast("long").alias("play_count"),
        _first_available(event_df, "play_rate", "percent_played").cast("double").alias("play_rate"),
        _first_available(event_df, "total_watch_time", "time_watched").cast("double").alias(
            "total_watch_time"
        ),
        _first_available(event_df, "watched_percent", "percent_watched", "percent_viewed")
        .cast("double")
        .alias("watched_percent"),
    ).where(F.col("media_id").isNotNull())


def build_fact_media_stats(media_stats_df: DataFrame) -> DataFrame:
    return media_stats_df.select(
        _first_available_string(media_stats_df, "media_id", "payload.media_id").alias("media_id"),
        F.lit(None).cast("string").alias("visitor_id"),
        F.to_date(F.to_timestamp(F.col("run_id"), "yyyyMMdd'T'HHmmss'Z'")).alias("date"),
        _first_available(media_stats_df, "payload.play_count", "play_count")
        .cast("long")
        .alias("play_count"),
        _first_available(media_stats_df, "payload.play_rate", "play_rate")
        .cast("double")
        .alias("play_rate"),
        (_first_available(media_stats_df, "payload.hours_watched", "hours_watched") * F.lit(3600.0))
        .cast("double")
        .alias("total_watch_time"),
        _first_available(media_stats_df, "payload.engagement", "engagement")
        .cast("double")
        .alias("watched_percent"),
    ).where(F.col("media_id").isNotNull())


def empty_dim_visitor(spark: SparkSession) -> DataFrame:
    schema = StructType(
        [
            StructField("visitor_id", StringType(), True),
            StructField("ip_address", StringType(), True),
            StructField("country", StringType(), True),
        ]
    )
    return spark.createDataFrame([], schema)


def transform_raw_to_curated(spark: SparkSession, raw_root: Path, curated_root: Path) -> None:
    media_path = raw_root / "wistia" / "media_stats"
    metadata_path = raw_root / "wistia" / "media_metadata"
    visitor_path = raw_root / "wistia" / "visitor_stats"
    event_path = raw_root / "wistia" / "event_stats"

    media_df = _read_json_if_exists(spark, media_path)
    metadata_df = _read_json_if_exists(spark, metadata_path)
    visitor_df = _read_json_if_exists(spark, visitor_path)
    event_df = _read_json_if_exists(spark, event_path)

    curated_root.mkdir(parents=True, exist_ok=True)

    if metadata_df is not None:
        build_dim_media(metadata_df).write.mode("overwrite").parquet(str(curated_root / "dim_media"))
    elif media_df is not None:
        build_dim_media(media_df).write.mode("overwrite").parquet(str(curated_root / "dim_media"))

    fact_frames: list[DataFrame] = []
    if media_df is not None:
        fact_frames.append(build_fact_media_stats(media_df))
    visitor_dim_frames: list[DataFrame] = []
    if visitor_df is not None:
        visitor_dim_frames.append(normalize_visitor_records(visitor_df))
    if event_df is not None:
        normalized_events = normalize_payload_records(event_df)
        visitor_dim_frames.append(normalized_events)
        fact_frames.append(build_fact_event_engagement(normalized_events))

    if visitor_dim_frames:
        visitor_dim_df = visitor_dim_frames[0]
        for extra_visitor_df in visitor_dim_frames[1:]:
            visitor_dim_df = visitor_dim_df.unionByName(extra_visitor_df, allowMissingColumns=True)
        build_dim_visitor(visitor_dim_df).write.mode("overwrite").parquet(
            str(curated_root / "dim_visitor")
        )
    else:
        empty_dim_visitor(spark).write.mode("overwrite").parquet(str(curated_root / "dim_visitor"))

    if visitor_df is not None:
        normalized_visitors = normalize_visitor_records(visitor_df)
        fact_frames.append(build_fact_media_engagement(normalized_visitors))

    if fact_frames:
        fact_df = fact_frames[0]
        for extra_df in fact_frames[1:]:
            fact_df = fact_df.unionByName(extra_df, allowMissingColumns=True)
        fact_df.write.mode("overwrite").partitionBy("date").parquet(
            str(curated_root / "fact_media_engagement")
        )
