# Flask Backend Setup & Troubleshooting

## Prerequisites
Ensure the following files exist in the project root:
- `requirements.txt` - Contains all Python dependencies
- `mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl` - Trained model
- `mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/vectorizer/tfidf_tmp.pkl` - TF-IDF vectorizer

## Step 1: Install Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

Required packages:
- Flask==3.0.3
- Flask-Cors==5.0.0
- numpy==2.1.2
- pandas==2.2.3
- matplotlib==3.9.2
- wordcloud==1.9.3
- nltk==3.9.1
- scikit-learn
- lightgbm==4.5.0
- langdetect==1.0.9

## Step 2: Download NLTK Data

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

## Step 3: Run the Flask App

### Option A: From the flask_app directory
```bash
cd flask_app
python app.py
```

### Option B: From the project root
```bash
python -m flask_app.app
```

The app will run on `http://localhost:5000`

## Common Issues & Solutions

### Error: "No module named 'flask'"
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Error: "lgbm_model.pkl not found"
**Solution**: This is handled automatically. The app will look for models in:
1. `./lgbm_model.pkl` (current directory)
2. `./mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl` (fallback)

### Error: "Connection refused" from Chrome extension
**Solution**: 
1. Make sure Flask app is running: `python app.py`
2. Check if port 5000 is free: `netstat -ano | findstr :5000`
3. Update API_URL in popup.js if using a different port
4. Chrome extension needs permission for http://localhost:*

### NLTK Data Missing
**Error**: `LookupError: Resource stopwords not found`
**Solution**:
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

### Port Already in Use
**Solution**: Use a different port
```bash
PORT=5001 python app.py
```

Then update popup.js:
```javascript
const API_URL = 'http://localhost:5001/';
```

## Verify Flask is Working

Test the endpoints:

```bash
# Test home endpoint
curl http://localhost:5000/

# Test prediction endpoint
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"comments": ["This is great!", "I hate this"]}'

# Test language detection
curl -X POST http://localhost:5000/detect_languages \
  -H "Content-Type: application/json" \
  -d '{"comments": ["This is great!", "Esto es excelente"]}'
```

## Production Deployment

For production, use a proper WSGI server:

```bash
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
```

## Debug Mode

The Flask app runs in debug mode by default. To disable:
1. Edit `app.py` line: `app.run(host='0.0.0.0', port=port, debug=False)`
2. Or set environment variable: `set FLASK_ENV=production`
