# Flask App Startup Script for PowerShell

Write-Host "========================================"
Write-Host "YouTube Comment Insights - Flask Backend"
Write-Host "========================================"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion"
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the correct directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory"
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Download NLTK data
Write-Host ""
Write-Host "Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')" 2>$null

# Run Flask app
Write-Host ""
Write-Host "Starting Flask app on http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop"
Write-Host ""

Set-Location flask_app
python app.py
