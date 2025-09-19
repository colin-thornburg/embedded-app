# Healthcare Analytics Dashboard

A Streamlit application for healthcare claims and member analytics, integrated with dbt for data transformation and Snowflake for data storage.

## Features

- 📊 **Executive Dashboard**: Key metrics and trends overview
- 🏥 **Claims Analysis**: Detailed claims breakdown and analysis
- 👥 **Member Analytics**: Member demographics and behavior insights
- 💳 **Plan Analytics**: Health plan comparison and performance
- 🔍 **Data Explorer**: Interactive exploration of dbt models

## Architecture

```
streamlit_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── config/
│   └── settings.py       # Configuration settings
├── utils/
│   ├── database.py       # Database connection utilities
│   └── visualizations.py # Visualization helper functions
└── pages/
    └── __init__.py       # Pages module
```

## Setup

### 1. Install Dependencies

```bash
cd streamlit_app
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your Snowflake credentials:

```env
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### 3. dbt Configuration

Ensure your dbt project is properly configured and models are built:

```bash
# From the project root
dbt run
dbt test
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Navigation

The application includes a sidebar navigation with the following pages:

- **Dashboard**: Executive overview with key metrics
- **Claims Analysis**: Claims data analysis and visualization
- **Member Analytics**: Member demographics and behavior
- **Plan Analytics**: Health plan comparison
- **Data Explorer**: Interactive data exploration

### Features

- **Interactive Filters**: Filter data by various dimensions
- **Real-time Metrics**: Live updates from your dbt models
- **Responsive Design**: Works on desktop and mobile
- **Data Export**: Export filtered data as CSV

## Development

### Adding New Pages

1. Create a new Python file in the `pages/` directory
2. Import the necessary utilities from `utils/`
3. Add the page to the navigation menu in `app.py`

### Adding New Visualizations

1. Add new visualization functions to `utils/visualizations.py`
2. Import and use them in your pages
3. Follow the existing patterns for consistency

### Database Integration

The application uses the `utils/database.py` module for all database operations:

- `get_snowflake_connection()`: Get cached Snowflake connection
- `execute_query()`: Execute SQL queries
- `get_dbt_models_info()`: Get dbt model information
- `get_metrics_data()`: Get metrics from semantic models

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Verify your Snowflake credentials in `.env`
2. **dbt Models Not Found**: Ensure dbt models are built and accessible
3. **Import Errors**: Check that all dependencies are installed

### Logs

The application logs errors and warnings. Check the console output for debugging information.

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Include docstrings for new functions
4. Test with sample data before production use

## License

This project is part of the embedded-app dbt project.
