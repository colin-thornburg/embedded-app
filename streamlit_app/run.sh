#!/bin/bash

# Streamlit App Runner Script
# This script sets up and runs the Streamlit application

echo "🚀 Starting Healthcare Analytics Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please copy env.example to .env and configure your settings."
    echo "   cp env.example .env"
    echo "   # Then edit .env with your Snowflake credentials"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Run the application
echo "🌐 Starting Streamlit application..."
echo "   Open your browser to: http://localhost:8501"
echo "   Press Ctrl+C to stop the application"

streamlit run app.py
