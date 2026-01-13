# Chrome Extension Setup & Troubleshooting Guide

## Prerequisites
1. Flask backend must be running on `http://localhost:5000`
2. Chrome browser (Version 88+)
3. YouTube API key in `popup.js`

## Step 1: Start Flask Backend

Open PowerShell and run:
```powershell
Set-Location "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\flask_app"
python app.py
```

You should see:
```
Model and vectorizer loaded successfully!
 * Running on http://127.0.0.1:5000
```

**Keep this terminal window open while using the extension!**

## Step 2: Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **"Load unpacked"**
4. Navigate to: `c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main\yt-chrome-plugin-frontend`
5. Click "Select Folder"

You should see "YouTube Sentiment Insights" extension loaded.

## Step 3: Test the Extension

1. Go to any YouTube video with comments (e.g., https://www.youtube.com/watch?v=Di7XRPcPuyw)
2. Click the extension icon in Chrome
3. A popup will appear showing analysis

## Troubleshooting

### Problem: "Error fetching sentiment predictions"

**Solution 1: Check Flask is running**
- Look at the Flask terminal - you should see it running on port 5000
- If not running, restart it with the command above

**Solution 2: Check browser console for errors**
1. Right-click popup → Inspect
2. Go to Console tab
3. Look for error messages
4. Take note of any error details

**Solution 3: Verify CORS is enabled**
- Flask app has `CORS(app)` enabled - this should work
- Flask should print request logs when extension calls it

**Solution 4: Hard reload the extension**
1. Go to `chrome://extensions/`
2. Click refresh icon next to "YouTube Sentiment Insights"
3. Try again

### Problem: Extension doesn't appear in Chrome

**Solution:**
1. Go to `chrome://extensions/`
2. Check that "Developer mode" is ON
3. Try "Load unpacked" again and select the folder

### Problem: "Model not loaded" error

**Solution:**
- This means Flask started but couldn't load the model files
- Check that the model exists at: `mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl`
- Restart Flask

### Problem: CORS Error in browser console

**Solution:**
- Chrome extension needs permission for localhost
- manifest.json has been updated with proper host_permissions
- Hard reload the extension

## Debug Tips

### Check Flask is responding
Open PowerShell in a new window:
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing
$response.Content
```

Should print: `Welcome to our flask api`

### Run API tests
```powershell
cd "c:\Users\User\OneDrive\Documents\MSIS_PROJECT-FINAL\MSIS_PROJECT-main"
python test_api.py
```

This will test all endpoints.

### View Flask logs
The Flask terminal shows all requests. Look for:
- `POST /predict_with_timestamps` - sentiment analysis requests
- `POST /detect_languages` - language detection requests
- `POST /generate_chart` - chart generation requests

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port 5000 already in use | `$port = netstat -ano \| findstr :5000` - kill the process or use different port |
| Extension not calling backend | Reload extension and clear browser cache |
| Blank popup | Check console (F12) for errors |
| Slow response | First request may be slow - wait or try again |
| Model load fails | Restart Flask - may need NLTK data: `python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"` |

## API Endpoints

All endpoints available at `http://localhost:5000`:

- `GET /` - Health check
- `POST /predict_with_timestamps` - Sentiment analysis
- `POST /detect_languages` - Language detection
- `POST /generate_chart` - Sentiment pie chart
- `POST /generate_wordcloud` - Comment word cloud
- `POST /generate_trend_graph` - Sentiment trend over time

## Performance Tips

- First analysis takes longer (model loading)
- Subsequent analyses are faster
- Language detection works better with 10+ comments
- For best results, use videos with 100+ comments

## Next Steps

If all is working:
1. Try different YouTube videos
2. Check different languages
3. Monitor Flask terminal for requests
4. Review sentiment predictions accuracy

For deployment to production, see `SETUP_AND_RUN.md` in the flask_app folder.
