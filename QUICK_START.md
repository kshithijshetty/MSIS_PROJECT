# Quick Start Guide

## TL;DR - Get it running in 2 minutes

### Terminal 1: Start Flask Backend
```powershell
Set-Location "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\flask_app"
python app.py
```

Wait for: **"Model and vectorizer loaded successfully!"** and **"Running on http://127.0.0.1:5000"**

### Terminal 2 (or Chrome): Load Extension

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (toggle, top-right)
3. Click **"Load unpacked"**
4. Select folder: `c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\yt-chrome-plugin-frontend`
5. Extension appears!

### Test It

1. Go to YouTube: https://www.youtube.com/watch?v=Di7XRPcPuyw
2. Click extension icon
3. Wait for analysis (first time takes 10-15 seconds)
4. See results! 🎉

## Still Getting "Error fetching sentiment predictions"?

### Step 1: Verify Flask is running
Look at Flask terminal - should show: `Running on http://127.0.0.1:5000`

If not, restart it.

### Step 2: Check browser console
1. Right-click extension popup → **Inspect**
2. Click **Console** tab
3. Look for red error messages
4. Take a screenshot if needed

### Step 3: Reload extension
1. Go to `chrome://extensions/`
2. Click refresh ↻ next to "YouTube Sentiment Insights"
3. Try YouTube again

### Step 4: Test API directly
Open PowerShell:
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing
$response.Content
```

Should show: `Welcome to our flask api`

If not → Flask is not running

## What You Should See

### In Flask Terminal
```
Loading model from: C:\Users\User\...\model.pkl
Loading vectorizer from: C:\Users\User\...\tfidf_tmp.pkl
Model and vectorizer loaded successfully!
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

### In Extension Popup
- Video ID
- "Fetched X comments"
- "Performing sentiment analysis..."
- Metrics (Total Comments, Sentiment Score, etc.)
- Sentiment pie chart
- Sentiment trend graph
- **Language distribution pie chart** ← NEW!
- Word cloud
- Top 25 comments with sentiments

## Features

✅ **Sentiment Analysis** - Positive/Negative/Neutral  
✅ **Language Detection** - NEW! Shows what languages commenters use  
✅ **Trend Analysis** - How sentiment changes over time  
✅ **Word Cloud** - Most common words in comments  
✅ **Top Comments** - 25 most recent with sentiments  

## Port Already in Use?

If port 5000 is busy:

```powershell
$PORT=5001 python app.py
```

Then update in `popup.js`:
```javascript
const API_URL = 'http://localhost:5001/';
```

## Still Stuck?

1. **Restart everything:**
   - Close Flask terminal
   - Unload extension from Chrome
   - Reload Flask
   - Reload extension

2. **Check files:**
   - Flask: `flask_app/app.py`
   - Frontend: `yt-chrome-plugin-frontend/popup.js`
   - Manifest: `yt-chrome-plugin-frontend/manifest.json`

3. **Clear cache:**
   - Chrome: Ctrl+Shift+Delete → Clear all
   - Extension: Reload (refresh button)

## Advanced Debugging

### Run API test suite
```powershell
cd "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main"
python test_api.py
```

### View all Flask requests
Flask terminal shows every request:
```
POST /predict_with_timestamps 200 OK
POST /detect_languages 200 OK
```

### Check model files exist
```powershell
ls "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\mlruns\0\0ac12d40a61c40fea07f635b551d4e3b\artifacts\"
```

Should show: `model/` and `vectorizer/`

## What Happens When I Click the Extension?

1. **Extracts YouTube video ID** from URL
2. **Fetches up to 500 comments** from YouTube API
3. **Sends to Flask backend** for analysis
4. **Flask processes:**
   - Detects language of each comment
   - Predicts sentiment (positive/negative/neutral)
   - Generates charts and visualizations
5. **Extension displays** all results

All happens in 10-30 seconds depending on comment count.

## YouTube Video IDs

To test, you need a video WITH comments:
- ✅ Good: https://www.youtube.com/watch?v=Di7XRPcPuyw
- ❌ Bad: Disabled comments or no comments

## Need Help?

1. Check Flask terminal for errors (look for `ERROR` or `Exception`)
2. Check browser console (F12 → Console tab)
3. Run `test_api.py` to verify backend
4. Review `CHROME_EXTENSION_SETUP.md` for detailed troubleshooting

Good luck! 🚀
