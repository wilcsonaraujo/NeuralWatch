import numpy as np
import pandas as pd


def transform_time_features(df):
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    return df


def extract_status_family(df):
    df["status_family"] = df["response"].astype(str).str[0] + "xx"
    return df


def create_is_error(df):
    df["is_error"] = np.where(df["status_family"] == "2xx", 0, 1)
    return df


def create_is_empty_response(df):
    df["is_empty_response"] = np.where(df["bytes"] == 0, 1, 0)
    return df


def convert_bytes_to_kbytes(df):
    df["bytes_kb"] = (df["bytes"] / 1024).round(2)
    return df


def create_endpoint_group(df):
    df["endpoint_group"] = (
        df["url"].str.split("/").str[1].fillna("home").replace("", "home")
    )
    return df
