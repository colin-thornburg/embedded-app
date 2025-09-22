"""
Database connection utilities for the Streamlit app
"""
import streamlit as st
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import pd_writer
from sqlalchemy import create_engine
from config.settings import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

@st.cache_resource
def get_snowflake_connection():
    """Get Snowflake connection using cached resource"""
    try:
        # Check if all required config values are present
        required_keys = ["account", "user", "password", "warehouse", "database", "schema", "role"]
        missing_keys = [key for key in required_keys if not DB_CONFIG.get(key)]
        
        if missing_keys:
            st.warning(f"Missing database configuration: {', '.join(missing_keys)}")
            return None
            
        conn = snowflake.connector.connect(
            account=DB_CONFIG["account"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            warehouse=DB_CONFIG["warehouse"],
            database=DB_CONFIG["database"],
            schema=DB_CONFIG["schema"],
            role=DB_CONFIG["role"]
        )
        return conn
    except Exception as e:
        st.warning(f"Database connection not available: {str(e)}")
        logger.warning(f"Database connection error: {str(e)}")
        return None

@st.cache_resource
def get_sqlalchemy_engine():
    """Get SQLAlchemy engine for pandas operations"""
    try:
        connection_string = (
            f"snowflake://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['account']}/{DB_CONFIG['database']}/{DB_CONFIG['schema']}"
            f"?warehouse={DB_CONFIG['warehouse']}&role={DB_CONFIG['role']}"
        )
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Failed to create SQLAlchemy engine: {str(e)}")
        logger.error(f"SQLAlchemy engine error: {str(e)}")
        return None

def execute_query(query: str, params: dict = None) -> pd.DataFrame:
    """Execute a SQL query and return results as DataFrame"""
    conn = get_snowflake_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        cursor.close()
        return df
        
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        logger.error(f"Query execution error: {str(e)}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def get_dbt_models_info() -> pd.DataFrame:
    """Get information about dbt models from the database"""
    query = """
    SELECT 
        table_name,
        table_type,
        created,
        last_altered
    FROM information_schema.tables 
    WHERE table_schema = 'PUBLIC'
    AND table_name LIKE 'STG_%' 
       OR table_name LIKE 'INT_%' 
       OR table_name LIKE 'DIM_%' 
       OR table_name LIKE 'FCT_%'
    ORDER BY table_name
    """
    return execute_query(query)

def get_metrics_data(metric_name: str, filters: dict = None) -> pd.DataFrame:
    """Get metrics data from dbt semantic models"""
    # This would be replaced with actual dbt semantic layer queries
    # For now, return sample data structure
    base_query = f"""
    SELECT * FROM {metric_name}
    """
    
    if filters:
        where_conditions = []
        for key, value in filters.items():
            if value:
                where_conditions.append(f"{key} = '{value}'")
        
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
    
    return execute_query(base_query)
