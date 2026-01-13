# Flask Backend - Setup Complete ✅

## Status: READY TO USE

Your Flask backend is now running successfully on **http://localhost:5000**

### ✅ What's Working:
- Flask app is running
- Model loaded successfully from: `mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl`
- Vectorizer loaded successfully from: `mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/vectorizer/tfidf_tmp.pkl`
- All dependencies installed
- NLTK data downloaded
- Language detection feature implemented

### ⚠️ Version Warnings (Normal):
You may see scikit-learn version warnings (1.7.2 vs 1.6.1). These are compatibility warnings but **do not prevent the model from working correctly**.

### 🔧 Available Endpoints:

1. **POST /predict_with_timestamps**
   - Predicts sentiment for comments with timestamps
   - Expected input: `{"comments": [{"text": "...", "timestamp": "..."}, ...]}`
   - Response: `[{"comment": "...", "sentiment": "-1/0/1", "timestamp": "..."}, ...]`

2. **POST /generate_chart**
   - Generates sentiment pie chart
   - Expected input: `{"sentiment_counts": {"1": N, "0": N, "-1": N}}`
   - Response: PNG image

3. **POST /generate_wordcloud**
   - Generates word cloud from comments
   - Expected input: `{"comments": ["comment1", "comment2", ...]}`
   - Response: PNG image

4. **POST /generate_trend_graph**
   - Generates sentiment trend over time
   - Expected input: `{"sentiment_data": [{"timestamp": "...", "sentiment": 1}, ...]}`
   - Response: PNG image

5. **POST /detect_languages** (NEW)
   - Detects language distribution of comments
   - Expected input: `{"comments": ["comment1", "comment2", ...]}`
   - Response: PNG pie chart showing language distribution

### 🚀 How to Use with Chrome Extension:

1. ✅ Flask backend is running
2. Open Chrome and navigate to a YouTube video
3. Click the YouTube Sentiment Insights extension
4. Paste the video ID: **Di7XRPcPuyw** (or use current video)
5. The plugin will:
   - Fetch YouTube comments
   - Send them to Flask for sentiment analysis
   - Display results with charts

### 📋 To Keep Flask Running:

**Option 1: Keep terminal open**
- Flask runs in terminal at: `C:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\flask_app`
- Press Ctrl+C to stop

**Option 2: Quick restart (run from project root)**
```powershell
cd "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\flask_app"
python app.py
```

**Option 3: Use batch script (Windows)**
```batch
run_flask.bat
```

**Option 4: Use PowerShell script (Windows)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\run_flask.ps1
```

### 🧪 Test Endpoints:

**Test in PowerShell:**
```powershell
# Test home endpoint
curl http://localhost:5000/

# Test sentiment prediction
$body = @{comments = @(@{text = "This is great!"; timestamp = "2025-01-12T00:00:00Z"}, @{text = "This is bad"; timestamp = "2025-01-12T00:01:00Z"})} | ConvertTo-Json
curl -Method POST -Uri http://localhost:5000/predict_with_timestamps -Body $body -ContentType "application/json"

# Test language detection  
$body = @{comments = @("This is great!", "Esto es excelente", "C'est magnifique")} | ConvertTo-Json
curl -Method POST -Uri http://localhost:5000/detect_languages -Body $body -ContentType "application/json"
```

### 📝 Recent Changes Made:

1. **Fixed Model Loading**: Now correctly finds model files from mlruns directory
2. **Added Language Detection**: New `/detect_languages` endpoint with pie chart
3. **Better Error Handling**: Clear messages if model fails to load
4. **Cross-Directory Support**: Works whether running from flask_app or project root
5. **NLTK Data**: Automatically installed

### 🐛 If You Get Errors:

1. **"Connection refused"**: Flask not running. Run `python app.py` in flask_app directory
2. **"Model not loaded"**: Restart Flask. Check file paths in output
3. **"NLTK data missing"**: Run `python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"`
4. **"Port 5000 in use"**: Change port or kill process: `Get-Process python | Stop-Process -Force`

### ✨ You're All Set!

The backend is ready. Your Chrome extension can now connect and analyze YouTube comments with:
- Sentiment analysis
- Word clouds
- Trend graphs
- Language detection
- Comment metrics

Enjoy analyzing YouTube comments! 🎉
