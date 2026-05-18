import joblib
from pathlib import Path
from keras import layers, models
import numpy as np
import pandas as pd
import tensorflow as tf
from src.ml.model import prepare_data_for_training, train_and_save_model_scaler

MODEL_SCALER_PATH = Path(__file__).parent / "scaler.joblib"
MODEL_AUTOENCODER_PATH = Path(__file__).parent / "autoencoder_model.keras"

def build_autoencoder(input_dim, encoding_dim):
    input_layer = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(encoding_dim, activation='relu')(input_layer)
    decoded = layers.Dense(input_dim, activation='linear')(encoded)
    autoencoder = models.Model(input_layer, decoded)
    autoencoder.compile(loss='mean_squared_error', optimizer='adam', metrics='mse')
    return autoencoder

def train_autoencoder(model, data):
    history = model.fit(
        data, data,
        epochs=50,
        batch_size=32,
        shuffle=True,
        validation_split=0.2
    )
    model.save(MODEL_AUTOENCODER_PATH)
    return history

def predict_anomaly_autoencoder(metrics_dict, threshold):
    autoencoder_model = tf.keras.models.load_model(MODEL_AUTOENCODER_PATH)
    scaler_model =joblib.load(MODEL_SCALER_PATH)

    df = pd.DataFrame([metrics_dict])
    x_scaled = scaler_model.transform(df)

    X_reconstructed = autoencoder_model.predict(x_scaled)
    mse = tf.keras.losses.mean_squared_error(x_scaled, X_reconstructed)
    errors = tf.keras.losses.mean_squared_error(x_scaled, X_reconstructed).numpy()

    threshold = np.percentile(errors, 95)
    is_anomaly = errors > threshold
    return is_anomaly

def autoencoder():
    data_df = prepare_data_for_training()
    data_scaler = train_and_save_model_scaler(data_df)
    builded_autoencoder = build_autoencoder(data_df.shape[1], int(data_df.shape[1]/2))    
    train_autoencoder(builded_autoencoder, data_scaler)
    return 

if __name__ == "__main__":
    autoencoder()