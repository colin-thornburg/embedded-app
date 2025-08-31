SELECT
    p.plan_id,
    p.company_id,
    p.plan_name,
    p.plan_type,
    p.annual_deductible_individual,
    p.annual_deductible_family,
    p.oop_max_individual,
    p.oop_max_family,
    p.premium_monthly_employee,
    p.premium_monthly_family,
    p.coinsurance_percentage,
    p.copay_primary,
    p.copay_specialist,
    p.copay_emergency,
    p.prescription_coverage,
    c.company_name
FROM {{ ref('stg_plans') }} p
LEFT JOIN {{ ref('stg_companies') }} c
    ON p.company_id = c.company_id