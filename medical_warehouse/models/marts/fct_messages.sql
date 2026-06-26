-- marts/fct_messages.sql
-- Fact table for message analytics

SELECT
    s.message_id,
    c.channel_key,
    d.date_key,
    s.message_date,
    s.message_text,
    s.message_length,
    s.views,
    s.forwards,
    s.has_media,
    s.image_path
FROM staging.stg_telegram_messages s
LEFT JOIN marts.dim_channels c ON s.channel_name = c.channel_name
LEFT JOIN marts.dim_dates d ON DATE(s.message_date) = d.full_date