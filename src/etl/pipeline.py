import logging
from src.etl.extract import read_csv_file
from src.etl.cleaning import (
    remove_empty_columns,
    remove_duplicates,
    normalize_column_names,
    remove_constant_columns,
)
from src.etl.transform import (
    convert_bytes_to_kbytes,
    create_endpoint_group,
    create_is_empty_response,
    create_is_error,
    extract_status_family,
    transform_time_features,
)


def cleaning_data(df):
    df = (
        df.pipe(remove_empty_columns)
        .pipe(remove_duplicates)
        .pipe(normalize_column_names)
        .pipe(remove_constant_columns)
    )
    logging.info(f"Cleaning success.")
    return df


def transforming_data(df):
    df = (
        df.pipe(transform_time_features)
        .pipe(extract_status_family)
        .pipe(create_is_error)
        .pipe(create_is_empty_response)
        .pipe(convert_bytes_to_kbytes)
        .pipe(create_endpoint_group)
    )
    logging.info(f"Transforming success.")
    return df


def main():
    df = read_csv_file()
    df = df.pipe(cleaning_data).pipe(transforming_data)
