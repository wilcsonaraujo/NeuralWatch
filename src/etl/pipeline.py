import logging
from src.db.database import init_db, insert_metrics
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
from src.ml.model import get_prediction


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
    init_db()

    if df is None or df.empty:
        logging.error("DataFrame empty or not loaded.")
        return None

    df = df.pipe(inject_chaos).pipe(cleaning_data).pipe(transforming_data)

    metrics_dict = extract_all_metrics(df)
    is_anomaly = get_prediction(metrics_dict)
    metrics_dict["anomaly_detected"] = is_anomaly
    insert_metrics(metrics_dict)
    return metrics_dict


def pipeline():
    #run_pipeline()
    for i in range(15):
        run_pipeline()


if __name__ == "__main__":
    pipeline()
