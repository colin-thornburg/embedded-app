"""
Chat interface components for the Insurance Portal
Handles conversation display and user interactions
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from agent.insurance_agent import InsuranceAgent

def render_chat_interface():
    """Render the main chat interface"""

    # Initialize agent
    if 'agent' not in st.session_state:
        st.session_state.agent = InsuranceAgent()

    # Show sample questions
    render_sample_questions()

    # Display chat history
    render_chat_history()

    # Chat input
    handle_chat_input()

def render_sample_questions():
    """Show sample questions to help users get started"""

    if not st.session_state.messages:
        st.markdown("### 💡 Try asking me about:")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💰 How much of my deductible have I met?", use_container_width=True):
                process_user_message("How much of my deductible have I met?")

            if st.button("📊 Show my claims this year", use_container_width=True):
                process_user_message("Show my claims this year")

        with col2:
            if st.button("💳 What's my out-of-pocket spending?", use_container_width=True):
                process_user_message("What's my out-of-pocket spending this year?")

            if st.button("📈 Claims by type breakdown", use_container_width=True):
                process_user_message("Show me my claims broken down by type")

        st.markdown("---")

def render_chat_history():
    """Display the conversation history"""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                # Assistant message with potential data visualization
                render_assistant_message(message)

def render_assistant_message(message: Dict[str, Any]):
    """Render assistant message with data visualization if applicable"""

    # Show the text response
    st.write(message["content"])

    # Handle different response types
    response_data = message.get("data")
    if response_data:
        response_type = message.get("type", "text")

        if response_type == "metric":
            render_metric_display(response_data)
        elif response_type == "data":
            render_data_visualization(response_data)

def render_metric_display(metric_data: Dict[str, Any]):
    """Display a single metric prominently"""

    metric_name = metric_data.get("metric", "")
    value = metric_data.get("value", 0)

    # Format the metric display
    if isinstance(value, (int, float)):
        if metric_name in ['deductible_met', 'oop_spent', 'total_claims', 'paid_amount', 'member_responsibility']:
            formatted_value = f"${value:,.2f}"
        else:
            formatted_value = f"{value:,}"
    else:
        formatted_value = str(value)

    # Display as a prominent metric
    st.metric(
        label=metric_name.replace('_', ' ').title(),
        value=formatted_value
    )

def render_data_visualization(data: Any):
    """Render data as tables and charts"""

    if not data:
        return

    # Convert to DataFrame for easier manipulation
    if isinstance(data, list) and data:
        df = pd.DataFrame(data)

        # Clean up column names for display
        df.columns = [col.replace('_', ' ').title() for col in df.columns]

        # Show data table
        st.dataframe(df, use_container_width=True)

        # Auto-generate charts if appropriate
        render_auto_charts(df)

def render_auto_charts(df: pd.DataFrame):
    """Automatically generate charts based on data structure"""

    if df.empty or len(df) < 2:
        return

    # Look for time series data
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    if date_columns and numeric_columns:
        # Time series chart
        date_col = date_columns[0]
        for metric_col in numeric_columns[:2]:  # Limit to 2 metrics
            fig = px.line(
                df,
                x=date_col,
                y=metric_col,
                title=f"{metric_col} Over Time",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

    elif len(numeric_columns) >= 1 and len(df) <= 20:
        # Bar chart for categorical data
        categorical_cols = [col for col in df.columns if col not in numeric_columns]
        if categorical_cols:
            cat_col = categorical_cols[0]
            metric_col = numeric_columns[0]

            fig = px.bar(
                df,
                x=cat_col,
                y=metric_col,
                title=f"{metric_col} by {cat_col}"
            )
            st.plotly_chart(fig, use_container_width=True)

def handle_chat_input():
    """Handle user input and process messages"""

    # Chat input
    if prompt := st.chat_input("Ask me about your insurance benefits..."):
        process_user_message(prompt)

def process_user_message(user_input: str):
    """Process a user message and generate response"""

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Show user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Process query through the agent
                response = st.session_state.agent.process_query(user_input)

                # Add to message history
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("message", "I'm sorry, I couldn't process that request."),
                    "type": response.get("type", "text"),
                    "data": response.get("data")
                }

                st.session_state.messages.append(assistant_message)

                # Render the response
                render_assistant_message(assistant_message)

            except Exception as e:
                error_message = f"I encountered an error: {str(e)}"
                st.error(error_message)

                # Add error to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "type": "error",
                    "data": None
                })

def clear_chat_history():
    """Clear the chat history"""
    st.session_state.messages = []
    st.rerun()

# Sample questions helper
def get_sample_questions() -> list:
    """Get context-aware sample questions"""

    user_context = st.session_state.get('user_context', {})
    company_name = user_context.get('company_name', 'Company')

    return [
        "How much of my deductible have I met this year?",
        "What's my total out-of-pocket spending?",
        f"Show me all claims for {company_name} this quarter",
        "What are my most expensive claim types?",
        "How many claims were approved vs denied?",
        "What's my remaining deductible amount?",
        "Show claims by month for this year",
        "What's the average claim amount?",
    ]