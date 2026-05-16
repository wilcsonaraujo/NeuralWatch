import logging
from src.etl.extract import read_csv_file
from src.etl.cleaning import (remove_empty_columns, 
                              remove_duplicates, 
                              normalize_column_names,
                              remove_constant_columns)
from src.etl.transform import convert_bytes_to_kbytes, create_endpoint_group, create_is_empty_response, create_is_error, extract_status_family, transform_time_features

def cleaning_data():
    df = read_csv_file()
    df = remove_empty_columns(df)
    df = remove_duplicates(df)
    df = normalize_column_names(df)
    df = remove_constant_columns(df)
    logging.info(f"Cleaning success.")
    return df

def transforming_data(df):
    df = transform_time_features(df)
    df = extract_status_family(df)
    df = create_is_error(df)
    df = create_is_empty_response(df)
    df = convert_bytes_to_kbytes(df)
    df = create_endpoint_group(df)
    logging.info(f"Transforming success.")
    return df

def main():
    df = cleaning_data()
    df = transforming_data(df)
    
if __name__ == "__main__":
    main()