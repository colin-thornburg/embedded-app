SELECT
    company_id,
    company_name,
    industry,
    employee_count,
    primary_plan_type,
    logo_url,
    brand_color,
    CURRENT_TIMESTAMP() as loaded_at
FROM {{ ref('companies') }}