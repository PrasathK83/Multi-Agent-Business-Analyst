"""
Configuration and Constants for AI Business Analytics System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (allow .env to override shell values)
load_dotenv(override=True)

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Default Groq chat model

# File Upload Limits
MAX_FILE_SIZE_MB = 200
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# Data Processing
MISSING_VALUE_STRATEGIES = {
    'Mean': 'mean',
    'Median': 'median',
    'Mode': 'mode',
    'Forward Fill': 'ffill',
    'Backward Fill': 'bfill',
    'Drop Rows': 'drop'
}

DUPLICATE_STRATEGIES = {
    'Remove All Duplicates': 'drop',
    'Keep First Occurrence': 'first',
    'Keep Last Occurrence': 'last',
    'Keep All': 'keep'
}

# Visualization Configuration
CHART_TYPES = [
    'bar',
    'line',
    'pie',
    'histogram',
    'scatter',
    'box',
    'heatmap'
]

PLOTLY_TEMPLATE = 'plotly_white'
MATPLOTLIB_STYLE = 'seaborn-v0_8-darkgrid'

# Colors
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
]

# PDF Report Configuration
REPORT_TITLE = "Business Data Analysis Report"
REPORT_AUTHOR = "AI Multi-Agent Analytics System"
REPORT_PAGE_SIZE = "A4"

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
CHARTS_DIR = OUTPUTS_DIR / "charts"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

# Create directories if they don't exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# LangChain Configuration
LANGCHAIN_VERBOSE = False
LANGCHAIN_TEMPERATURE = 0.1

# PandasAI Configuration
PANDASAI_VERBOSE = False
PANDASAI_ENFORCE_PRIVACY = True
