SELECT
    prescription_id,
    drug_name,
    drug_category,
    formulary_tier,
    generic_available,
    typical_copay_tier1,
    typical_copay_tier2,
    typical_copay_tier3,
    typical_copay_tier4,
    prior_auth_required,
    CURRENT_TIMESTAMP() as loaded_at
FROM {{ ref('prescriptions') }}