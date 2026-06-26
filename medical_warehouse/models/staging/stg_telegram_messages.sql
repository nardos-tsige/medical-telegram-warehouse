-- staging/stg_telegram_messages.sql
-- Clean and standardize raw telegram messages

WITH source AS (
    SELECT
        message_id,
        channel_name,
        message_date,
        message_text,
        has_media,
        image_path,
        views,
        forwards,
        scraped_at
    FROM raw.telegram_messages
)

SELECT
    message_id,
    channel_name,
    message_date,
    DATE(message_date) as message_date_only,
    EXTRACT(HOUR FROM message_date) as message_hour,
    EXTRACT(DOW FROM message_date) as day_of_week,
    message_text,
    LENGTH(message_text) as message_length,
    has_media,
    image_path,
    COALESCE(views, 0) as views,
    COALESCE(forwards, 0) as forwards,
    scraped_at
FROM source
WHERE message_text IS NOT NULL 
  AND LENGTH(TRIM(message_text)) > 0