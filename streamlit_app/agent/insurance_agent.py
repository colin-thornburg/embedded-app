"""
Insurance AI Agent
Handles natural language queries and converts them to semantic layer queries
"""
import streamlit as st
import openai
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from utils.mcp_client import (
    mcp_list_metrics,
    mcp_get_dimensions,
    mcp_query_metrics,
    is_mcp_available
)
from utils.semantic_layer import DbtSemanticLayer
from utils.security import get_company_filter, sanitize_user_input

logger = logging.getLogger(__name__)

class InsuranceAgent:
    """AI Agent for processing insurance-related queries"""

    def __init__(self):
        """Initialize the agent with OpenAI and available metrics"""
        # Get OpenAI API key from secrets or environment
        api_key = None
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            pass

        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("No OpenAI API key found. Agent will have limited functionality.")

        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        self.available_metrics = self._load_available_metrics()
        self.available_dimensions = self._load_available_dimensions()
        self.semantic_layer = DbtSemanticLayer()

    def _load_available_metrics(self) -> List[Dict]:
        """Load available metrics from MCP server"""
        try:
            if is_mcp_available():
                return mcp_list_metrics()
            else:
                logger.warning("MCP not available, using fallback metrics")
                return self._get_fallback_metrics()
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return self._get_fallback_metrics()

    def _load_available_dimensions(self) -> List[Dict]:
        """Load available dimensions from MCP server"""
        try:
            if is_mcp_available() and self.available_metrics:
                metric_names = [m['name'] for m in self.available_metrics]
                return mcp_get_dimensions(metric_names)
            else:
                return self._get_fallback_dimensions()
        except Exception as e:
            logger.error(f"Failed to load dimensions: {e}")
            return self._get_fallback_dimensions()

    def _get_fallback_metrics(self) -> List[Dict]:
        """Fallback metrics when MCP is unavailable"""
        return [
            {"name": "total_claims", "description": "Total claim amount", "type": "SIMPLE"},
            {"name": "paid_amount", "description": "Amount paid by insurance", "type": "SIMPLE"},
            {"name": "member_responsibility", "description": "Member out-of-pocket amount", "type": "SIMPLE"},
            {"name": "claims_by_type", "description": "Claims breakdown by type", "type": "SIMPLE"},
            {"name": "deductible_met", "description": "YTD deductible met", "type": "SIMPLE"},
            {"name": "oop_spent", "description": "YTD out-of-pocket spent", "type": "SIMPLE"},
        ]

    def _get_fallback_dimensions(self) -> List[Dict]:
        """Fallback dimensions when MCP is unavailable"""
        return [
            {"name": "claim_date", "type": "time"},
            {"name": "claim_type", "type": "categorical"},
            {"name": "claim_status", "type": "categorical"},
            {"name": "provider_name", "type": "categorical"},
            {"name": "department", "type": "categorical"},
            {"name": "plan_type", "type": "categorical"},
        ]

    def process_query(self, user_question: str) -> Dict[str, Any]:
        """
        Process a natural language query and return structured response
        """

        # Sanitize input
        user_question = sanitize_user_input(user_question)

        # Check if OpenAI client is available
        if not self.client:
            return {
                "type": "error",
                "message": "AI functionality is not available. Please configure your OpenAI API key.",
                "data": None
            }

        try:
            # Get user context for personalization
            user_context = st.session_state.get('user_context', {})

            # Create system prompt with available metrics and user context
            system_prompt = self._create_system_prompt(user_context)

            # Create function schema for query_metrics
            function_schema = self._create_function_schema()

            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                functions=[function_schema],
                function_call="auto",
                temperature=0.1
            )

            return self._process_openai_response(response, user_question)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "type": "error",
                "message": f"I'm sorry, I encountered an error processing your question: {str(e)}",
                "data": None
            }

    def _create_system_prompt(self, user_context: Dict) -> str:
        """Create comprehensive system prompt"""

        metrics_list = "\\n".join([f"- {m['name']}: {m['description']}" for m in self.available_metrics])
        dimensions_list = "\\n".join([f"- {d['name']} ({d['type']})" for d in self.available_dimensions])

        return f"""You are an AI assistant for {user_context.get('company_name', 'the company')} insurance portal.

USER CONTEXT:
- Name: {user_context.get('first_name')} {user_context.get('last_name')}
- Company: {user_context.get('company_name')}
- Department: {user_context.get('department')}
- Plan Type: Primary member: {user_context.get('is_primary')}

AVAILABLE METRICS:
{metrics_list}

AVAILABLE DIMENSIONS:
{dimensions_list}

GUIDELINES:
1. Help users understand their insurance claims, benefits, and spending
2. When users ask questions, determine which metrics and dimensions are needed
3. Use the query_metrics function to fetch data from the semantic layer
4. Provide clear, friendly explanations of the results
5. For time-based queries, default to current year unless specified
6. NEVER mention internal IDs (company_id, member_id) in responses
7. If a query is ambiguous, ask clarifying questions
8. Format monetary amounts with $ and proper formatting

COMMON QUERY PATTERNS:
- "How much of my deductible have I met?" → deductible_met metric
- "Show my claims this year" → claims_by_type with current year filter
- "What's my out-of-pocket spending?" → oop_spent metric
- "Claims by type" → claims_by_type grouped by claim_type
- "Last month's claims" → metrics with claim_date dimension

Always be helpful and explain insurance terms when needed."""

    def _create_function_schema(self) -> Dict:
        """Create function schema for OpenAI function calling"""

        return {
            "name": "query_metrics",
            "description": "Query the insurance semantic layer for metrics and data",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of metric names to query"
                    },
                    "group_by": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "grain": {"type": "string", "enum": ["day", "week", "month", "quarter", "year"]}
                            }
                        },
                        "description": "Dimensions to group by with optional time grain"
                    },
                    "where": {
                        "type": "string",
                        "description": "Additional filters in dbt Semantic Layer format"
                    },
                    "order_by": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "descending": {"type": "boolean"}
                            }
                        },
                        "description": "Sort order for results"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return"
                    }
                },
                "required": ["metrics"]
            }
        }

    def _process_openai_response(self, response, user_question: str) -> Dict[str, Any]:
        """Process OpenAI response and execute function calls if needed"""

        message = response.choices[0].message

        # Check if OpenAI wants to call a function
        if hasattr(message, 'function_call') and message.function_call:
            function_call = message.function_call

            if function_call.name == "query_metrics":
                try:
                    # Parse function arguments
                    args = json.loads(function_call.arguments)

                    # Execute the query
                    query_result = self._execute_metrics_query(args)

                    # Generate response based on results
                    return self._generate_response_from_data(query_result, user_question, args)

                except Exception as e:
                    logger.error(f"Error executing function call: {e}")
                    return {
                        "type": "error",
                        "message": f"I had trouble retrieving that data: {str(e)}",
                        "data": None
                    }

        # If no function call, return the direct response
        return {
            "type": "text",
            "message": message.content,
            "data": None
        }

    def _execute_metrics_query(self, query_args: Dict) -> Any:
        """Execute metrics query with proper security filters"""

        # Inject company filter for security
        company_id = get_company_filter()

        # Add company filter to where clause
        existing_where = query_args.get('where', '')
        company_filter = f"{{{{ Dimension('company_id') }}}} = {company_id}"

        if existing_where:
            query_args['where'] = f"({existing_where}) AND {company_filter}"
        else:
            query_args['where'] = company_filter

        # Execute query via semantic layer (more reliable than MCP)
        logger.info(f"Executing metrics query: {query_args}")
        
        try:
            # Use semantic layer instead of MCP for better reliability
            df = self.semantic_layer.query_metrics(
                metrics=query_args.get('metrics', []),
                group_by=query_args.get('group_by'),
                where=query_args.get('where'),
                order_by=query_args.get('order_by'),
                limit=query_args.get('limit')
            )
            
            # Convert DataFrame to list of dicts for JSON serialization
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Semantic layer query failed, falling back to MCP: {e}")
            # Fallback to MCP if semantic layer fails
            raw_result = mcp_query_metrics(query_args)
            if isinstance(raw_result, str):
                return json.loads(raw_result)
            return raw_result

    def _generate_response_from_data(self, data: Any, user_question: str, query_args: Dict) -> Dict[str, Any]:
        """Generate user-friendly response from query data"""

        if not data:
            return {
                "type": "text",
                "message": "I didn't find any data for your query. This might be because there are no records matching your criteria.",
                "data": None
            }

        # Determine response type based on data structure
        if isinstance(data, list) and len(data) == 1 and len(query_args.get('metrics', [])) == 1:
            # Single metric value
            metric_name = query_args['metrics'][0]
            value = list(data[0].values())[0] if data[0] else 0

            return {
                "type": "metric",
                "message": self._format_single_metric_response(metric_name, value, user_question),
                "data": {"metric": metric_name, "value": value}
            }

        elif isinstance(data, list) and len(data) > 1:
            # Multiple rows - table/chart data
            return {
                "type": "data",
                "message": self._format_data_response(data, query_args, user_question),
                "data": data
            }

        else:
            # Fallback
            return {
                "type": "data",
                "message": "Here's what I found:",
                "data": data
            }

    def _format_single_metric_response(self, metric_name: str, value: Any, question: str) -> str:
        """Format response for single metric queries"""

        # Format monetary values
        if isinstance(value, (int, float)) and metric_name in ['deductible_met', 'oop_spent', 'total_claims', 'paid_amount', 'member_responsibility']:
            formatted_value = f"${value:,.2f}"
        else:
            formatted_value = str(value)

        # Create contextual responses
        if 'deductible' in question.lower():
            return f"You have met **{formatted_value}** of your deductible so far this year."
        elif 'out-of-pocket' in question.lower() or 'oop' in question.lower():
            return f"Your out-of-pocket spending this year is **{formatted_value}**."
        elif 'claims' in question.lower() and 'count' in metric_name:
            return f"You have **{formatted_value}** claims on record."
        else:
            return f"Your **{metric_name.replace('_', ' ').title()}** is **{formatted_value}**."

    def _format_data_response(self, data: List[Dict], query_args: Dict, question: str) -> str:
        """Format response for multi-row data"""

        metrics = query_args.get('metrics', [])
        group_by = query_args.get('group_by', [])

        if group_by:
            group_names = [g['name'] for g in group_by]
            return f"Here's your **{', '.join(metrics)}** broken down by **{', '.join(group_names)}**:"
        else:
            return f"Here are your **{', '.join(metrics)}** results:"