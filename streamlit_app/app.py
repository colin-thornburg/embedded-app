"""
Insurance Portal - Multi-tenant AI Agent
Main Streamlit application entry point
"""
import streamlit as st
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Import our modules
from auth.authenticator import handle_authentication
from components.chat import render_chat_interface
from components.metrics import render_quick_stats
from utils.security import validate_session

# Configure page
st.set_page_config(
    page_title="Insurance Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application logic"""

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Check authentication
    if not st.session_state.authenticated:
        handle_authentication()
        return

    # Validate session is still valid
    if not validate_session():
        st.session_state.authenticated = False
        st.rerun()

    # Main app layout
    render_main_app()

def render_main_app():
    """Render the main authenticated application"""

    # Get user context from session
    user_context = st.session_state.get('user_context', {})
    company_name = user_context.get('company_name', 'Your Company')
    brand_color = user_context.get('brand_color', '#0066cc')

    # Header with company branding
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {brand_color} 0%, {brand_color}88 100%);
                padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🏥 {company_name} Insurance Portal</h1>
        <p style="color: white; opacity: 0.9; margin: 0;">
            Welcome {user_context.get('first_name', 'User')}! Ask questions about your benefits and claims.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Layout: sidebar for quick stats, main area for chat
    col1, col2 = st.columns([1, 3])

    with col1:
        st.header("📊 Quick Stats")
        render_quick_stats()

        # Logout button
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        st.header("💬 Chat with AI Assistant")
        render_chat_interface()

if __name__ == "__main__":
    main()