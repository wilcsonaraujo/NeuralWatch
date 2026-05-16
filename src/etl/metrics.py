import logging

import pandas as pd

def count_records(df):
    return len(df)

def error_rate(df):
    error_avg = df['is_error'].mean()
    return error_avg

def avg_bytes_kb(df):
    avg_kbytes = df['bytes_kb'].mean()
    return avg_kbytes

def std_bytes_kb(df):
    std_kbytes = df['bytes_kb'].std()
    return std_kbytes

def empty_response_rate(df):
    response_rate_avg = df['is_empty_response'].mean()
    return response_rate_avg

def unique_endpoints(df):
    count_unique_endpoints = df['endpoint_group'].nunique()
    return count_unique_endpoints

def extract_all_metrics(df):
    metrics_dict = {
        "total_requests": count_records(df),
        "error_rate": error_rate(df),
        "avg_bytes_kb": avg_bytes_kb(df),
        "std_bytes_kb": std_bytes_kb(df),
        "empty_response_rate": empty_response_rate(df),
        "unique_endpoints": unique_endpoints(df)
    }
    logging.info("Extracted metrics successfully.")
    return metrics_dict