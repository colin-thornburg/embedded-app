"""
Quick metrics components for the Insurance Portal
Displays key statistics and KPIs in the sidebar
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import logging

from utils.mcp_client import mcp_query_metrics, is_mcp_available
from utils.security import get_company_filter

logger = logging.getLogger(__name__)

def render_quick_stats():
    """Render quick stats sidebar with key metrics"""

    user_context = st.session_state.get('user_context', {})

    # User info card
    render_user_info_card(user_context)

    st.markdown("---")

    # Key metrics
    render_key_metrics()

    st.markdown("---")

    # Plan information
    render_plan_info(user_context)

def render_user_info_card(user_context: Dict[str, Any]):
    """Display user information card"""

    with st.container():
        st.markdown(f"""
        **👤 {user_context.get('first_name', 'User')} {user_context.get('last_name', '')}**

        📧 {user_context.get('email', 'N/A')}
        🏢 {user_context.get('department', 'N/A')}
        {"👑 Primary Member" if user_context.get('is_primary') else "👥 Dependent"}
        """)

def render_key_metrics():
    """Display key insurance metrics"""

    st.subheader("🎯 Key Metrics")

    # Try to load real data
    try:
        metrics_data = load_quick_metrics()

        if metrics_data:
            # Deductible Met
            deductible_met = metrics_data.get('deductible_met', 0)
            st.metric(
                label="💰 Deductible Met",
                value=f"${deductible_met:,.2f}",
                help="Amount of deductible you've met this year"
            )

            # Out of Pocket Spent
            oop_spent = metrics_data.get('oop_spent', 0)
            st.metric(
                label="💳 Out-of-Pocket",
                value=f"${oop_spent:,.2f}",
                help="Total out-of-pocket spending this year"
            )

            # Claims by Type
            claims_by_type = metrics_data.get('claims_by_type', 0)
            st.metric(
                label="📋 Claims by Type",
                value=f"{claims_by_type:,.0f}",
                help="Claims breakdown by type this year"
            )

        else:
            # Fallback display
            render_fallback_metrics()

    except Exception as e:
        logger.error(f"Error loading quick metrics: {e}")
        render_fallback_metrics()

def render_fallback_metrics():
    """Display fallback metrics when data can't be loaded"""

    st.info("📊 Connect to view your metrics")

    st.metric(
        label="💰 Deductible Met",
        value="--",
        help="Amount of deductible you've met this year"
    )

    st.metric(
        label="💳 Out-of-Pocket",
        value="--",
        help="Total out-of-pocket spending this year"
    )

    st.metric(
        label="📋 Total Claims",
        value="--",
        help="Number of claims this year"
    )

def load_quick_metrics() -> Optional[Dict[str, Any]]:
    """Load key metrics for the quick stats"""

    if not is_mcp_available():
        return None

    try:
        # Get company filter for security
        company_id = get_company_filter()

        # Query for key metrics
        query_args = {
            "metrics": ["deductible_met", "oop_spent", "claims_by_type"],
            "where": f"{{{{ Dimension('company_id') }}}} = {company_id}"
        }

        # Execute query
        raw_result = mcp_query_metrics(query_args)

        # Parse result
        if isinstance(raw_result, str):
            import json
            result = json.loads(raw_result)
        else:
            result = raw_result

        if result and isinstance(result, list) and len(result) > 0:
            # Convert keys to lowercase and clean up
            metrics = {}
            first_row = result[0]

            for key, value in first_row.items():
                clean_key = key.lower().replace(' ', '_')
                metrics[clean_key] = value or 0

            return metrics

    except Exception as e:
        logger.error(f"Failed to load quick metrics: {e}")

    return None

def render_plan_info(user_context: Dict[str, Any]):
    """Display plan information"""

    st.subheader("📋 Plan Info")

    plan_id = user_context.get('plan_id')
    if plan_id:
        # Try to load plan details
        plan_info = load_plan_info(plan_id)

        if plan_info:
            st.markdown(f"""
            **Plan Type:** {plan_info.get('plan_type', 'N/A')}
            **Deductible:** ${plan_info.get('deductible', 0):,.2f}
            **OOP Max:** ${plan_info.get('oop_max', 0):,.2f}
            """)
        else:
            st.markdown(f"**Plan ID:** {plan_id}")
    else:
        st.info("Plan information not available")

def load_plan_info(plan_id: int) -> Optional[Dict[str, Any]]:
    """Load plan information from CSV data"""

    try:
        # Load plans data
        from pathlib import Path
        base_path = Path(__file__).parent.parent.parent / "seeds"
        plans_df = pd.read_csv(base_path / "plans.csv")

        # Find plan
        plan_row = plans_df[plans_df['plan_id'] == plan_id]
        if not plan_row.empty:
            plan = plan_row.iloc[0]
            return {
                'plan_type': plan.get('plan_type', 'N/A'),
                'deductible': plan.get('annual_deductible_individual', 0),
                'oop_max': plan.get('oop_max_individual', 0),
                'premium': plan.get('premium_monthly_employee', 0)
            }

    except Exception as e:
        logger.error(f"Failed to load plan info: {e}")

    return None

def render_metric_card(title: str, value: str, help_text: str = "", delta: str = None):
    """Render a custom metric card"""

    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{title}**")
            st.markdown(f"### {value}")
            if help_text:
                st.caption(help_text)

        if delta:
            with col2:
                st.markdown(f"**{delta}**")

def render_progress_bar(current: float, maximum: float, label: str):
    """Render a progress bar for metrics like deductible progress"""

    if maximum > 0:
        progress = min(current / maximum, 1.0)
        st.progress(progress)
        st.caption(f"{label}: ${current:,.2f} / ${maximum:,.2f}")
    else:
        st.caption(f"{label}: ${current:,.2f}")

# Cache for metrics to avoid repeated queries
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_metrics(company_id: int) -> Optional[Dict[str, Any]]:
    """Get cached metrics data"""
    try:
        return load_quick_metrics()
    except Exception:
        return None