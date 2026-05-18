import pandas as pd
import tensorflow as tf
from keras import layers, models

def build_autoencoder(input_dim, encoding_dim):
    input_layer = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(encoding_dim, activation='relu')(input_layer)
    decoded = layers.Dense(input_dim, activation='linear')(encoded)
    autoencoder = models.Model(input_layer, decoded)
    return autoencoder