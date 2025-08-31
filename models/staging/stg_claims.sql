SELECT
    claim_id,
    member_id,
    company_id,
    claim_date::DATE as claim_date,
    claim_type,
    provider_name,
    diagnosis_code,
    diagnosis_description,
    claim_amount::DECIMAL(10,2) as claim_amount,
    paid_amount::DECIMAL(10,2) as paid_amount,
    member_responsibility::DECIMAL(10,2) as member_responsibility,
    claim_status,
    service_date::DATE as service_date,
    YEAR(claim_date) as claim_year,
    MONTH(claim_date) as claim_month,
    CURRENT_TIMESTAMP() as loaded_at
FROM {{ ref('claims') }}