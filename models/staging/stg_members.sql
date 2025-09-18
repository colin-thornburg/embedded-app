SELECT
    member_id,
    company_id,
    employee_id,
    first_name,
    last_name,
    email,
    date_of_birth,
    gender,
    plan_id,
    enrollment_date,
    is_primary,
    dependent_of,
    department,
    annual_salary,
    CURRENT_TIMESTAMP as loaded_at
FROM {{ ref('members') }}