import joblib
from pathlib import Path
from keras import layers, models

from src.ml.model import prepare_data_for_training, train_and_save_model_scaler

MODEL_SCALER_PATH = Path(__file__).parent / "scaler.joblib"

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
    model.save("src/ml/autoencoder_model.keras")
    return history


if __name__ == "__main__":
    data_df = prepare_data_for_training()
    data_scaler = train_and_save_model_scaler(data_df)
    builded_autoencoder = build_autoencoder(data_df.shape[1], data_df.shape[1]/2)    
    train_autoencoder(builded_autoencoder, data_scaler)
    data_df_after = prepare_data_for_training()