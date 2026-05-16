import pandas as pd
import logging
import os

file_log_01 = os.environ.get("FILE_LOG_01")

def read_csv_file():
    try:
        df = pd.read_csv(file_log_01, sep = '\t', encoding='latin1')
        logging.info('File was read successfully.')
        return df
    except FileNotFoundError:
        logging.error("File not found!")
    