import pandas as pd
import logging


def read_csv_file():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    try:
        df = pd.read_csv('data/raw/log_1.tsv', sep = '\t', encoding='latin1')
        logging.info('File was read successfully.')
        return df
    except FileNotFoundError:
        logging.error("File not found!")
    