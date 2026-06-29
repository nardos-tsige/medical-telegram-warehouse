-- marts/fct_image_detections.sql
-- Fact table for YOLO image detection results

WITH image_detections AS (
    SELECT
        message_id,
        channel_name,
        image_path,
        detected_class,
        confidence,
        category,
        num_objects,
        detection_timestamp
    FROM raw.image_detections
)

SELECT
    d.message_id,
    c.channel_key,
    d.channel_name,
    d.detected_class,
    d.confidence,
    d.category,
    d.num_objects,
    d.image_path,
    m.views,
    m.forwards,
    m.message_date,
    da.date_key,
    d.detection_timestamp,
    CURRENT_TIMESTAMP as updated_at
FROM image_detections d
LEFT JOIN marts.fct_messages m ON d.message_id = m.message_id
LEFT JOIN marts.dim_channels c ON d.channel_name = c.channel_name
LEFT JOIN marts.dim_dates da ON DATE(d.detection_timestamp) = da.full_date
WHERE d.message_id IS NOT NULL