# 🚀 AI-Powered Multi-Agent Business Data Analysis System

A complete end-to-end natural language business analytics platform built with Flask, vanilla HTML/CSS/JS, and Groq LLM.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📋 Overview

This system allows users to:
- ✅ Upload CSV or Excel datasets (up to 200 MB)
- ✅ Automatically clean and validate data
- ✅ Ask questions in natural language (no coding required)
- ✅ Get instant analytical insights
- ✅ Generate automatic visualizations
- ✅ Download comprehensive PDF reports

## 🏗️ Architecture

### Sequential Multi-Agent System

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐     ┌────────────┐     ┌──────────┐
│   Input     │────▶│   Cleaning   │────▶│   NLQ   │────▶│Visualization│────▶│  Report  │
│   Agent     │     │    Agent     │     │  Agent  │     │   Agent     │     │  Agent   │
└─────────────┘     └──────────────┘     └─────────┘     └────────────┘     └──────────┘
      │                    │                   │                 │                  │
   Validate           Clean Data          Query LLM        Auto Charts         PDF Export
   Load CSV           User Choices       Pandas Ops        Matplotlib
                                                           Plotly
```

### Agent Responsibilities

1. **Input Agent** 🔵
   - File validation (CSV, Excel)
   - Data loading
   - Metadata extraction
   - Issue detection

2. **Cleaning Agent** 🟢
   - Interactive missing value handling
   - Duplicate removal
   - User-driven cleaning decisions
   - Operation logging

3. **NLQ Agent** 🟡
   - Natural language understanding
   - Query to Pandas conversion
   - LLM-powered reasoning (Groq)
   - PandasAI integration

4. **Visualization Agent** 🟣
   - Auto chart selection
   - Multiple chart types (bar, line, pie, scatter, etc.)
   - Matplotlib & Plotly support
   - Interactive visualizations

5. **Report Agent** 🔴
   - PDF generation
   - Comprehensive summary
   - Chart embedding
   - Professional formatting

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Flask + HTML/CSS/JS |
| **Data Processing** | Pandas, NumPy |
| **AI/ML** | LangChain, PandasAI, Groq LLM |
| **Visualization** | Matplotlib, Plotly, Seaborn |
| **PDF Generation** | ReportLab |
| **API** | Groq API (Mixtral-8x7b) |

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Groq API key ([Get one here](https://console.groq.com/keys))

### Step-by-Step Setup

1. **Clone or Download the Project**
```bash
cd ai-business-analytics
```

2. **Create Virtual Environment (Recommended)**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_api_key_here
```

5. **Run the Application**
```bash
python app.py
```

Then open `http://localhost:8000` to load the HTML/CSS/JS interface. The Flask server also exposes REST endpoints under `/api/*`.

## 🎯 Usage Guide

### Step 1: Upload Data
- Click "Browse files" or drag-and-drop
- Supported formats: CSV, XLSX, XLS
- Maximum size: 200 MB
- View automatic data summary

### Step 2: Clean Data
- Review detected issues (missing values, duplicates)
- Select cleaning strategies:
  - Missing values: mean, median, mode, forward/backward fill, drop
  - Duplicates: remove all, keep first/last, keep all
- Apply cleaning and view summary

### Step 3: Ask Questions
Natural language query examples:
- "What is the total sales amount?"
- "How many unique customers are there?"
- "Show me sales by region"
- "What is the average order value?"
- "Count orders by product category"

### Step 4: Visualize
- **Auto Mode**: AI automatically generates relevant charts
- **Custom Mode**: Select chart type and columns manually
- Supported charts:
  - Bar charts
  - Line graphs
  - Pie charts
  - Histograms
  - Scatter plots
  - Box plots
  - Correlation heatmaps

### Step 5: Generate Report
- Click "Generate PDF Report"
- Includes:
  - Dataset overview
  - Cleaning summary
  - Query history
  - All visualizations
  - Key insights
- Download as PDF

## 📁 Project Structure

```
ai-business-analytics/
│
├── app.py                          # Flask backend + REST API
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── README.md                       # This file
│
├── agents/                         # Multi-agent system
│   ├── __init__.py
│   ├── input_agent.py             # Data ingestion
│   ├── cleaning_agent.py          # Data cleaning
│   ├── nlq_agent.py               # NL query processing
│   ├── visualization_agent.py     # Chart generation
│   └── report_agent.py            # PDF reports
│
├── utils/                          # Utilities
│   ├── __init__.py
│   ├── config.py                  # Configuration
│   ├── session_manager.py         # State management
│   └── validators.py              # Input validation
│
├── static/                         # HTML, CSS, JS frontend
├── sample_data/                    # Sample datasets
│   ├── sales_data.csv
│   └── sample_queries.txt
│
├── outputs/                        # Generated files
│   ├── reports/                   # PDF reports
│   └── charts/                    # Saved charts
│
└── docs/                          # Documentation
    ├── ARCHITECTURE.md
    ├── VIVA_GUIDE.md
    └── API_REFERENCE.md
```

## 🔧 Configuration

Key settings in `utils/config.py`:

```python
# API Configuration
GROQ_MODEL = "mixtral-8x7b-32768"

# File Limits
MAX_FILE_SIZE_MB = 200
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# Visualization
CHART_TYPES = ['bar', 'line', 'pie', 'histogram', 'scatter', 'box', 'heatmap']
```

## 📊 Sample Data

Included sample dataset: `sample_data/sales_data.csv`
- 40 sample orders
- Columns: Order_ID, Customer_Name, Product_Category, Total_Sales, Region, etc.
- Perfect for testing all features

## 🧪 Testing the System

1. **Load Sample Data**
   - Navigate to Step 1
   - Upload `sample_data/sales_data.csv`

2. **Clean Data**
   - Go to Step 2
   - Select cleaning options
   - Apply cleaning

3. **Test Queries** (from `sample_queries.txt`):
   ```
   - What is the total sales amount?
   - How many unique customers?
   - Show me sales by product category
   ```

4. **Generate Visualizations**
   - Try Auto mode
   - Or create custom charts

5. **Export Report**
   - Generate PDF
   - Download and review

## 🎓 Viva/Presentation Points

### Architecture Overview
- Sequential multi-agent design
- Each agent has single responsibility
- Shared session state management
- Groq LLM for NL understanding

### Key Features
- No-code interface for business users
- Supports large datasets (50MB+)
- Real-time query processing
- Auto chart recommendations
- Professional PDF reports

### Technical Highlights
- LangChain integration
- PandasAI for query execution
- Dual visualization (Matplotlib + Plotly)
- ReportLab for PDF generation
- Flask + custom HTML/CSS/JS interface

### Data Flow
1. User uploads file
2. Input Agent validates
3. Cleaning Agent prepares data
4. NLQ Agent processes queries
5. Viz Agent creates charts
6. Report Agent exports PDF

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
Solution: Ensure GROQ_API_KEY is set in .env file
```

**2. Module Not Found**
```bash
Solution: pip install -r requirements.txt
```

**3. File Upload Fails**
```
Solution: Check file size (<200MB) and format (CSV/Excel)
```

**4. Query Returns Error**
```
Solution: Rephrase query, ensure data is loaded and cleaned
```

## 📝 Future Enhancements

- [ ] Database connectivity (PostgreSQL, MySQL)
- [ ] Real-time streaming data support
- [ ] Custom ML model integration
- [ ] Multi-user collaboration
- [ ] Advanced statistical tests
- [ ] Export to PowerPoint
- [ ] Email report delivery
- [ ] Scheduled automated reports

## 👥 Contributing

This is an educational project. Feel free to fork and enhance!

## 📄 License

MIT License - Free for educational and commercial use

## 🙏 Acknowledgments

- **Groq**: For fast LLM inference
- **Flask**: For lightweight backend routing
- **LangChain**: For LLM orchestration
- **PandasAI**: For NL to Pandas conversion

## 📧 Support

For questions or issues:
1. Check the documentation
2. Review sample queries
3. Ensure API key is configured
4. Test with sample data first

---

**Built with ❤️ using AI Multi-Agent Architecture**

*Version 1.0.0 | Last Updated: February 2026*
