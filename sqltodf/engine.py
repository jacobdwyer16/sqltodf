import logging
import os
import re
from pathlib import Path
from typing import Any, Optional, Tuple

import jaydebeapi
import pandas as pd
import polars as pl
import pyodbc
from pydantic import BaseModel, ValidationError


class DatabaseConfig(BaseModel):
    DB_CONN_DRIVER: str
    DB_HOST: str = "localhost"
    DB_PORT: int
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    JAVA_HOME: str | None = None


class DatabaseEngine:
    def __init__(
        self, config_data: dict, logger: Optional[logging.Logger] = None
    ) -> None:
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.logger.info("Initializing DatabaseEngine")
        try:
            config = DatabaseConfig(**config_data)
        except ValidationError as e:
            self.logger.error("Configuration validation error: %s", e)
            raise RuntimeError("Invalid configuration provided") from e

        self.__db_conn_driver = config.DB_CONN_DRIVER
        self.__db_host = config.DB_HOST
        self.__db_port = config.DB_PORT
        self.__db_database = config.DB_DATABASE
        self.__db_user = config.DB_USER
        self.__db_password = config.DB_PASSWORD
        self.__db_driver = config.DB_CONN_DRIVER
        self.__java_home = config.JAVA_HOME
        self.connection = None

    def _database_conn_pyodbc(self) -> str:
        return f"DRIVER={self.__db_conn_driver};SERVER={self.__db_host},{self.__db_port};DATABASE={self.__db_database};UID={self.__db_user};PWD={self.__db_password}"

    def _database_uri_pyodbc(self) -> str:
        return f"{self.__db_conn_driver}://{self.__db_user}:{self.__db_password}@{self.__db_host}:{self.__db_port}/{self.__db_driver}"

    def _database_conn_jaydebeapi(
        self, driver_class: str | None = None, jdbc_url: str | None = None
    ) -> jaydebeapi.Connection:
        jar_file = Path(__file__).parent / "jars" / "mssql-jdbc-12.4.2.jre8.jar"
        if not jar_file.exists():
            self.logger.error("JDBC driver JAR file not found.")
            raise FileNotFoundError("JDBC driver JAR file not found.")

        if driver_class is None:
            driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

        if jdbc_url is None:
            # THIS REQUIRES REVERTING TO AN OLD TLS VERSION
            # USE AT YOUR OWN RISK
            jdbc_url = f"jdbc:sqlserver://{self.__db_host}:{self.__db_port};databaseName={self.__db_database};encrypt=true;trustServerCertificate=true;sslProtocol=TLSv1;"

        return jaydebeapi.connect(
            driver_class,
            jdbc_url,
            {"user": self.__db_user, "password": self.__db_password},
            str(jar_file),
        )

    @staticmethod
    def load_sql(sql_file_path: str) -> str:
        with open(sql_file_path, "r") as f:
            return f.read()

    @staticmethod
    def query_checker(query: str) -> Tuple[bool, str]:
        # list of patterns for potentially unsafe SQL operations
        unsafe_patterns = [
            r"\b(ALTER|CREATE|DROP|EXECUTE|DELETE|INSERT|UPDATE|GRANT|REVOKE|TRUNCATE)\b",
            r"--",  # Single line comment
            r";",  # Query separator
            r"/\*",  # Start of multi-line comment
            r"\*/",  # End of multi-line comment
            r"\bOR\b.*\b=\b",  # OR conditionals that might be used for SQLi
            r"\bAND\b.*\b=\b",  # AND conditionals that might be used for SQLi
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return (False, f"Unsafe query pattern: {pattern}")

        return (True, "Safe")

    def query(
        self, sql_file_path: str, safety_check: bool = True, batch_size: int = 250_000, **parameters: Any
    ) -> pd.DataFrame:
        query = self.load_sql(sql_file_path)
        if safety_check:
            safe, message = self.query_checker(query)
            if not safe:
                logging.error(f"Unsafe query: {message}")
                raise ValueError(f"Unsafe query: {message}")

        if not safety_check:
            logging.warning("Safety check is disabled.")
        
        for key, value in parameters.items():
            query = query.replace(f"{key}", f"{value}")

        if self.connection is None:
            logging.info("Establishing a database connection...")
            try:
                # raise pyodbc.Error # for testing Java connection
                logging.info("Trying to connect using pyodbc...")
                self.connection = pyodbc.connect(self._database_conn_pyodbc())
                logging.info("Connection established using pyodbc.")
            except pyodbc.Error:
                try:
                    logging.info("Trying to connect using jaydebeapi...")
                    if self.__java_home is not None:
                        logging.info("Setting JAVA_HOME...")
                        os.environ["JAVA_HOME"] = self.__java_home
                    else:
                        logging.info("JAVA_HOME not set.")
                        raise RuntimeError("JAVA_HOME not set.")
                    self.connection = self._database_conn_jaydebeapi()
                    logging.info("Connection established using jaydebeapi.")
                except jaydebeapi.Error as e:
                    logging.error(f"Failed to establish a database connection: {e}")
                    raise ConnectionError(
                        "Failed to establish a database connection."
                    ) from e
        if self.connection is None:
            logging.error("Failed to establish a database connection.")
            raise ConnectionError("Failed to establish a database connection.")
        try:
            if isinstance(self.connection, pyodbc.Connection):
                df = pl.read_database(
                    query, self.connection, batch_size=batch_size
                ).to_pandas()
            else:
                cursor = self.connection.cursor()
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                    df = pd.DataFrame(cursor.fetchall())
        except (pyodbc.Error, jaydebeapi.Error) as e:
            logging.error(f"Query execution failed: {e}")
            raise RuntimeError(f"Query execution failed: {e}")

        return df
