-- marts/dim_channels.sql
-- Channel dimension table

WITH channel_stats AS (
    SELECT
        channel_name,
        MIN(message_date) as first_post_date,
        MAX(message_date) as last_post_date,
        COUNT(*) as total_posts,
        AVG(views) as avg_views,
        AVG(forwards) as avg_forwards
    FROM staging.stg_telegram_messages
    GROUP BY channel_name
)

SELECT
    ROW_NUMBER() OVER (ORDER BY channel_name) as channel_key,
    channel_name,
    first_post_date,
    last_post_date,
    total_posts,
    ROUND(avg_views, 2) as avg_views,
    ROUND(avg_forwards, 2) as avg_forwards,
    CASE
        WHEN LOWER(channel_name) LIKE '%pharma%' OR LOWER(channel_name) LIKE '%drug%' 
            THEN 'Pharmaceutical'
        WHEN LOWER(channel_name) LIKE '%cosmetic%' OR LOWER(channel_name) LIKE '%beauty%' 
            THEN 'Cosmetics'
        ELSE 'Medical'
    END as channel_type,
    CURRENT_TIMESTAMP as updated_at
FROM channel_stats