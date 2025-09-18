SELECT
    plan_id,
    company_id,
    plan_name,
    plan_type,
    annual_deductible_individual,
    annual_deductible_family,
    oop_max_individual,
    oop_max_family,
    premium_monthly_employee,
    premium_monthly_family,
    coinsurance_percentage,
    copay_primary,
    copay_specialist,
    copay_emergency,
    prescription_coverage,
    CURRENT_TIMESTAMP as loaded_at
FROM {{ ref('plans') }}