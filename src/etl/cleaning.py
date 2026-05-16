import logging


def remove_empty_columns(df):
    if df.isnull().all(axis=0).any():
        logging.info(f"Removing all null values columns.")
        return df.dropna(axis=1, how="all")
    return df


def remove_constant_columns(df):
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    logging.info(f"Removing constant columns: {constant_cols}")
    return df.drop(columns=constant_cols)


def remove_duplicates(df):
    if df.duplicated().any():
        df = df.drop_duplicates()
        logging.info("Removing duplicates.")
        return df
    return df


def normalize_column_names(df):
    df.columns = df.columns.str.strip().str.lower()
    return df
