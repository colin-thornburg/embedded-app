"""
Security utilities for the Insurance Portal
Handles session validation and company data isolation
"""
import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_session() -> bool:
    """
    Validate that the current session is still valid
    Returns True if session is valid, False if expired/invalid
    """

    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        return False

    # Check if user context exists
    user_context = st.session_state.get('user_context', {})
    if not user_context:
        logger.warning("No user context found in session")
        return False

    # Check session timeout
    session_timeout = user_context.get('session_timeout')
    if session_timeout and datetime.now() > session_timeout:
        logger.info(f"Session expired for user {user_context.get('email')}")
        return False

    # Validate required fields
    required_fields = ['member_id', 'company_id', 'email']
    for field in required_fields:
        if not user_context.get(field):
            logger.warning(f"Missing required field {field} in user context")
            return False

    return True

def get_company_filter():
    """
    Get the company filter for secure queries
    This is the CRITICAL security function - every query must use this
    """

    user_context = st.session_state.get('user_context', {})
    company_id = user_context.get('company_id')

    if not company_id:
        raise ValueError("No company_id found in session - potential security breach!")

    logger.debug(f"Applied company filter: company_id={company_id}")
    return company_id

def get_member_filter():
    """
    Get the member filter for user-specific queries
    """

    user_context = st.session_state.get('user_context', {})
    member_id = user_context.get('member_id')

    if not member_id:
        raise ValueError("No member_id found in session")

    return member_id

def validate_query_filters(query_filters: dict) -> dict:
    """
    Validate and inject required security filters into queries
    This ensures every query is properly scoped to the user's company
    """

    # Always inject company filter
    company_id = get_company_filter()
    query_filters['company_id'] = company_id

    # Log for audit trail
    user_context = st.session_state.get('user_context', {})
    logger.info(f"Query executed by {user_context.get('email')} for company {company_id}")

    return query_filters

def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    """

    if not user_input:
        return ""

    # Remove potentially dangerous characters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    sanitized = user_input

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()

def mask_sensitive_data(data: dict) -> dict:
    """
    Mask sensitive data in responses
    Never expose internal IDs or sensitive information to users
    """

    sensitive_fields = ['company_id', 'member_id', 'employee_id']
    masked_data = data.copy()

    for field in sensitive_fields:
        if field in masked_data:
            # Remove entirely rather than mask
            del masked_data[field]

    return masked_data