import json
import logging
import joblib
from pathlib import Path
from keras import layers, models
import numpy as np
import pandas as pd
import tensorflow as tf
from src.ml.model import prepare_data_for_training, train_and_save_model_scaler

MODEL_SCALER_PATH = Path(__file__).parent / "scaler.joblib"
MODEL_AUTOENCODER_PATH = Path(__file__).parent / "autoencoder_model.keras"
THRESHOLD_PATH = Path(__file__).parent / "threshold.json"


def build_autoencoder(input_dim, encoding_dim):
    input_layer = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(encoding_dim, activation="relu")(input_layer)
    decoded = layers.Dense(input_dim, activation="linear")(encoded)
    autoencoder = models.Model(input_layer, decoded)
    autoencoder.compile(loss="mean_squared_error", optimizer="adam", metrics=["mse"])
    return autoencoder


def train_autoencoder(model, data):
    model.fit(data, data, epochs=50, batch_size=32, shuffle=True, validation_split=0.2)
    model.save(MODEL_AUTOENCODER_PATH)
    return model


def predict_anomaly_autoencoder(metrics_dict, threshold):
    if not MODEL_AUTOENCODER_PATH.exists():
        logging.warning("Autoencoder model not found. Skipping anomaly detection.")
        return False
    if not MODEL_SCALER_PATH.exists():
        logging.warning("IScaler model not found. Skipping anomaly detection.")
        return False

    try:
        autoencoder_model = tf.keras.models.load_model(MODEL_AUTOENCODER_PATH)
        scaler_model = joblib.load(MODEL_SCALER_PATH)

        df = pd.DataFrame([metrics_dict])
        x_scaled = scaler_model.transform(df)

        X_reconstructed = autoencoder_model.predict(x_scaled)
        mse = np.mean(np.power(x_scaled - X_reconstructed, 2), axis=1)

        error = mse[0]
        is_anomaly = error > threshold

        return int(is_anomaly)
    except Exception as e:
        logging.error(f"Error in anomaly prediction: {e}")
        return False


def calculate_threshold(model, scaled_data):
    try:
        reconstructed_data = model.predict(scaled_data)
        mse = np.mean(np.power(scaled_data - reconstructed_data, 2), axis=1)

        threshold = np.percentile(mse, 95)
        return threshold

    except Exception as e:
        logging.error(f"Error in threshold calculation: {e}")
        return False


def save_threshold(threshold_value):
    with open(THRESHOLD_PATH, "w", encoding="utf-8") as file:
        json.dump(threshold_value, file, indent=4, ensure_ascii=False)
        logging.info("Threshold json created.")


def load_threshold():
    if not THRESHOLD_PATH.exists():
        logging.warning("Threshold file not found. Using default value 0.1")
        return 0.1

    try:
        with open(THRESHOLD_PATH, "r", encoding="utf-8") as file:
            threshold_value = json.load(file)
            return float(threshold_value)
    except Exception as e:
        logging.error(f"Error loading threshold: {e}")
        return 0.1


def run_autoencoder_model():
    data_df = prepare_data_for_training()
    data_scaler = train_and_save_model_scaler(data_df)
    builded_autoencoder = build_autoencoder(data_df.shape[1], int(data_df.shape[1] / 2))
    train_autoencoder(builded_autoencoder, data_scaler)

    autoencoder_model = tf.keras.models.load_model(MODEL_AUTOENCODER_PATH)
    threshold_value = calculate_threshold(autoencoder_model, data_scaler)
    save_threshold(threshold_value)


if __name__ == "__main__":
    run_autoencoder_model()
