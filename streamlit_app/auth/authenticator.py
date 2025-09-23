"""
Authentication module for the Insurance Portal
Handles demo login with email-based authentication
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import time
from datetime import datetime, timedelta

def load_user_data():
    """Load member and company data from CSV files"""

    # Get path to seed files
    base_path = Path(__file__).parent.parent.parent / "seeds"

    # Load members data
    members_df = pd.read_csv(base_path / "members.csv")
    companies_df = pd.read_csv(base_path / "companies.csv")

    return members_df, companies_df

def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticate user with email and demo password
    Returns user context if successful, None if failed
    """

    # Demo password for all users
    if password != "demo123":
        return None

    try:
        members_df, companies_df = load_user_data()

        # Find user by email
        user_row = members_df[members_df['email'] == email]
        if user_row.empty:
            return None

        user = user_row.iloc[0]

        # Get company info
        company_row = companies_df[companies_df['company_id'] == user['company_id']]
        if company_row.empty:
            return None

        company = company_row.iloc[0]

        # Build user context (critical for security)
        user_context = {
            'member_id': int(user['member_id']),
            'company_id': int(user['company_id']),
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'department': user['department'],
            'plan_id': int(user['plan_id']),
            'is_primary': bool(user['is_primary']),

            # Company branding
            'company_name': company['company_name'],
            'brand_color': company['brand_color'],
            'logo_url': company['logo_url'],
            'industry': company['industry'],

            # Session metadata
            'login_time': datetime.now(),
            'session_timeout': datetime.now() + timedelta(minutes=30)
        }

        return user_context

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def handle_authentication():
    """Render authentication interface"""

    st.markdown("""
    <div style="max-width: 400px; margin: 2rem auto; padding: 2rem;
                border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)

    st.title("🏥 Insurance Portal")
    st.markdown("---")

    # Show demo instructions
    with st.expander("🎯 Demo Instructions", expanded=True):
        st.markdown("""
        **Demo Login Credentials:**
        - **Password:** `demo123` (for all users)
        - **Email:** Use any email from the examples below

        **Sample Users:**
        - `bob.johnson@techcorp.com` (TechCorp)
        - `alice.chen@techcorp.com` (TechCorp)
        - `sam.wilson@retailplus.com` (RetailPlus)
        - `jennifer.martinez@retailplus.com` (RetailPlus)
        """)

    # Login form
    with st.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email", placeholder="user@company.com")
        password = st.text_input("Password", type="password", placeholder="demo123")
        login_button = st.form_submit_button("🔑 Login", use_container_width=True)

        if login_button:
            if not email or not password:
                st.error("Please enter both email and password")
                return

            # Authenticate user
            with st.spinner("Authenticating..."):
                user_context = authenticate_user(email, password)

            if user_context:
                # Store in session state
                st.session_state.authenticated = True
                st.session_state.user_context = user_context

                st.success(f"Welcome {user_context['first_name']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials. Please check your email and password.")

    st.markdown("</div>", unsafe_allow_html=True)

def get_user_context():
    """Get current user context from session state"""
    return st.session_state.get('user_context', {})

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_company_filter():
    """Get company_id filter for secure queries"""
    user_context = get_user_context()
    company_id = user_context.get('company_id')

    if not company_id:
        raise ValueError("No company context found in session")

    return {'company_id': company_id}