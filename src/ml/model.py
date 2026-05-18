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
    scaler.fit_transform(df)
    joblib.dump(scaler, MODEL_SCALER_PATH)
    return scaler


def predict_anomaly(metrics_dict):
    if not MODEL_SCALER_PATH.exists():
        logging.warning("Model not found. Skipping anomaly detection.")
        return False
    model = joblib.load(MODEL_SCALER_PATH)
    df = pd.DataFrame([metrics_dict])
    result = model.predict(df)
    return bool(result[0] == -1)


def train_isolation_forest_script(data_df):
    train_and_save_model_iso_forest(data_df)

def train_stantard_scaler_script(data_df):
    train_and_save_model_scaler(data_df)

if __name__ == "__main__":
    data_df = prepare_data_for_training()
    train_isolation_forest_script(data_df)
    train_stantard_scaler_script(data_df)
