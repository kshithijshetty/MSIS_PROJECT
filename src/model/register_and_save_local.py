import os
import pickle
import mlflow
import mlflow.sklearn
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


logger = logging.getLogger('register_and_save_local')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_tracking_uri():
    return os.getenv(
        "MLFLOW_TRACKING_URI",
        f"file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mlruns'))}"
    )


def create_and_train():
    # small synthetic dataset
    comments = [
        "I love this video, very helpful!",
        "Terrible explanation, I didn't like it",
        "Not bad, but could be better",
        "Excellent content and clear presentation",
        "Poor audio and bad pacing",
        "I have mixed feelings about this video",
        "Amazing tutorial, thanks!",
        "Waste of time, very boring"
    ]
    # labels: 1 -> Positive, 0 -> Neutral, -1 -> Negative
    labels = [1, -1, 0, 1, -1, 0, 1, -1]

    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(comments)
    y = labels

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=42)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    return model, vectorizer


def save_pickles(model, vectorizer, root_dir):
    model_path = os.path.join(root_dir, 'lgbm_model.pkl')
    vec_path = os.path.join(root_dir, 'tfidf_vectorizer.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(vec_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    logger.info(f"Saved model to {model_path} and vectorizer to {vec_path}")
    return model_path, vec_path


def log_to_mlflow(model, vectorizer, model_name='yt_chrome_plugin_model'):
    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    logger.info(f"Using MLflow tracking URI: {tracking_uri}")

    with mlflow.start_run() as run:
        run_id = run.info.run_id
        logger.info(f"Started MLflow run {run_id}")

        # Log sklearn model
        try:
            mlflow.sklearn.log_model(model, artifact_path='model')
            # Save vectorizer to temporary file and log as artifact
            tmp_vec = os.path.join(os.getcwd(), 'tfidf_tmp.pkl')
            with open(tmp_vec, 'wb') as f:
                pickle.dump(vectorizer, f)
            mlflow.log_artifact(tmp_vec, artifact_path='vectorizer')
            os.remove(tmp_vec)

            logger.info('Logged model and vectorizer to MLflow')

            # Attempt to register model in model registry
            model_uri = f"runs:/{run_id}/model"
            try:
                mv = mlflow.register_model(model_uri, model_name)
                logger.info(f"Registered model {model_name} version {mv.version}")
            except Exception as e:
                logger.warning(f"Model registration failed or registry unavailable: {e}")

        except Exception as e:
            logger.error(f"Failed to log model to MLflow: {e}")


if __name__ == '__main__':
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    model, vec = create_and_train()
    save_pickles(model, vec, root)
    log_to_mlflow(model, vec)
