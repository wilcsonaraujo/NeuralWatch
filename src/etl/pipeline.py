import logging
from src.db.database import get_connection
from src.etl.chaos import inject_chaos
from src.etl.extract import read_csv_file
from src.etl.cleaning import (
    remove_empty_columns,
    remove_duplicates,
    normalize_column_names,
    remove_constant_columns,
)
from src.etl.metrics import extract_all_metrics
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


def run_pipeline():
    df = read_csv_file()
    get_connection()

    if df is None or df.empty:
        logging.error("DataFrame empty or not loaded.")
        print("DataFrame empty or not loaded")
        return None

    df = inject_chaos(df)

    df = cleaning_data(df)
    df = transforming_data(df)

    metrics_dict = extract_all_metrics(df)
    return metrics_dict


def main():
    metrics = run_pipeline()
    if metrics:
        print(metrics)


if __name__ == "__main__":
    main()
