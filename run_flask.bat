@echo off
REM Flask App Startup Script for Windows

echo.
echo ========================================
echo YouTube Comment Insights - Flask Backend
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')" >nul 2>&1

REM Run Flask app
echo.
echo Starting Flask app on http://localhost:5000
echo Press Ctrl+C to stop
echo.
cd flask_app
python app.py
