import logging
from src.etl.extract import read_csv_file
from src.etl.cleaning import (remove_empty_columns, 
                              remove_duplicates, 
                              normalize_column_names,
                              remove_constant_columns)

def treat_data():
    df = read_csv_file()
    df = remove_empty_columns(df)
    df = remove_duplicates(df)
    df = normalize_column_names(df)
    df = remove_constant_columns(df)
    logging.info(f"Cleaning success.")
    return df

def main():
    df = treat_data()
    print(df.head(5))
    
if __name__ == "__main__":
    main()