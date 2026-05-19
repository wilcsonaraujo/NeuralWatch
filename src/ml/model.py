import logging
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from src.db.database import get_all_metrics
from sklearn.preprocessing import StandardScaler
from pathlib import Path


MODEL_PATH = Path(__file__).parent / "isolation_forest.joblib"
MODEL_SCALER_PATH = Path(__file__).parent / "scaler.joblib"


def prepare_data_for_training():
    metrics_list = get_all_metrics()
    df = pd.DataFrame(metrics_list)

    if df.empty:
        raise ValueError("There is not enough data to train the model.")

    df.drop(["id", "timestamp", "anomaly_detected"], axis=1, inplace=True)
    return df


def train_and_save_model_iso_forest(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df)
    joblib.dump(model, MODEL_PATH)
    return model

def train_and_save_model_scaler(df):
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(df)
    joblib.dump(scaler, MODEL_SCALER_PATH)
    return x_scaled


def predict_anomaly(metrics_dict):
    if not MODEL_PATH.exists():
        logging.warning("Isolation model not found. Skipping anomaly detection.")
        return False
    if not MODEL_SCALER_PATH.exists():
        logging.warning("Scaler model not found. Skipping anomaly detection.")
        return False
    try:
        isolation_model = joblib.load(MODEL_PATH)
        scaler_model = joblib.load(MODEL_SCALER_PATH)

        df = pd.DataFrame([metrics_dict])
        x_scaled = scaler_model.transform(df)

        result = isolation_model.predict(x_scaled)
        return bool(result[0] == -1)
    except Exception as e:
        logging.error(f"Error in anomaly prediction: {e}")
        return False

def run_scaler_model():
    data_df = prepare_data_for_training()
    data_scaler = train_and_save_model_scaler(data_df)
    train_and_save_model_iso_forest(data_scaler)

if __name__ == "__main__":
    run_scaler_model()
    
