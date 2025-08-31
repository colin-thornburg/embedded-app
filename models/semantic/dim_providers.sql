SELECT
    provider_id,
    provider_name,
    specialty,
    address,
    city,
    state,
    zip,
    phone,
    accepting_new_patients,
    quality_rating,
    company_id,
    network_status,
    is_in_network
FROM {{ ref('int_provider_network') }}