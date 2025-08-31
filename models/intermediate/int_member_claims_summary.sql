WITH member_claims AS (
    SELECT
        m.member_id,
        m.company_id,
        m.first_name,
        m.last_name,
        m.plan_id,
        c.claim_id,
        c.claim_date,
        c.claim_type,
        c.claim_amount,
        c.paid_amount,
        c.member_responsibility,
        c.claim_year,
        c.claim_month
    FROM {{ ref('stg_members') }} m
    LEFT JOIN {{ ref('stg_claims') }} c
        ON m.member_id = c.member_id
),

ytd_calculations AS (
    SELECT
        member_id,
        company_id,
        first_name,
        last_name,
        plan_id,
        COUNT(claim_id) as total_claims_count,
        SUM(claim_amount) as total_claims_amount,
        SUM(paid_amount) as total_paid_amount,
        SUM(member_responsibility) as total_member_responsibility,
        SUM(CASE 
            WHEN claim_year = YEAR(CURRENT_DATE()) 
            THEN member_responsibility 
            ELSE 0 
        END) as ytd_member_responsibility,
        SUM(CASE 
            WHEN claim_year = YEAR(CURRENT_DATE()) 
            THEN claim_amount 
            ELSE 0 
        END) as ytd_claims_amount
    FROM member_claims
    GROUP BY 1, 2, 3, 4, 5
)

SELECT * FROM ytd_calculations