"""
Main Streamlit application for dbt Analytics Dashboard
"""
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import sys
import os
from pathlib import Path

# Add the streamlit_app directory to Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import STREAMLIT_CONFIG, APP_CONFIG
from utils.database import get_dbt_models_info, get_metrics_data
from utils.visualizations import (
    create_metric_card, 
    create_dashboard_grid, 
    create_filters_sidebar,
    apply_filters,
    create_data_table
)

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

def main():
    """Main application function"""
    
    # Header
    st.title(f"{APP_CONFIG['title']} 📊")
    st.markdown(f"*{APP_CONFIG['description']}*")
    
    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "Claims Analysis", "Member Analytics", "Plan Analytics", "Data Explorer"],
            icons=["house", "file-medical", "people", "credit-card", "search"],
            menu_icon="cast",
            default_index=0,
        )
    
    # Route to appropriate page
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Claims Analysis":
        show_claims_analysis()
    elif selected == "Member Analytics":
        show_member_analytics()
    elif selected == "Plan Analytics":
        show_plan_analytics()
    elif selected == "Data Explorer":
        show_data_explorer()

def show_dashboard():
    """Main dashboard page"""
    st.header("📊 Executive Dashboard")
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            title="Total Claims",
            value="1,234",
            delta="+12%",
            delta_color="normal"
        )
    
    with col2:
        create_metric_card(
            title="Total Members",
            value="456",
            delta="+5%",
            delta_color="normal"
        )
    
    with col3:
        create_metric_card(
            title="Avg Claim Amount",
            value="$1,234",
            delta="-3%",
            delta_color="inverse"
        )
    
    with col4:
        create_metric_card(
            title="Deductible Met",
            value="78%",
            delta="+8%",
            delta_color="normal"
        )
    
    # Charts section
    st.subheader("📈 Trends")
    
    # Sample data for demonstration
    import plotly.express as px
    import numpy as np
    
    # Claims over time
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    claims_data = pd.DataFrame({
        'date': dates,
        'claims': np.random.randint(10, 50, 30),
        'amount': np.random.randint(1000, 5000, 30)
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(claims_data, x='date', y='claims', title='Claims Count Over Time')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(claims_data, x='date', y='amount', title='Claim Amounts Over Time')
        st.plotly_chart(fig2, use_container_width=True)

def show_claims_analysis():
    """Claims analysis page"""
    st.header("🏥 Claims Analysis")
    
    # Get dbt models info
    models_df = get_dbt_models_info()
    
    if not models_df.empty:
        st.subheader("Available dbt Models")
        st.dataframe(models_df, use_container_width=True)
    else:
        st.warning("No dbt models found. Make sure your dbt project is properly configured and models are built.")
    
    # Sample claims analysis
    st.subheader("Claims by Type")
    
    # Sample data
    claims_by_type = pd.DataFrame({
        'claim_type': ['Medical', 'Pharmacy', 'Dental', 'Vision'],
        'count': [450, 320, 180, 90],
        'total_amount': [125000, 85000, 45000, 22000]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        import plotly.express as px
        fig = px.pie(claims_by_type, values='count', names='claim_type', title='Claims Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(claims_by_type, x='claim_type', y='total_amount', title='Total Amount by Claim Type')
        st.plotly_chart(fig, use_container_width=True)

def show_member_analytics():
    """Member analytics page"""
    st.header("👥 Member Analytics")
    
    # Sample member data
    member_data = pd.DataFrame({
        'department': ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'],
        'member_count': [120, 85, 45, 30, 25],
        'avg_claims': [3.2, 2.8, 2.1, 1.9, 2.5],
        'avg_deductible_met': [0.75, 0.68, 0.82, 0.71, 0.79]
    })
    
    # Filters
    filters = create_filters_sidebar(member_data, ['department'])
    filtered_data = apply_filters(member_data, filters)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        import plotly.express as px
        fig = px.bar(filtered_data, x='department', y='member_count', title='Members by Department')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(filtered_data, x='avg_claims', y='avg_deductible_met', 
                        size='member_count', hover_name='department',
                        title='Claims vs Deductible Met by Department')
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    create_data_table(filtered_data, "Member Analytics Data")

def show_plan_analytics():
    """Plan analytics page"""
    st.header("💳 Plan Analytics")
    
    # Sample plan data
    plan_data = pd.DataFrame({
        'plan_type': ['HMO', 'PPO', 'EPO', 'POS'],
        'member_count': [200, 150, 75, 50],
        'avg_premium': [450, 520, 380, 480],
        'avg_deductible': [1500, 2000, 1000, 1800],
        'satisfaction_score': [4.2, 4.5, 3.8, 4.1]
    })
    
    # Plan comparison
    st.subheader("Plan Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        import plotly.express as px
        fig = px.bar(plan_data, x='plan_type', y='member_count', title='Members by Plan Type')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(plan_data, x='avg_premium', y='avg_deductible', 
                        size='member_count', hover_name='plan_type',
                        title='Premium vs Deductible by Plan')
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    create_data_table(plan_data, "Plan Analytics Data")

def show_data_explorer():
    """Data explorer page"""
    st.header("🔍 Data Explorer")
    
    # Get available models
    models_df = get_dbt_models_info()
    
    if models_df.empty:
        st.warning("No dbt models available. Please ensure your dbt project is properly configured.")
        return
    
    # Model selector
    selected_model = st.selectbox(
        "Select a dbt model to explore:",
        options=models_df['table_name'].tolist()
    )
    
    if selected_model:
        st.subheader(f"Exploring: {selected_model}")
        
        # Sample data for the selected model
        st.info("This would show actual data from your dbt model. For now, showing sample data structure.")
        
        # Create sample data based on model type
        if 'stg_' in selected_model.lower():
            sample_data = pd.DataFrame({
                'id': range(1, 101),
                'name': [f'Record {i}' for i in range(1, 101)],
                'created_date': pd.date_range('2024-01-01', periods=100),
                'status': np.random.choice(['Active', 'Inactive'], 100)
            })
        elif 'dim_' in selected_model.lower():
            sample_data = pd.DataFrame({
                'id': range(1, 21),
                'name': [f'Dimension {i}' for i in range(1, 21)],
                'category': np.random.choice(['A', 'B', 'C'], 21),
                'value': np.random.randint(1, 100, 21)
            })
        elif 'fct_' in selected_model.lower():
            sample_data = pd.DataFrame({
                'id': range(1, 201),
                'amount': np.random.randint(100, 5000, 200),
                'date': pd.date_range('2024-01-01', periods=200),
                'category': np.random.choice(['Type1', 'Type2', 'Type3'], 200)
            })
        else:
            sample_data = pd.DataFrame({
                'id': range(1, 51),
                'value': np.random.randint(1, 100, 50),
                'description': [f'Item {i}' for i in range(1, 51)]
            })
        
        # Show data
        create_data_table(sample_data, f"Data from {selected_model}")

if __name__ == "__main__":
    main()
