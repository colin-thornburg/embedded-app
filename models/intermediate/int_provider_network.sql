WITH provider_network_pivot AS (
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
        1001 as company_id,
        network_status_techcorp as network_status
    FROM {{ ref('stg_providers') }}
    
    UNION ALL
    
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
        1002 as company_id,
        network_status_retailplus as network_status
    FROM {{ ref('stg_providers') }}
    
    UNION ALL
    
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
        1003 as company_id,
        network_status_manufacturingco as network_status
    FROM {{ ref('stg_providers') }}
)

SELECT
    *,
    CASE 
        WHEN network_status = 'In-Network' THEN TRUE 
        ELSE FALSE 
    END as is_in_network
FROM provider_network_pivot