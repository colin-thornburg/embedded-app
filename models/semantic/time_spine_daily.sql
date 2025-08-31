{{ config(materialized='table') }}

WITH date_spine AS (
  SELECT 
    dateadd(
      day, 
      seq4(), 
      '2020-01-01'::date
    ) as date_day
  FROM table(generator(rowcount => 3653)) -- ~10 years of dates (2020-2030)
)

SELECT 
  date_day
FROM date_spine
WHERE date_day <= current_date() + interval '2 years'
ORDER BY date_day