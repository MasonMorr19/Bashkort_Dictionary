#!/bin/bash
# Bashkir Memory Palace Enhanced Edition - Startup Script

echo "🚀 Starting Bashkir Memory Palace Enhanced Edition..."
echo "=================================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo " activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo " installing dependencies..."
    pip install -r requirements.txt
fi

echo " starting application..."
echo " access the app at: http://localhost:8501"
streamlit run app.py