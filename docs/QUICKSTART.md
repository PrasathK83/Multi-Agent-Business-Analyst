# 🚀 Quick Start Guide

Get your AI Business Analytics system running in under 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] pip package manager
- [ ] Internet connection (for package installation)
- [ ] Groq API key ([Get free key](https://console.groq.com/keys))

---

## Step-by-Step Installation

### 1. Project Setup

```bash
# Navigate to project directory
cd ai-business-analytics

# Verify Python version
python --version
# Should show: Python 3.10.x or higher
```bash
# Use different port (temporary override)
# Windows PowerShell

# macOS/Linux
PORT=8800 python app.py

# Or kill existing process
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <process_id>
```
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will take 2-3 minutes
```

**Expected Output:**
```
Successfully installed flask-3.0.2 pandas-2.1.4 ...
```

### 4. Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

**Add your Groq API key:**
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

**To get a free Groq API key:**
1. Visit https://console.groq.com/keys
2. Sign up/login
3. Click "Create API Key"
4. Copy the key
5. Paste into `.env` file

### 5. Verify Installation

```bash
# Test imports
python -c "import flask, pandas, langchain, plotly; print('✅ All packages installed')"
```

### 6. Launch Application

```bash
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open http://localhost:8000 to access the HTML/JS dashboard.

---

## First-Time Usage

### Test with Sample Data

1. **Card 01 · Upload Dataset**
   - Drop `sample_data/sales_data.csv`
   - Wait for profiling (1-2 seconds)
   - ✅ Preview panel lists columns + sample rows

2. **Card 02 · Clean Data**
   - Review missing values + duplicates summary
   - Choose strategies and submit
   - ✅ Cleaning summary shows rows removed + gaps fixed

3. **Card 03 · Ask Questions**
   - Ask "What is the total sales amount?"
   - Hit "Run NLQ"
   - ✅ Result panel shows metric/table

4. **Card 04 · Visualize**
   - Click "Auto-generate" for AI charts
   - Or craft a custom chart via the form
   - ✅ Gallery renders Plotly visuals inline

5. **Card 05 · Generate Report**
   - Click "Build PDF dossier"
   - Download from the provided link
   - ✅ Confirm PDF contains tables + charts

---

## Troubleshooting

### Issue 1: "GROQ_API_KEY not found"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env  # On macOS/Linux
dir .env     # On Windows

# Make sure it contains your key
cat .env     # On macOS/Linux
type .env    # On Windows

# Restart application after adding key
# Press Ctrl+C in terminal, then run again:
python app.py
```

### Issue 2: "Module not found"

**Solution:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in prompt

# Reinstall requirements
pip install -r requirements.txt

# If specific package fails:
pip install package_name --upgrade
```

### Issue 3: Port 8000 already in use

**Solution:**
```bash
# Use different port for this run
# Windows PowerShell
$env:PORT=8800; python app.py

# macOS/Linux
PORT=8800 python app.py

# Or kill existing process
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <process_id>
```

### Issue 4: File upload fails

**Solution:**
- Check file size (<200MB)
- Ensure file is CSV or Excel (.xlsx, .xls)
- Try sample data first
- Check file encoding (UTF-8 recommended)

### Issue 5: Query returns error

**Solution:**
- Ensure data is loaded (Step 1 complete)
- Rephrase query more specifically
- Check internet connection (LLM requires API call)
- Verify API key is valid

---

## Testing Checklist

### ✅ Basic Functionality

- [ ] Application launches successfully
- [ ] Sample data uploads without errors
- [ ] Data preview displays correctly
- [ ] Cleaning options appear
- [ ] At least one query executes successfully
- [ ] At least one chart generates
- [ ] PDF report downloads

### ✅ Sample Queries to Test

```
1. What is the total sales amount?
2. How many unique customers are there?
3. Show me sales by product category
4. What is the average order value?
5. Count orders by region
6. Which payment method is most popular?
7. What is the maximum sales amount?
8. Total quantity sold
```

### ✅ Expected Results

| Query | Expected Result Type |
|-------|---------------------|
| Total sales | Single number ~$30,000 |
| Unique customers | Single number (40) |
| Sales by category | Table with 3 rows |
| Average order value | Single number ~$750 |
| Orders by region | Table with 4 rows |

---

## Performance Benchmarks

### Expected Timings (on average laptop)

| Operation | Time |
|-----------|------|
| File Upload (sample data) | <1 second |
| Data Validation | <1 second |
| Cleaning Operation | 1-2 seconds |
| NLQ Query Execution | 2-4 seconds |
| Chart Generation | <1 second |
| PDF Report Generation | 3-5 seconds |

**If operations take significantly longer:**
- Check internet connection (for LLM API)
- Verify system resources (RAM, CPU)
- Try smaller dataset first

---

## Next Steps

### After Successful Testing

1. **Try Your Own Data**
   - Prepare CSV or Excel file
   - Ensure clean column names
   - Keep under 200MB
   - Upload and analyze!

2. **Explore Features**
   - Try different cleaning strategies
   - Ask various types of questions
   - Generate different chart types
   - Customize visualizations

3. **Read Documentation**
   - `docs/ARCHITECTURE.md` - System design
   - `docs/VIVA_GUIDE.md` - Q&A preparation
   - `sample_data/sample_queries.txt` - More query examples

4. **Customize**
   - Modify `utils/config.py` for settings
   - Adjust chart colors, themes
   - Add custom cleaning strategies
   - Extend with new agents

---

## Development Mode

### For Development/Debugging

```bash
# Run with auto-reload
python app.py

# Run on different port
# Windows PowerShell
$env:PORT=8800; python app.py

# macOS/Linux
PORT=8800 python app.py

# Increase upload limit (for larger files)
# Update MAX_FILE_SIZE_MB inside utils/config.py
```

### Viewing Logs

```bash
# Flask development server logs appear in terminal
# INFO lines confirm the server is healthy

# Python tracebacks show in red with stack traces
# Flask error handlers surface JSON payloads in the console
```

---

## Common Use Cases

### Use Case 1: Sales Analysis
```
1. Upload sales data CSV
2. Clean missing values with "Mean"
3. Ask: "Total sales by region"
4. Ask: "Top 10 products by revenue"
5. Generate charts
6. Download PDF report
```

### Use Case 2: HR Analytics
```
1. Upload employee data
2. Clean duplicates
3. Ask: "Average salary by department"
4. Ask: "Count of employees by role"
5. Visualize with bar charts
6. Export report
```

### Use Case 3: Marketing Metrics
```
1. Upload campaign data
2. Handle missing values
3. Ask: "Conversion rate by channel"
4. Ask: "Cost per acquisition"
5. Generate trend lines
6. Share PDF report
```

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.10 - 3.12
- **Internet**: Required for LLM API calls

### Recommended Setup
- **RAM**: 8GB+
- **CPU**: 4 cores
- **SSD**: For faster file operations
- **Browser**: Chrome, Firefox, Safari, Edge (latest)

---

## Getting Help

### Resources

1. **Documentation**
   - README.md - Project overview
   - ARCHITECTURE.md - Technical details
   - VIVA_GUIDE.md - Q&A guide

2. **Sample Files**
   - `sample_data/sales_data.csv` - Test dataset
   - `sample_data/sample_queries.txt` - Query examples

3. **Error Messages**
   - Read error messages carefully
   - Check logs in terminal
   - Verify all prerequisites

### Debug Mode

```python
# Add to agents for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Success Checklist

By the end of this guide, you should have:

- [x] Application running on http://localhost:8000
- [x] Sample data successfully uploaded
- [x] At least one cleaning operation completed
- [x] At least one query executed successfully
- [x] At least one chart generated
- [x] PDF report downloaded and viewable

**If all boxes checked: You're ready to use the system! 🎉**

---

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Deactivate virtual environment
deactivate

# Update packages
pip install --upgrade -r requirements.txt

# Clean cache (optional)
pip cache purge
```

---

**Need more help? Check docs/VIVA_GUIDE.md for detailed Q&A!**
