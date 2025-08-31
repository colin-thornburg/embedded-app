SELECT
    m.member_id,
    m.company_id,
    m.employee_id,
    m.first_name,
    m.last_name,
    m.email,
    m.date_of_birth,
    m.gender,
    m.plan_id,
    m.enrollment_date,
    m.is_primary,
    m.dependent_of,
    m.department,
    m.annual_salary,
    p.plan_name,
    p.plan_type,
    c.company_name,
    c.industry,
    c.brand_color
FROM {{ ref('stg_members') }} m
LEFT JOIN {{ ref('stg_plans') }} p
    ON m.plan_id = p.plan_id
LEFT JOIN {{ ref('stg_companies') }} c
    ON m.company_id = c.company_id