# tests/test_queries.py
from sqltodf.engine import DatabaseEngine
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

def test_query_execution()->None:
    load_dotenv()
    config = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_DATABASE": os.getenv("DB_DATABASE"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_CONN_DRIVER": os.getenv("DB_CONN_DRIVER"),
        "JAVA_HOME": os.getenv("JAVA_HOME")
    }

    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)

    # Format the date as "dd-mmm-yyyy"
    formatted_date = yesterday.strftime("%d-%b-%Y")

    # Store it as a string
    formatted_date_str = str(formatted_date.lower())

    engine = DatabaseEngine(config)
    params: dict = {
        "@StartDate@": formatted_date_str,
    }
    current_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(current_dir, "test_query.sql")
    df = engine.query(sql_file_path, **params)

    assert not df.empty

if __name__ == "__main__":
    test_query_execution()