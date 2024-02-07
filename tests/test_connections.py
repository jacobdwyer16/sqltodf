# tests/test_connections.py
from sqltodf.engine import DatabaseEngine
from dotenv import load_dotenv
import os

def test_pyodbc_connection()->None:
    load_dotenv()
    config = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_DATABASE": os.getenv("DB_DATABASE"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_CONN_DRIVER": os.getenv("DB_CONN_DRIVER")
    }
    engine = DatabaseEngine(config)
    assert engine._database_conn_pyodbc() is not None
