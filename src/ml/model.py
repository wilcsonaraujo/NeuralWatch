import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from src.db.database import get_all_metrics


def prepare_data_for_training():
    metrics_list = get_all_metrics()
    df = pd.DataFrame(metrics_list)

    if df.empty:
        raise ValueError("There is not enough data to train the model.")

    df.drop(["id", "timestamp", "anomaly_detected"], axis=1, inplace=True)
    return df


def train_and_save_model(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df)
    joblib.dump(model, "isolation_forest.joblib")
    return model

def predict_anomaly(metrics_dict):
    model = joblib.load("isolation_forest.joblib")
    df = pd.DataFrame([metrics_dict])
    result = model.predict(df)
    return bool(result[0] == -1)

def model():
    data_df = prepare_data_for_training()
    train_and_save_model(data_df)
    print(data_df.head(20))


if __name__ == "__main__":
    model()
