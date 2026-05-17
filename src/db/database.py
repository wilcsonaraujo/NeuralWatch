import datetime
import logging
import sqlite3
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def get_connection():
    try:
        connection = sqlite3.connect("neuralwatch.db")
        logging.info("Connection established.")
        return connection
    except sqlite3.OperationalError:
        logging.error("Connection failed.")


def init_db():
    create_table_sql = """CREATE TABLE IF NOT EXISTS etl_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_requests INTEGER NOT NULL,
        error_rate REAL NOT NULL,
        avg_bytes_kb REAL NOT NULL,
        std_bytes_kb REAL NOT NULL,
        empty_response_rate REAL NOT NULL,
        unique_endpoints INTEGER NOT NULL,
        anomaly_detected INTEGER DEFAULT 0
    );"""

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        logging.info("Table created successfully.")
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        logging.error("Table creation failed.")


def insert_metrics(metrics_dict, db_path="neuralwatch.db"):

    # SQL de inserção
    insert_sql = """
    INSERT INTO neuralwatch (
        timestamp,
        total_requests,
        error_rate,
        avg_bytes_kb,
        std_bytes_kb,
        empty_response_rate,
        unique_endpoints,
        anomaly_detected
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        values = (
            datetime.now(),  # timestamp
            metrics_dict.get("total_requests", 0),  # total_requests
            metrics_dict.get("error_rate", 0.0),  # error_rate
            metrics_dict.get("avg_bytes_kb", 0.0),  # avg_bytes_kb
            metrics_dict.get("std_bytes_kb", 0.0),  # std_bytes_kb
            metrics_dict.get("empty_response_rate", 0.0),  # empty_response_rate
            metrics_dict.get("unique_endpoints", 0),  # unique_endpoints
            metrics_dict.get("anomaly_detected", 0),  # anomaly_detected
        )
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(insert_sql, values)
        logging.info(
            f"Metrics inserted: {metrics_dict.get('total_requests', 0)} requests"
        )
        conn.commit()
        conn.close()
        return True
    except KeyError as e:
        logging.error(f"Missing required field in metrics_dict: {e}")
        return False
    except Exception as e:
        logging.error(f"Error saving metrics: {e}")
        return False


def get_all_metrics(db_path="neuralwatch.db"):
    query = "SELECT * FROM etl_metrics ORDER BY timestamp DESC"

    try:
        conn = get_connection(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]

        return results

    except Exception as e:
        print(f"Consulting error: {e}")
        return pd.DataFrame()
