SELECT
    c.claim_id,
    c.member_id,
    c.company_id,
    c.claim_date,
    c.claim_type,
    c.provider_name,
    c.diagnosis_code,
    c.diagnosis_description,
    c.claim_amount,
    c.paid_amount,
    c.member_responsibility,
    c.claim_status,
    c.service_date,
    c.claim_year,
    c.claim_month,
    m.plan_id,
    m.department,
    p.plan_type
FROM {{ ref('stg_claims') }} c
LEFT JOIN {{ ref('stg_members') }} m
    ON c.member_id = m.member_id
LEFT JOIN {{ ref('stg_plans') }} p
    ON m.plan_id = p.plan_id