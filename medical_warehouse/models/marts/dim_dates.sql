-- marts/dim_dates.sql
-- Date dimension table

WITH date_range AS (
    SELECT DISTINCT DATE(message_date) as date_value
    FROM staging.stg_telegram_messages
    WHERE message_date IS NOT NULL
)

SELECT
    TO_CHAR(date_value, 'YYYYMMDD')::INTEGER as date_key,
    date_value as full_date,
    EXTRACT(YEAR FROM date_value) as year,
    EXTRACT(QUARTER FROM date_value) as quarter,
    EXTRACT(MONTH FROM date_value) as month,
    TO_CHAR(date_value, 'Month') as month_name,
    EXTRACT(WEEK FROM date_value) as week_of_year,
    EXTRACT(DOW FROM date_value) as day_of_week,
    TO_CHAR(date_value, 'Day') as day_name,
    CASE 
        WHEN EXTRACT(DOW FROM date_value) IN (0, 6) THEN TRUE 
        ELSE FALSE 
    END as is_weekend
FROM date_range
ORDER BY date_value