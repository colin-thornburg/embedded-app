# Technical Implementation Guide for AI Agent

## Architecture Overview
Build a multi-tenant insurance portal using:
- **Frontend**: Streamlit for web UI
- **Query Processing**: OpenAI GPT-4 with function calling
- **Data Layer**: dbt Semantic Layer accessed via MCP (Model Context Protocol)
- **Security**: Row-level security through company_id filter injection

## Critical Implementation Principles

### Security First
- **EVERY query** must have `company_id` filter injected before reaching the semantic layer
- Never trust client-side filtering - enforce at MCP server level
- Store company context in server-side session only
- Log all queries with company context for audit trail

### Data Flow
```
User Query → OpenAI (determine metrics) → MCP Server (inject filters) → dbt GraphQL → Response
```

## Step 1: MCP Server Implementation

### Framework & Dependencies
Use the dbt-MCP package from the official repo: https://github.com/dbt-labs/dbt-mcp

**Key Documentation**:
- MCP Protocol Spec: https://modelcontextprotocol.io/docs
- dbt-MCP README: https://github.com/dbt-labs/dbt-mcp/blob/main/README.md
- Example OpenAI Agent: https://github.com/dbt-labs/dbt-mcp/tree/main/examples/openai_agent

### Implementation Approach
1. **Install dbt-mcp package** - Follow the official installation guide
2. **Create custom middleware** for filter injection:
   - Intercept all incoming queries
   - Extract company_id from request context
   - Append to filters object before GraphQL call
   - This is THE MOST CRITICAL security feature

3. **Configure MCP tools** that expose:
   - `query_metrics` - Main tool for semantic layer queries
   - `list_metrics` - Show available metrics for the company
   - `get_metric_definition` - Return metric metadata

### Environment Variables Required
```
DBT_CLOUD_SERVICE_TOKEN  # From dbt Cloud Account Settings
DBT_CLOUD_ENVIRONMENT_ID  # From dbt Cloud project
DBT_CLOUD_HOST           # Usually https://cloud.getdbt.com
```

### Testing the MCP Server
Before proceeding, verify:
- Server starts and connects to dbt Cloud
- Can query the GraphQL endpoint
- Filters are properly injected (check server logs)

## Step 2: OpenAI Agent Configuration

### Documentation References
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- OpenAI Python SDK: https://github.com/openai/openai-python

### Agent Design Pattern
Implement a **ReAct pattern** (Reasoning + Acting):
1. Understand user intent
2. Determine required metrics/dimensions
3. Call MCP tool with parameters
4. Interpret results
5. Format response appropriately

### System Prompt Engineering
Create a comprehensive system prompt that includes:
- Available metrics from semantic_models.yml
- Valid dimension values
- Company context (name, but NOT the ID)
- Guidelines for handling ambiguous queries
- Instructions to NEVER reveal internal IDs

### Function Schema Definition
Define the `query_metrics` function with:
- `metrics`: array of metric names (from semantic model)
- `dimensions`: array of dimension names
- `filters`: object with additional filters (besides company_id)
- `time_grain`: enum of day/week/month/quarter/year

### Error Handling Strategy
- Catch metric not found errors → suggest similar metrics
- Handle timeout errors → retry with simpler query
- Detect ambiguous queries → ask clarifying questions

## Step 3: Streamlit Application Structure

### Documentation & Resources
- Streamlit Docs: https://docs.streamlit.io
- Session State: https://docs.streamlit.io/library/api-reference/session-state
- Authentication Pattern: https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

### Application Architecture

#### Authentication Module (Simplified)
1. **Simple demo authentication**:
   - Username = any email from members.csv
   - Password = "demo123" for all users
   - On successful login, load member's full context from CSVs
   - Store company_id, member_id, and other context in `st.session_state`

2. **Session Management**:
   - Use Streamlit's session_state for persistence
   - Implement timeout after 30 minutes
   - Clear sensitive data on logout

#### Chat Interface Design
Use Streamlit's chat components:
- `st.chat_message()` for message display
- `st.chat_input()` for user input
- Store conversation in `st.session_state.messages[]`

#### Data Visualization Strategy
When agent returns data:
- Tabular data → `st.dataframe()` with sorting/filtering
- Time series → Plotly charts via `st.plotly_chart()`
- Single metrics → `st.metric()` with delta values
- Multiple metrics → `st.columns()` with metric cards

### Component Organization
```
streamlit_app/
├── app.py                 # Main entry point
├── auth/
│   └── authenticator.py  # Handle login and company detection
├── agent/
│   └── insurance_agent.py # OpenAI + MCP integration
├── components/
│   ├── chat.py           # Chat interface
│   └── metrics.py        # Metric display components
└── utils/
    ├── mcp_client.py     # MCP server communication
    └── security.py       # Filter validation
```

## Step 4: dbt Semantic Layer Configuration

### Documentation
- Semantic Layer Setup: https://docs.getdbt.com/docs/build/semantic-models/semantic-models
- GraphQL API: https://docs.getdbt.com/docs/dbt-cloud-apis/sl-graphql
- MetricFlow: https://docs.getdbt.com/docs/build/metricflow

### Required Configurations

1. **Update semantic_models.yml**:
   - Ensure every model has `company_id` as a dimension
   - Add `member_id` dimension where needed
   - Define time dimensions with proper granularity

2. **Create Calculated Metrics**:
   - YTD metrics using time dimension filters
   - Deductible remaining (deductible - YTD spending)
   - Percentage of OOP max reached

3. **Test Semantic Layer Access**:
   - Use dbt Cloud UI to test queries
   - Verify GraphQL endpoint responds
   - Check that filters work correctly

## Step 5: Security Implementation

### Multi-Tenancy Enforcement

1. **MCP Server Level** (Primary Defense):
   - Middleware to inject company_id on EVERY request
   - Reject queries without proper context
   - Log all access attempts

2. **Application Level** (Secondary):
   - Validate user session before queries
   - Sanitize user inputs
   - Rate limiting per user/company

3. **Semantic Layer Level** (Final):
   - Use dbt's access controls
   - Implement row-level policies if supported

### Query Validation Pattern
```python
# Conceptual validation flow
def validate_query(query_params, user_context):
    # 1. Ensure company_id is present
    assert user_context.get('company_id'), "No company context"
    
    # 2. Check metrics are allowed
    allowed_metrics = ['total_claims', 'paid_amount', ...]
    assert all(m in allowed_metrics for m in query_params['metrics'])
    
    # 3. Inject filters
    query_params['filters']['company_id'] = user_context['company_id']
    
    return query_params
```

## Step 6: Integration Testing Approach

### Test Scenarios to Implement

1. **Data Isolation Test**:
   - Login as user from Company A
   - Run query for all claims
   - Login as user from Company B  
   - Run same query
   - Verify ZERO overlap in results

2. **Filter Injection Test**:
   - Monitor MCP server logs
   - Verify every GraphQL query has company_id filter
   - Test with direct API calls to ensure filters can't be bypassed

3. **Metric Access Test**:
   - Query each available metric
   - Verify calculations are correct
   - Test with different time granularities

### Debugging Tools
- MCP Server logs - Check filter injection
- dbt Cloud Query History - Verify GraphQL queries
- Browser DevTools - Monitor API calls
- Streamlit debug mode - `streamlit run app.py --logger.level=debug`

## Step 7: Error Handling & User Experience

### Common Error Scenarios

1. **Metric Not Available**: 
   - Agent should suggest similar metrics
   - Provide list of available options

2. **Ambiguous Time References**:
   - "Last month" → Clarify calendar vs rolling month
   - "This year" → Confirm current year vs last 12 months

3. **No Data Found**:
   - Explain why (e.g., no claims in period)
   - Suggest adjusting query parameters

4. **Timeout/Rate Limits**:
   - Implement exponential backoff
   - Cache frequent queries
   - Show loading states

## Step 8: Performance Optimization

### Caching Strategy
- Use Redis or in-memory cache for:
  - Company metadata (logos, colors)
  - Frequently used metrics
  - Recent query results (5-minute TTL)

### Query Optimization
- Start with aggregated metrics before detailed data
- Limit default time ranges to last 12 months
- Use pagination for large result sets

### Connection Management
- Implement connection pooling for MCP server
- Reuse OpenAI client instances
- Set appropriate timeouts (10s for complex queries)

## Critical Implementation Checklist

- [ ] MCP server successfully connects to dbt Cloud GraphQL endpoint
- [ ] Company_id filter is injected on EVERY query (verify in logs)
- [ ] OpenAI agent correctly identifies required metrics from user questions
- [ ] Session state properly maintains user context across interactions
- [ ] Different company users see completely isolated data
- [ ] Error messages don't expose internal IDs or sensitive information
- [ ] Query response time is under 5 seconds for standard queries
- [ ] Logout properly clears all session data

## Debugging Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| No data returned | MCP server logs | Verify filter format matches schema |
| Wrong company data | Session state | Check company_id in context |
| Slow queries | dbt Cloud metrics | Add materialization to models |
| Function calling fails | OpenAI response | Simplify function schema |
| GraphQL errors | dbt Cloud API logs | Check service token permissions |

## Documentation Links Summary

**Essential Reading**:
1. dbt MCP: https://github.com/dbt-labs/dbt-mcp
2. dbt Semantic Layer GraphQL: https://docs.getdbt.com/docs/dbt-cloud-apis/sl-graphql
3. OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
4. Streamlit Session State: https://docs.streamlit.io/library/api-reference/session-state

**Reference Examples**:
1. MCP OpenAI Agent: https://github.com/dbt-labs/dbt-mcp/tree/main/examples/openai_agent
2. Streamlit Auth Pattern: https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

## Final Notes for AI Agent

Focus on getting the security model right first - the company_id filter injection is non-negotiable. Start with a simple query ("show all claims") and verify data isolation works perfectly before adding complex features. Use the MCP server logs extensively during development to ensure every query is properly filtered.

Remember: This is a multi-tenant system where data isolation is critical. When in doubt, be more restrictive with data access rather than less.