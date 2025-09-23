# Insurance Portal - AI Agent Implementation Spec

## Core Functionality
Multi-tenant insurance portal where users log in with company email, get authenticated to their company's data only, and ask natural language questions about their insurance claims/benefits. Responses come from dbt Semantic Layer via MCP server.

## Critical Requirements

### Authentication & Security (Simplified Demo)
- Use email from members.csv as username
- Password is "demo123" for all users
- On login, load member's company_id and context from CSV data
- Store company_id and member_id in session state
- **EVERY query must inject company_id filter before hitting semantic layer**
- Never expose company_id or member_id in UI responses

### Query Flow
1. User asks question in natural language
2. OpenAI GPT-4 determines needed metrics/dimensions
3. MCP server adds company_id filter
4. Query hits dbt Semantic Layer GraphQL API  
5. Results formatted and displayed

### Available Metrics (from semantic_models.yml)
- `total_claims` - sum of claim_amount
- `paid_amount` - sum paid by insurance
- `member_responsibility` - member out-of-pocket
- `claim_count` - count of claims
- `deductible_met` - YTD member responsibility
- `oop_spent` - YTD out-of-pocket

### Available Dimensions
- claim_date, claim_type, claim_status
- provider_name, diagnosis_description
- plan_type, department

### Sample User Queries to Support
- "How much of my deductible have I met?"
- "Show my claims from last quarter"
- "What's my out-of-pocket spending this year?"
- "How many claims were approved?"
- "What's my copay for specialists?"

## Data Model Context

### Key Tables (already in dbt project)
- **members**: member_id, company_id, email, plan_id
- **claims**: claim_id, member_id, company_id, amounts
- **plans**: plan_id, deductibles, oop_max, copays
- **companies**: company_id, company_name, brand_color

### Company IDs for Testing
- 1001: TechCorp
- 1002: RetailPlus  
- 1003: ManufacturingCo

## UI Requirements
- Login page with email/password
- Chat interface for questions
- Display tables and charts when appropriate
- Show company branding (logo, colors)
- Quick stats sidebar (deductible status, YTD spending)