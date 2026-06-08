-- Athena validation queries for the Wistia Video Analytics project.
-- Database: wistia_video_analytics
-- Tables: dim_media, dim_visitor, fact_media_engagement

USE wistia_video_analytics;

-- 1. Confirm curated table row counts.
SELECT 'dim_media' AS table_name, COUNT(*) AS row_count FROM dim_media
UNION ALL
SELECT 'dim_visitor' AS table_name, COUNT(*) AS row_count FROM dim_visitor
UNION ALL
SELECT 'fact_media_engagement' AS table_name, COUNT(*) AS row_count FROM fact_media_engagement;

-- 2. Confirm the two required Wistia media IDs are present.
SELECT
    media_id,
    title,
    duration,
    created
FROM dim_media
WHERE media_id IN ('gskhw4w4lm', 'v08dlrgr7v')
ORDER BY media_id;

-- 3. Confirm fact table date coverage and partition shape.
SELECT
    MIN(date) AS first_partition_date,
    MAX(date) AS last_partition_date,
    COUNT(DISTINCT date) AS distinct_partition_dates,
    COUNT(*) AS engagement_rows
FROM fact_media_engagement;

-- 4. Media-level engagement summary.
SELECT
    media_id,
    COUNT(*) AS engagement_rows,
    COUNT(DISTINCT visitor_id) AS unique_visitors,
    SUM(COALESCE(play_count, 0)) AS total_plays,
    SUM(COALESCE(seconds_watched, 0)) AS total_seconds_watched,
    AVG(COALESCE(percent_watched, 0)) AS avg_percent_watched
FROM fact_media_engagement
GROUP BY media_id
ORDER BY engagement_rows DESC;

-- 5. Visitor geography summary when country is available.
SELECT
    COALESCE(country, 'unknown') AS country,
    COUNT(*) AS visitors
FROM dim_visitor
GROUP BY COALESCE(country, 'unknown')
ORDER BY visitors DESC
LIMIT 25;

-- 6. Check for missing dimensional joins from the fact table.
SELECT
    f.media_id,
    COUNT(*) AS fact_rows_without_media_dim
FROM fact_media_engagement f
LEFT JOIN dim_media m
    ON f.media_id = m.media_id
WHERE m.media_id IS NULL
GROUP BY f.media_id
ORDER BY fact_rows_without_media_dim DESC;

-- 7. Daily engagement trend for dashboard validation.
SELECT
    date,
    media_id,
    COUNT(*) AS engagement_rows,
    COUNT(DISTINCT visitor_id) AS unique_visitors,
    SUM(COALESCE(play_count, 0)) AS total_plays
FROM fact_media_engagement
GROUP BY date, media_id
ORDER BY date DESC, media_id;
