import pandas as pd
import joblib as joblib
from sklearn.ensemble import IsolationForest
from src.db.database import get_all_metrics


def prepare_data_for_training():
    metrics_list = get_all_metrics()
    df = pd.DataFrame(metrics_list)
    df.drop(['id', 'timestamp', 'anomaly_detected'], axis=1, inplace=True)
    return df

def train_and_save_model(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df)
    joblib.dump(model, "isolation_forest.joblib")

def main():
    data_df = prepare_data_for_training()
    train_and_save_model(data_df)
    """ for i in range(30):
        metrics = run_pipeline() """
    print(data_df.head(5))


if __name__ == "__main__":
    main()
