"""
Configuration settings for the Streamlit app
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BASE_DIR.parent

# dbt configuration
DBT_PROJECT_DIR = PROJECT_ROOT
DBT_PROFILES_DIR = os.path.expanduser("~/.dbt")

# Database configuration (will be loaded from environment variables)
DB_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "dbt Analytics Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# App configuration
APP_CONFIG = {
    "title": "Healthcare Analytics Dashboard",
    "description": "Interactive dashboard for healthcare claims and member analytics",
    "version": "1.0.0",
}
