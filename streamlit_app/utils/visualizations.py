"""
Visualization utilities for the Streamlit app
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional

def create_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Create a metric card with optional delta"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None):
    """Create a line chart"""
    fig = px.line(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        template="plotly_white"
    )
    fig.update_layout(
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title(),
        hovermode='x unified'
    )
    return fig

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None):
    """Create a bar chart"""
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        template="plotly_white"
    )
    fig.update_layout(
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title(),
        hovermode='x unified'
    )
    return fig

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    """Create a pie chart"""
    fig = px.pie(
        df, 
        names=names, 
        values=values, 
        title=title,
        template="plotly_white"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_heatmap(df: pd.DataFrame, x: str, y: str, values: str, title: str):
    """Create a heatmap"""
    fig = px.imshow(
        df.pivot(index=y, columns=x, values=values),
        title=title,
        template="plotly_white",
        aspect="auto"
    )
    return fig

def create_dashboard_grid(metrics: List[Dict], charts: List[Dict]):
    """Create a dashboard grid layout"""
    # Metrics row
    if metrics:
        st.subheader("📊 Key Metrics")
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                create_metric_card(**metric)
    
    # Charts section
    if charts:
        st.subheader("📈 Analytics")
        for chart in charts:
            st.plotly_chart(chart, use_container_width=True)

def create_filters_sidebar(df: pd.DataFrame, filter_columns: List[str]):
    """Create filter sidebar for the dataframe"""
    st.sidebar.header("🔍 Filters")
    
    filters = {}
    for col in filter_columns:
        if col in df.columns:
            unique_values = df[col].unique()
            if len(unique_values) > 1:
                selected = st.sidebar.multiselect(
                    f"Select {col.replace('_', ' ').title()}",
                    options=unique_values,
                    default=unique_values
                )
                filters[col] = selected
    
    return filters

def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    for col, values in filters.items():
        if col in filtered_df.columns and values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    return filtered_df

def create_data_table(df: pd.DataFrame, title: str = "Data Table"):
    """Create an interactive data table"""
    st.subheader(title)
    
    # Add search and filter options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search in all columns...")
    
    with col2:
        show_rows = st.selectbox("Show rows", [10, 25, 50, 100, "All"])
    
    # Apply search filter
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df = df[mask]
    
    # Show data
    if show_rows == "All":
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df.head(show_rows), use_container_width=True)
    
    # Show summary
    st.info(f"Showing {len(df)} rows out of {len(df)} total rows")
