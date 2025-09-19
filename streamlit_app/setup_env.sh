#!/bin/bash

# Setup script for Streamlit app environment

echo "🚀 Setting up Streamlit app environment..."

# Copy env.example to .env
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file with your actual credentials:"
    echo "   - SNOWFLAKE_ACCOUNT"
    echo "   - SNOWFLAKE_USER" 
    echo "   - SNOWFLAKE_PASSWORD"
    echo "   - SNOWFLAKE_DATABASE"
    echo "   - DBT_SERVICE_TOKEN"
    echo "   - DBT_ENVIRONMENT_ID"
    echo ""
else
    echo "✅ .env file already exists!"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "🎉 Setup complete! You can now run:"
echo "   python3 -m streamlit run app.py"
echo ""
echo "📖 Or use the run script:"
echo "   ./run.sh"
