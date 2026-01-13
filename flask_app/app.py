import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend before importing pyplot

import warnings
warnings.filterwarnings('ignore')

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import re
import pickle
import os
import sys

# Import heavy dependencies upfront with warnings suppressed
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from langdetect import detect, DetectorFactory
import matplotlib.dates as mdates
import pandas as pd

# Set seed for language detection consistency
DetectorFactory.seed = 0

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup error logging
import logging
from logging.handlers import RotatingFileHandler
if not app.debug:
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/app_errors.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Define the preprocessing function
def preprocess_comment(comment):
    """Apply preprocessing transformations to a comment."""
    try:
        # Convert to lowercase
        comment = comment.lower()

        # Remove trailing and leading whitespaces
        comment = comment.strip()

        # Remove newline characters
        comment = re.sub(r'\n', ' ', comment)

        # Remove non-alphanumeric characters, except punctuation
        comment = re.sub(r'[^A-Za-z0-9\s!?.,]', '', comment)

        # Remove stopwords but retain important ones for sentiment analysis
        stop_words = set(stopwords.words('english')) - {'not', 'but', 'however', 'no', 'yet'}
        comment = ' '.join([word for word in comment.split() if word not in stop_words])

        # Lemmatize the words
        lemmatizer = WordNetLemmatizer()
        comment = ' '.join([lemmatizer.lemmatize(word) for word in comment.split()])

        return comment
    except Exception as e:
        print(f"Error in preprocessing comment: {e}")
        return comment


def simple_sentiment_check(comment):
    """Simple rule-based sentiment check as a fallback."""
    comment_lower = comment.lower()
    
    # Negative indicators
    negative_words = {'hate', 'bad', 'terrible', 'horrible', 'awful', 'worst', 'disgusting', 
                      'poor', 'pathetic', 'disappointing', 'stupid', 'garbage', 'trash',
                      'waste', 'useless', 'boring', 'cringe', 'sucks', 'trash', 'disaster'}
    # Positive indicators  
    positive_words = {'love', 'great', 'amazing', 'awesome', 'excellent', 'fantastic', 
                      'wonderful', 'best', 'good', 'beautiful', 'perfect', 'brilliant',
                      'incredible', 'awesome', 'superb', 'outstanding'}
    
    negative_count = sum(1 for word in negative_words if word in comment_lower)
    positive_count = sum(1 for word in positive_words if word in comment_lower)
    
    if negative_count > positive_count and negative_count > 0:
        return -1
    elif positive_count > negative_count and positive_count > 0:
        return 1
    else:
        return 0  # neutral



# Load the model and vectorizer from the model registry and local storage
# def load_model_and_vectorizer(model_name, model_version, vectorizer_path):
#     # Set MLflow tracking URI to your server
#     mlflow.set_tracking_uri("http://ec2-54-167-108-249.compute-1.amazonaws.com:5000/")  # Replace with your MLflow tracking URI
#     client = MlflowClient()
#     model_uri = f"models:/{model_name}/{model_version}"
#     model = mlflow.pyfunc.load_model(model_uri)
#     with open(vectorizer_path, 'rb') as file:
#         vectorizer = pickle.load(file)
   
#     return model, vectorizer



def load_model(model_path, vectorizer_path):
    """Load the trained model."""
    import os
    try:
        # Get the directory where this app.py file is located
        app_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(app_dir)
        
        # Check if files exist in current directory first
        if not os.path.exists(model_path):
            # Try relative to project root (when running from flask_app dir)
            model_path = os.path.join(project_root, "mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl")
        if not os.path.exists(vectorizer_path):
            # Try relative to project root (when running from flask_app dir)
            vectorizer_path = os.path.join(project_root, "mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/vectorizer/tfidf_tmp.pkl")
        
        print(f"Loading model from: {model_path}")
        print(f"Loading vectorizer from: {vectorizer_path}")
        
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        
        with open(vectorizer_path, 'rb') as file:
            vectorizer = pickle.load(file)
        
        print("Model and vectorizer loaded successfully!")
        return model, vectorizer
    except Exception as e:
        print(f"Error loading model: {e}")
        raise


# Initialize the model and vectorizer
model = None
vectorizer = None
try:
    model, vectorizer = load_model("../mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/model/model.pkl", "../mlruns/0/0ac12d40a61c40fea07f635b551d4e3b/artifacts/vectorizer/tfidf_tmp.pkl")
except Exception as e:
    print(f"Failed to load model: {e}")
    print("The app will still start, but prediction endpoints will fail")  

# Initialize the model and vectorizer
# model, vectorizer = load_model_and_vectorizer("my_model", "1", "./tfidf_vectorizer.pkl")  # Update paths and versions as needed

@app.route('/')
def home():
    return "Welcome to our flask api"



@app.route('/predict_with_timestamps', methods=['POST', 'OPTIONS'])
def predict_with_timestamps():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    if model is None or vectorizer is None:
        return jsonify({"error": "Model not loaded. Please restart the Flask app."}), 500
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        comments_data = data.get('comments')
        
        if not comments_data:
            return jsonify({"error": "No comments provided"}), 400

        comments = [item['text'] for item in comments_data]
        timestamps = [item['timestamp'] for item in comments_data]

        # Preprocess each comment before vectorizing
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]
        
        # Transform comments using the vectorizer
        transformed_comments = vectorizer.transform(preprocessed_comments)

        # Convert the sparse matrix to dense format
        dense_comments = transformed_comments.toarray()  # Convert to dense array
        
        # Make predictions with model
        model_predictions = model.predict(dense_comments).tolist()  # Convert to list
        
        # Convert predictions to strings and enhance with simple sentiment check
        predictions = []
        for i, (comment, model_pred) in enumerate(zip(comments, model_predictions)):
            # If model predicts all positive, try rule-based check
            model_sentiment = int(model_pred)
            if model_sentiment == 1:
                # Use rule-based check to see if it's actually negative
                rule_sentiment = simple_sentiment_check(comment)
                final_sentiment = rule_sentiment if rule_sentiment != 0 else 1
            else:
                final_sentiment = model_sentiment
            predictions.append(str(final_sentiment))
    except Exception as e:
        app.logger.error(f"Error in predict_with_timestamps: {str(e)}", exc_info=True)
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    # Return the response with original comments, predicted sentiments, and timestamps
    response = [{"comment": comment, "sentiment": sentiment, "timestamp": timestamp} for comment, sentiment, timestamp in zip(comments, predictions, timestamps)]
    return jsonify(response)



@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    comments = data.get('comments')
    print("i am the comment: ",comments)
    print("i am the comment type: ",type(comments))
    
    if not comments:
        return jsonify({"error": "No comments provided"}), 400

    try:
        # Preprocess each comment before vectorizing
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]
        
        # Transform comments using the vectorizer
        transformed_comments = vectorizer.transform(preprocessed_comments)

        # Convert the sparse matrix to dense format
        dense_comments = transformed_comments.toarray()  # Convert to dense array
        
        # Make predictions
        predictions = model.predict(dense_comments).tolist()  # Convert to list
        
        # Convert predictions to strings for consistency
        # predictions = [str(pred) for pred in predictions]
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    # Return the response with original comments and predicted sentiments
    response = [{"comment": comment, "sentiment": sentiment} for comment, sentiment in zip(comments, predictions)]
    return jsonify(response)



@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    try:
        data = request.get_json()
        sentiment_counts = data.get('sentiment_counts')
        
        if not sentiment_counts:
            return jsonify({"error": "No sentiment counts provided"}), 400

        # Prepare data for the pie chart
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [
            int(sentiment_counts.get('1', 0)),
            int(sentiment_counts.get('0', 0)),
            int(sentiment_counts.get('-1', 0))
        ]
        if sum(sizes) == 0:
            raise ValueError("Sentiment counts sum to zero")
        
        colors = ['#36A2EB', '#C9CBCF', '#FF6384']  # Blue, Gray, Red

        # Generate the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': 'w'}
        )
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the chart to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG', transparent=True)
        img_io.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_chart: {e}")
        return jsonify({"error": f"Chart generation failed: {str(e)}"}), 500

@app.route('/generate_wordcloud', methods=['POST'])
def generate_wordcloud():
    try:
        data = request.get_json()
        comments = data.get('comments')

        if not comments:
            return jsonify({"error": "No comments provided"}), 400

        # Preprocess comments
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]

        # Combine all comments into a single string
        text = ' '.join(preprocessed_comments)

        # Generate the word cloud
        wordcloud_obj = WordCloud(
            width=800,
            height=400,
            background_color='black',
            colormap='Blues',
            stopwords=set(stopwords.words('english')),
            collocations=False
        ).generate(text)

        # Save the word cloud to a BytesIO object
        img_io = io.BytesIO()
        wordcloud_obj.to_image().save(img_io, format='PNG')
        img_io.seek(0)

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_wordcloud: {e}")
        return jsonify({"error": f"Word cloud generation failed: {str(e)}"}), 500

@app.route('/generate_trend_graph', methods=['POST'])
def generate_trend_graph():
    try:
        data = request.get_json()
        sentiment_data = data.get('sentiment_data')

        if not sentiment_data:
            return jsonify({"error": "No sentiment data provided"}), 400

        # Convert sentiment_data to DataFrame
        df = pd.DataFrame(sentiment_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Set the timestamp as the index
        df.set_index('timestamp', inplace=True)

        # Ensure the 'sentiment' column is numeric
        df['sentiment'] = df['sentiment'].astype(int)

        # Map sentiment values to labels
        sentiment_labels = {-1: 'Negative', 0: 'Neutral', 1: 'Positive'}

        # Resample the data over monthly intervals and count sentiments
        monthly_counts = df.resample('M')['sentiment'].value_counts().unstack(fill_value=0)

        # Calculate total counts per month
        monthly_totals = monthly_counts.sum(axis=1)

        # Calculate percentages
        monthly_percentages = (monthly_counts.T / monthly_totals).T * 100

        # Ensure all sentiment columns are present
        for sentiment_value in [-1, 0, 1]:
            if sentiment_value not in monthly_percentages.columns:
                monthly_percentages[sentiment_value] = 0

        # Sort columns by sentiment value
        monthly_percentages = monthly_percentages[[-1, 0, 1]]

        # Plotting
        plt.figure(figsize=(12, 6))

        colors = {
            -1: 'red',     # Negative sentiment
            0: 'gray',     # Neutral sentiment
            1: 'green'     # Positive sentiment
        }

        for sentiment_value in [-1, 0, 1]:
            plt.plot(
                monthly_percentages.index,
                monthly_percentages[sentiment_value],
                marker='o',
                linestyle='-',
                label=sentiment_labels[sentiment_value],
                color=colors[sentiment_value]
            )

        plt.title('Monthly Sentiment Percentage Over Time')
        plt.xlabel('Month')
        plt.ylabel('Percentage of Comments (%)')
        plt.grid(True)
        plt.xticks(rotation=45)

        # Format the x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))

        plt.legend()
        plt.tight_layout()

        # Save the trend graph to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG')
        img_io.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /generate_trend_graph: {e}")
        return jsonify({"error": f"Trend graph generation failed: {str(e)}"}), 500


@app.route('/detect_languages', methods=['POST'])
def detect_languages():
    """Detect languages in comments and generate a language distribution chart."""
    try:
        data = request.get_json()
        comments = data.get('comments', [])
        
        if not comments:
            return jsonify({"error": "No comments provided"}), 400

        # Detect language for each comment
        language_counts = {}
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'id': 'Indonesian',
            'fil': 'Filipino'
        }
        
        for comment in comments:
            try:
                if comment.strip():  # Only detect if comment is not empty
                    lang = detect(comment)
                    language_counts[lang] = language_counts.get(lang, 0) + 1
            except Exception as e:
                # If language detection fails, count as 'unknown'
                language_counts['unknown'] = language_counts.get('unknown', 0) + 1
        
        if not language_counts:
            return jsonify({"error": "Could not detect languages"}), 400
        
        # Prepare data for the pie chart
        labels = [language_names.get(lang, lang.upper()) for lang in language_counts.keys()]
        sizes = list(language_counts.values())
        
        # Generate pie chart
        plt.figure(figsize=(8, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': 'w', 'fontsize': 10}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        plt.title('Language Distribution in Comments', color='w', fontsize=14, fontweight='bold')
        plt.axis('equal')
        
        # Save the chart to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG', transparent=True, bbox_inches='tight')
        img_io.seek(0)
        plt.close()
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /detect_languages: {e}")
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 500


if __name__ == '__main__':
    # Allow overriding port with env var `PORT` (useful to avoid conflicts)
    print("Starting Flask app...")
    sys.stdout.flush()
    port = int(os.getenv('PORT', '5000'))
    print(f"Port: {port}")
    sys.stdout.flush()
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=False)
    except Exception as e:
        print(f"Error starting Flask: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
