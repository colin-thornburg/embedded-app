SELECT
    provider_id,
    provider_name,
    specialty,
    address,
    city,
    state,
    zip,
    phone,
    network_status_techcorp,
    network_status_retailplus,
    network_status_manufacturingco,
    accepting_new_patients,
    quality_rating,
    CURRENT_TIMESTAMP() as loaded_at
FROM {{ ref('providers') }}