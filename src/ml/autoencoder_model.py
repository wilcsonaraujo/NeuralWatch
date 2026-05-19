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
    autoencoder.compile(loss="mean_squared_error", optimizer="adam", metrics="mse")
    return autoencoder


def train_autoencoder(model, data):
    history = model.fit(
        data, data, epochs=50, batch_size=32, shuffle=True, validation_split=0.2
    )
    model.save(MODEL_AUTOENCODER_PATH)
    return history


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
        mse = tf.keras.losses.mean_squared_error(x_scaled, X_reconstructed)

        error = mse.numpy()[0]
        is_anomaly = error > threshold

        return is_anomaly
    except Exception as e:
        logging.error(f"Error in anomaly prediction: {e}")
        return False

def calculate_threshold(model, scaled_data):
    try:
        reconstructed_data  = model.predict(scaled_data)
        mse = np.mean(np.power(scaled_data - reconstructed_data, 2), axis=1)
        errors = mse.numpy()

        threshold = np.percentile(errors, 95)
        print(f"\n🎯 Limiar (percentil 95%): {threshold:.6f}")
        print(f"   → 95% dos dados têm erro <= {threshold:.6f}")
        print(f"   → 95% dos dados são considerados anomalias")
        return threshold, errors
    
    except Exception as e:
        logging.error(f"Error in threshold calculation: {e}")
        return False
    
def save_threshold(threshold_value):
    if not THRESHOLD_PATH.exists():
        with open(THRESHOLD_PATH, "w", encoding="utf-8") as file:
            json.dump(threshold_value, file, indent=4, ensure_ascii=False)
            logging.warning("Threshold json created or rewritten.")
            

if __name__ == "__main__":
    data_df = prepare_data_for_training()
    data_scaler = train_and_save_model_scaler(data_df)
    builded_autoencoder = build_autoencoder(data_df.shape[1], int(data_df.shape[1] / 2))
    model = train_autoencoder(builded_autoencoder, data_scaler)
    threshold_value = calculate_threshold(model, data_scaler)
    save_threshold(threshold_value)
