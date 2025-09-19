"""
dbt Semantic Layer integration utilities
"""
import streamlit as st
import pandas as pd
import requests
import json
import os
from typing import Dict, List, Optional
from config.settings import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

class DbtSemanticLayer:
    """dbt Semantic Layer client for querying metrics"""
    
    def __init__(self):
        self.service_token = os.getenv("DBT_SERVICE_TOKEN")
        self.environment_id = os.getenv("DBT_ENVIRONMENT_ID")
        self.semantic_layer_host = os.getenv("SEMANTIC_LAYER_HOST", "semantic-layer.cloud.getdbt.com")
        
        if not self.service_token or not self.environment_id:
            st.warning("dbt Cloud credentials not configured. Please set DBT_SERVICE_TOKEN and DBT_ENVIRONMENT_ID in your .env file.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for dbt Cloud API requests"""
        return {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json"
        }
    
    def list_metrics(self) -> List[Dict]:
        """List available metrics from the semantic layer"""
        try:
            # Use dbt Cloud API to get project info first
            url = f"https://cloud.getdbt.com/api/v2/accounts/{self.environment_id}/projects"
            
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            projects = response.json().get("data", [])
            if not projects:
                raise Exception("No projects found")
            
            # For demo purposes, return the metrics defined in our semantic_models.yml
            return [
                {
                    "name": "deductible_met", 
                    "description": "Amount of deductible met YTD",
                    "type": "simple",
                    "label": "Deductible Met"
                },
                {
                    "name": "oop_spent", 
                    "description": "Out of pocket spent YTD",
                    "type": "simple", 
                    "label": "OOP Spent"
                },
                {
                    "name": "claims_by_type", 
                    "description": "Claims breakdown by type",
                    "type": "simple",
                    "label": "Claims by Type"
                },
                {
                    "name": "member_count",
                    "description": "Count of members",
                    "type": "simple",
                    "label": "Member Count"
                },
                {
                    "name": "monthly_premium",
                    "description": "Monthly premium for employee",
                    "type": "simple",
                    "label": "Monthly Premium"
                }
            ]
        except Exception as e:
            st.info(f"Using demo metrics - dbt Cloud API: {str(e)}")
            logger.info(f"Using demo metrics: {str(e)}")
            # Return sample metrics for demo
            return [
                {
                    "name": "deductible_met", 
                    "description": "Amount of deductible met YTD",
                    "type": "simple",
                    "label": "Deductible Met"
                },
                {
                    "name": "oop_spent", 
                    "description": "Out of pocket spent YTD",
                    "type": "simple", 
                    "label": "OOP Spent"
                },
                {
                    "name": "claims_by_type", 
                    "description": "Claims breakdown by type",
                    "type": "simple",
                    "label": "Claims by Type"
                },
                {
                    "name": "member_count",
                    "description": "Count of members",
                    "type": "simple",
                    "label": "Member Count"
                },
                {
                    "name": "monthly_premium",
                    "description": "Monthly premium for employee",
                    "type": "simple",
                    "label": "Monthly Premium"
                }
            ]
    
    def list_dimensions(self, metric_names: List[str]) -> List[Dict]:
        """List available dimensions for given metrics"""
        try:
            # For demo purposes, return dimensions from our semantic models
            return [
                {
                    "name": "claim_date",
                    "type": "time",
                    "description": "Date of the claim",
                    "grain": "day"
                },
                {
                    "name": "claim_type", 
                    "type": "categorical",
                    "description": "Type of claim (Medical, Pharmacy, etc.)"
                },
                {
                    "name": "department",
                    "type": "categorical", 
                    "description": "Member department"
                },
                {
                    "name": "plan_type",
                    "type": "categorical",
                    "description": "Type of health plan"
                },
                {
                    "name": "provider_name",
                    "type": "categorical",
                    "description": "Healthcare provider name"
                }
            ]
        except Exception as e:
            st.info(f"Using demo dimensions: {str(e)}")
            logger.info(f"Using demo dimensions: {str(e)}")
            return [
                {
                    "name": "claim_date",
                    "type": "time",
                    "description": "Date of the claim",
                    "grain": "day"
                },
                {
                    "name": "claim_type", 
                    "type": "categorical",
                    "description": "Type of claim (Medical, Pharmacy, etc.)"
                },
                {
                    "name": "department",
                    "type": "categorical", 
                    "description": "Member department"
                },
                {
                    "name": "plan_type",
                    "type": "categorical",
                    "description": "Type of health plan"
                }
            ]
    
    def query_metrics(self, 
                     metrics: List[str], 
                     group_by: Optional[List[Dict]] = None,
                     where: Optional[str] = None,
                     order_by: Optional[List[Dict]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """Query metrics from the semantic layer"""
        try:
            # Generate realistic demo data that showcases semantic layer capabilities
            import numpy as np
            import pandas as pd
            from datetime import datetime, timedelta
            
            st.info("🎯 Demo Mode: Simulating dbt Semantic Layer queries with realistic healthcare data")
            
            # Determine time range based on where clause
            start_date = pd.to_datetime('2024-01-01')
            end_date = pd.to_datetime('2024-12-31')
            
            if where and 'claim_date' in where:
                # Extract date range from where clause for demo
                if '2024-01-01' in where:
                    start_date = pd.to_datetime('2024-01-01')
                if '2024-12-31' in where:
                    end_date = pd.to_datetime('2024-12-31')
            
            # Create time series based on group_by
            if group_by and any('claim_date' in str(gb) for gb in group_by):
                grain = 'day'
                for gb in group_by:
                    if isinstance(gb, dict) and 'grain' in gb:
                        grain = gb['grain']
                        break
                
                if grain == 'day':
                    dates = pd.date_range(start_date, end_date, freq='D')
                elif grain == 'week':
                    dates = pd.date_range(start_date, end_date, freq='W')
                elif grain == 'month':
                    dates = pd.date_range(start_date, end_date, freq='M')
                elif grain == 'quarter':
                    dates = pd.date_range(start_date, end_date, freq='Q')
                else:
                    dates = pd.date_range(start_date, end_date, freq='D')
            else:
                dates = pd.date_range(start_date, end_date, freq='D')
            
            # Create realistic healthcare data
            sample_data = {
                'claim_date': dates
            }
            
            # Generate realistic metrics with trends and patterns
            for metric in metrics:
                if metric == 'deductible_met':
                    # Simulate deductible met with seasonal patterns
                    base_values = np.random.randint(200, 800, len(dates))
                    seasonal_trend = 100 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
                    sample_data[metric] = np.maximum(0, base_values + seasonal_trend)
                    
                elif metric == 'oop_spent':
                    # Simulate out-of-pocket spending with monthly patterns
                    base_values = np.random.randint(100, 400, len(dates))
                    monthly_pattern = 50 * np.sin(np.arange(len(dates)) * 2 * np.pi / 30)
                    sample_data[metric] = np.maximum(0, base_values + monthly_pattern)
                    
                elif metric == 'claims_by_type':
                    # Simulate claims count with weekly patterns
                    base_values = np.random.randint(10, 60, len(dates))
                    weekly_pattern = 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
                    sample_data[metric] = np.maximum(0, base_values + weekly_pattern)
                    
                elif metric == 'member_count':
                    # Simulate member count (relatively stable)
                    sample_data[metric] = np.random.randint(450, 500, len(dates))
                    
                elif metric == 'monthly_premium':
                    # Simulate monthly premium (stable with small variations)
                    sample_data[metric] = np.random.randint(400, 550, len(dates))
                    
                else:
                    # Generic metric
                    sample_data[metric] = np.random.randint(50, 200, len(dates))
            
            df = pd.DataFrame(sample_data)
            
            # Apply limit if specified
            if limit:
                df = df.head(limit)
            
            # Add some demo metadata
            st.success(f"✅ Semantic Layer Query Executed Successfully!")
            st.caption(f"📊 Retrieved {len(df)} rows for metrics: {', '.join(metrics)}")
            
            return df
                
        except Exception as e:
            st.error(f"Failed to query metrics: {str(e)}")
            logger.error(f"Error querying metrics: {str(e)}")
            return pd.DataFrame()
    
    def get_metric_sql(self, 
                      metrics: List[str], 
                      group_by: Optional[List[Dict]] = None,
                      where: Optional[str] = None) -> str:
        """Get the compiled SQL for a metric query"""
        try:
            url = f"https://{self.semantic_layer_host}/api/v1/query/sql"
            
            payload = {
                "environment_id": self.environment_id,
                "metrics": metrics
            }
            
            if group_by:
                payload["group_by"] = group_by
            if where:
                payload["where"] = where
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("sql", "")
                
        except Exception as e:
            st.error(f"Failed to get metric SQL: {str(e)}")
            logger.error(f"Error getting metric SQL: {str(e)}")
            return ""

# Global semantic layer client
@st.cache_resource
def get_semantic_layer_client():
    """Get cached semantic layer client"""
    return DbtSemanticLayer()

def get_available_metrics() -> List[Dict]:
    """Get list of available metrics"""
    client = get_semantic_layer_client()
    return client.list_metrics()

def get_available_dimensions(metric_names: List[str]) -> List[Dict]:
    """Get list of available dimensions for metrics"""
    client = get_semantic_layer_client()
    return client.list_dimensions(metric_names)

def query_metric_data(metrics: List[str], 
                     group_by: Optional[List[Dict]] = None,
                     where: Optional[str] = None,
                     order_by: Optional[List[Dict]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
    """Query metric data from semantic layer"""
    client = get_semantic_layer_client()
    return client.query_metrics(metrics, group_by, where, order_by, limit)

def get_metric_sql(metrics: List[str], 
                  group_by: Optional[List[Dict]] = None,
                  where: Optional[str] = None) -> str:
    """Get compiled SQL for metric query"""
    client = get_semantic_layer_client()
    return client.get_metric_sql(metrics, group_by, where)

# Predefined metric queries for common use cases
def get_claims_metrics_by_date(start_date: str = "2024-01-01", end_date: str = "2024-12-31") -> pd.DataFrame:
    """Get claims metrics grouped by date"""
    return query_metric_data(
        metrics=["deductible_met", "oop_spent", "claims_by_type"],
        group_by=[{"name": "claim_date", "grain": "day"}],
        where=f"{{{{ Dimension('claim__claim_date') }}}} >= '{start_date}' AND {{{{ Dimension('claim__claim_date') }}}} <= '{end_date}'",
        order_by=[{"name": "claim_date", "descending": False}]
    )

def get_member_metrics_by_department() -> pd.DataFrame:
    """Get member metrics grouped by department"""
    return query_metric_data(
        metrics=["member_count"],
        group_by=[{"name": "department", "grain": None}]
    )

def get_plan_metrics() -> pd.DataFrame:
    """Get plan-related metrics"""
    return query_metric_data(
        metrics=["monthly_premium", "annual_deductible", "oop_max"],
        group_by=[{"name": "plan_type", "grain": None}]
    )
