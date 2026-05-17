import logging
import sqlite3
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    try:
        connection = sqlite3.connect("neuralwatch.db")
        logging.info("Connection established.")
    except sqlite3.OperationalError:
        logging.error("connection failed.")


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
    pass
