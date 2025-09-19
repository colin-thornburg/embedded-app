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
            url = f"https://{self.semantic_layer_host}/api/v1/metrics"
            params = {"environment_id": self.environment_id}
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            return response.json().get("data", [])
        except Exception as e:
            st.error(f"Failed to list metrics: {str(e)}")
            logger.error(f"Error listing metrics: {str(e)}")
            return []
    
    def list_dimensions(self, metric_names: List[str]) -> List[Dict]:
        """List available dimensions for given metrics"""
        try:
            url = f"https://{self.semantic_layer_host}/api/v1/dimensions"
            params = {
                "environment_id": self.environment_id,
                "metrics": metric_names
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            return response.json().get("data", [])
        except Exception as e:
            st.error(f"Failed to list dimensions: {str(e)}")
            logger.error(f"Error listing dimensions: {str(e)}")
            return []
    
    def query_metrics(self, 
                     metrics: List[str], 
                     group_by: Optional[List[Dict]] = None,
                     where: Optional[str] = None,
                     order_by: Optional[List[Dict]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """Query metrics from the semantic layer"""
        try:
            url = f"https://{self.semantic_layer_host}/api/v1/query"
            
            payload = {
                "environment_id": self.environment_id,
                "metrics": metrics
            }
            
            if group_by:
                payload["group_by"] = group_by
            if where:
                payload["where"] = where
            if order_by:
                payload["order_by"] = order_by
            if limit:
                payload["limit"] = limit
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            if "data" in data and data["data"]:
                return pd.DataFrame(data["data"])
            else:
                return pd.DataFrame()
                
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
