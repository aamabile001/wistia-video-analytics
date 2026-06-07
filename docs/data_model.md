# Data Model

## dim_media

| Column | Type | Description |
| --- | --- | --- |
| media_id | string | Wistia media identifier or hashed ID |
| title | string | Video title |
| url | string | Video or embed URL |
| channel | string | Marketing channel, if available |
| created_at | timestamp | Media creation timestamp |

## dim_visitor

| Column | Type | Description |
| --- | --- | --- |
| visitor_id | string | Wistia visitor key or visitor ID |
| ip_address | string | Visitor IP address, if available |
| country | string | Visitor country, if available |

## fact_media_engagement

| Column | Type | Description |
| --- | --- | --- |
| media_id | string | Foreign key to `dim_media` |
| visitor_id | string | Foreign key to `dim_visitor` |
| date | date | Engagement date |
| play_count | long | Number of plays |
| play_rate | double | Play rate |
| total_watch_time | double | Watch time |
| watched_percent | double | Percent watched |
