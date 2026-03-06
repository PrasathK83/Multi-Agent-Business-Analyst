# 📁 AI Business Analytics - Project Structure

```
ai-business-analytics/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # Project documentation
│
├── agents/                         # Multi-agent architecture
│   ├── __init__.py
│   ├── input_agent.py             # Agent 1: Data ingestion & validation
│   ├── cleaning_agent.py          # Agent 2: Interactive data cleaning
│   ├── nlq_agent.py               # Agent 3: Natural language query processing
│   ├── visualization_agent.py     # Agent 4: Auto chart generation
│   └── report_agent.py            # Agent 5: PDF report generation
│
├── utils/                          # Helper utilities
│   ├── __init__.py
│   ├── session_manager.py         # Streamlit session state management
│   ├── config.py                  # Configuration and constants
│   └── validators.py              # Input validation helpers
│
├── assets/                         # Static assets
│   ├── logo.png                   # Application logo (optional)
│   └── styles.css                 # Custom CSS (optional)
│
├── sample_data/                    # Sample datasets for testing
│   ├── sales_data.csv
│   ├── hr_analytics.xlsx
│   └── sample_queries.txt
│
├── outputs/                        # Generated outputs
│   ├── reports/                   # PDF reports
│   └── charts/                    # Saved visualizations
│
└── docs/                          # Documentation
    ├── ARCHITECTURE.md            # System architecture explanation
    ├── VIVA_GUIDE.md             # Viva preparation points
    └── API_REFERENCE.md          # Agent API documentation
```

## 📊 Data Flow

```
User Upload → Input Agent → Cleaning Agent → NLQ Agent → Visualization Agent → Report Agent
     ↓              ↓              ↓              ↓                ↓                ↓
  File CSV      Validation    User Choices   Query Parse      Auto Charts      PDF Export
                DataFrame     Clean Data      Pandas Ops       Matplotlib
                                                               Plotly
```
