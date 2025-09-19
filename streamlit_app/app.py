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
from utils.semantic_layer import (
    get_available_metrics,
    get_available_dimensions,
    query_metric_data,
    get_claims_metrics_by_date,
    get_member_metrics_by_department,
    get_plan_metrics
)
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
            options=["Dashboard", "Claims Analysis", "Member Analytics", "Plan Analytics", "Semantic Layer", "Data Explorer"],
            icons=["house", "file-medical", "people", "credit-card", "layers", "search"],
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
    elif selected == "Semantic Layer":
        show_semantic_layer()
    elif selected == "Data Explorer":
        show_data_explorer()

def show_dashboard():
    """Main dashboard page"""
    st.header("📊 Executive Dashboard")
    
    # Check if semantic layer is available
    try:
        # Get real metrics from semantic layer
        claims_data = get_claims_metrics_by_date()
        member_data = get_member_metrics_by_department()
        
        if not claims_data.empty:
            # Calculate summary metrics from real data
            total_claims = claims_data['claims_by_type'].sum() if 'claims_by_type' in claims_data.columns else 0
            total_deductible = claims_data['deductible_met'].sum() if 'deductible_met' in claims_data.columns else 0
            total_oop = claims_data['oop_spent'].sum() if 'oop_spent' in claims_data.columns else 0
            
            # Key metrics cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card(
                    title="Total Claims",
                    value=f"{total_claims:,.0f}",
                    delta="+12%",
                    delta_color="normal"
                )
            
            with col2:
                create_metric_card(
                    title="Total Members",
                    value=f"{member_data['member_count'].sum():,.0f}" if not member_data.empty else "0",
                    delta="+5%",
                    delta_color="normal"
                )
            
            with col3:
                create_metric_card(
                    title="Deductible Met",
                    value=f"${total_deductible:,.0f}",
                    delta="+8%",
                    delta_color="normal"
                )
            
            with col4:
                create_metric_card(
                    title="Out of Pocket",
                    value=f"${total_oop:,.0f}",
                    delta="+3%",
                    delta_color="normal"
                )
            
            # Charts section
            st.subheader("📈 Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'claim_date' in claims_data.columns and 'deductible_met' in claims_data.columns:
                    import plotly.express as px
                    fig1 = px.line(claims_data, x='claim_date', y='deductible_met', 
                                 title='Deductible Met Over Time')
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                if 'claim_date' in claims_data.columns and 'oop_spent' in claims_data.columns:
                    import plotly.express as px
                    fig2 = px.line(claims_data, x='claim_date', y='oop_spent', 
                                 title='Out of Pocket Spending Over Time')
                    st.plotly_chart(fig2, use_container_width=True)
        
        else:
            st.warning("No data available from semantic layer. Please ensure your dbt models are built and semantic layer is configured.")
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        
        # Fallback to sample data
        st.info("Showing sample data - configure your dbt Cloud credentials to see real data")
        
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

def show_claims_analysis():
    """Claims analysis page"""
    st.header("🏥 Claims Analysis")
    
    try:
        # Get real claims data from semantic layer
        claims_data = get_claims_metrics_by_date()
        
        if not claims_data.empty:
            st.subheader("Claims Metrics Over Time")
            
            # Show claims trends
            col1, col2 = st.columns(2)
            
            with col1:
                if 'claim_date' in claims_data.columns and 'deductible_met' in claims_data.columns:
                    import plotly.express as px
                    fig = px.line(claims_data, x='claim_date', y='deductible_met', 
                                title='Deductible Met Over Time')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'claim_date' in claims_data.columns and 'oop_spent' in claims_data.columns:
                    import plotly.express as px
                    fig = px.line(claims_data, x='claim_date', y='oop_spent', 
                                title='Out of Pocket Spending Over Time')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Show raw data
            st.subheader("Claims Data")
            create_data_table(claims_data, "Claims Metrics Data")
            
        else:
            st.warning("No claims data available from semantic layer.")
            
    except Exception as e:
        st.error(f"Error loading claims data: {str(e)}")
        
        # Fallback to sample data
        st.info("Showing sample data - configure your dbt Cloud credentials to see real data")
        
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

def show_semantic_layer():
    """Semantic layer exploration page"""
    st.header("🔗 dbt Semantic Layer")
    
    # Demo mode indicator
    st.info("🎯 **Demo Mode**: This showcases dbt Semantic Layer capabilities with realistic healthcare data. In production, this would connect to your actual dbt Cloud semantic layer.")
    
    try:
        # Get available metrics
        st.subheader("📊 Available Metrics")
        metrics = get_available_metrics()
        
        if metrics:
            metrics_df = pd.DataFrame(metrics)
            create_data_table(metrics_df, "Available Metrics")
            
            # Get dimensions for selected metrics
            if st.button("Load Dimensions"):
                metric_names = [m.get('name', '') for m in metrics if m.get('name')]
                if metric_names:
                    dimensions = get_available_dimensions(metric_names)
                    if dimensions:
                        st.subheader("📏 Available Dimensions")
                        dimensions_df = pd.DataFrame(dimensions)
                        create_data_table(dimensions_df, "Available Dimensions")
                    else:
                        st.warning("No dimensions found for the selected metrics.")
        else:
            st.warning("No metrics available. Please ensure your dbt project is properly configured and semantic layer is set up.")
        
        # Interactive query builder
        st.subheader("🔍 Interactive Query Builder")
        
        if metrics:
            # Metric selector
            metric_options = [m.get('name', '') for m in metrics if m.get('name')]
            selected_metrics = st.multiselect(
                "Select metrics to query:",
                options=metric_options,
                default=metric_options[:2] if len(metric_options) >= 2 else metric_options
            )
            
            if selected_metrics:
                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=pd.to_datetime('2024-01-01').date())
                with col2:
                    end_date = st.date_input("End Date", value=pd.to_datetime('2024-12-31').date())
                
                # Group by options
                group_by_option = st.selectbox(
                    "Group by:",
                    options=["None", "Day", "Week", "Month", "Quarter", "Year"]
                )
                
                if st.button("Run Query"):
                    try:
                        # Build query parameters
                        group_by = None
                        if group_by_option != "None":
                            group_by = [{"name": "claim_date", "grain": group_by_option.lower()}]
                        
                        where_clause = f"{{{{ Dimension('claim__claim_date') }}}} >= '{start_date}' AND {{{{ Dimension('claim__claim_date') }}}} <= '{end_date}'"
                        
                        # Execute query
                        with st.spinner("Querying semantic layer..."):
                            results = query_metric_data(
                                metrics=selected_metrics,
                                group_by=group_by,
                                where=where_clause,
                                limit=100
                            )
                        
                        if not results.empty:
                            st.subheader("Query Results")
                            create_data_table(results, "Semantic Layer Query Results")
                            
                            # Show charts
                            if len(selected_metrics) > 0:
                                st.subheader("Visualizations")
                                for metric in selected_metrics:
                                    if metric in results.columns:
                                        import plotly.express as px
                                        if group_by_option != "None" and 'claim_date' in results.columns:
                                            fig = px.line(results, x='claim_date', y=metric, title=f'{metric} Over Time')
                                        else:
                                            fig = px.bar(results, x=metric, title=f'{metric} Distribution')
                                        st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No results returned from the query.")
                            
                    except Exception as e:
                        st.error(f"Query failed: {str(e)}")
        else:
            st.info("Configure your dbt Cloud credentials to explore the semantic layer.")
            
    except Exception as e:
        st.error(f"Error loading semantic layer data: {str(e)}")
        st.info("Please ensure your dbt Cloud credentials are configured in the .env file.")

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
