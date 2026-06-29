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
    -- Primary identifiers
    d.message_id,
    c.channel_key,
    d.channel_name,
    
    -- Detection details
    d.detected_class,
    d.confidence,
    d.category,
    d.num_objects,
    
    -- Image path
    d.image_path,
    
    -- Message engagement
    m.views,
    m.forwards,
    m.message_date,
    
    -- Date dimension
    da.date_key,
    
    -- Metadata
    d.detection_timestamp,
    CURRENT_TIMESTAMP as updated_at

FROM image_detections d

-- Join to message fact table
LEFT JOIN marts.fct_messages m ON d.message_id = m.message_id

-- Join to channel dimension
LEFT JOIN marts.dim_channels c ON d.channel_name = c.channel_name

-- Join to date dimension
LEFT JOIN marts.dim_dates da ON DATE(d.detection_timestamp) = da.full_date

WHERE d.message_id IS NOT NULL