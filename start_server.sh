#!/bin/bash
# Startup script for Farm Connect backend with authentication

set -e

echo "🚀 Starting Farm Connect Backend..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import jose" 2>/dev/null || {
    echo "❌ python-jose not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Navigate to server directory
cd server

# Start uvicorn
echo "✅ Starting uvicorn server..."
echo "📍 API will be available at: http://127.0.0.1:8000"
echo "📚 API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
