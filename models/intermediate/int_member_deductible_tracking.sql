WITH plan_details AS (
    SELECT
        plan_id,
        company_id,
        annual_deductible_individual,
        annual_deductible_family,
        oop_max_individual,
        oop_max_family
    FROM {{ ref('stg_plans') }}
),

member_ytd_spending AS (
    SELECT
        m.member_id,
        m.company_id,
        m.plan_id,
        m.is_primary,
        SUM(CASE
            WHEN c.claim_year = YEAR(CURRENT_DATE())
            THEN c.member_responsibility
            ELSE 0
        END) as ytd_member_spending,
        SUM(CASE
            WHEN c.claim_year = YEAR(CURRENT_DATE()) 
                AND c.claim_type = 'Medical'
            THEN c.member_responsibility
            ELSE 0
        END) as ytd_deductible_spending
    FROM {{ ref('stg_members') }} m
    LEFT JOIN {{ ref('stg_claims') }} c
        ON m.member_id = c.member_id
    GROUP BY 1, 2, 3, 4
)

SELECT
    m.*,
    p.annual_deductible_individual,
    p.oop_max_individual,
    m.ytd_deductible_spending as deductible_met,
    GREATEST(0, p.annual_deductible_individual - m.ytd_deductible_spending) as deductible_remaining,
    m.ytd_member_spending as oop_spent,
    GREATEST(0, p.oop_max_individual - m.ytd_member_spending) as oop_remaining
FROM member_ytd_spending m
JOIN plan_details p
    ON m.plan_id = p.plan_id