# DatabaseEngine

`sqltodf` is a Python package providing a flexible and robust way to interact with databases. It supports connections via `pyodbc` and `jaydebeapi`, offering a fallback mechanism for enhanced reliability. The package is designed to be easy to use while handling various database operations efficiently.

## Features
- Supports database connections using pyodbc and jaydebeapi.
- Scans the SQL query for potentially unsafe operations before execution. *This can be disabled.*
- Automatic fallback from pyodbc to jaydebeapi in case of connection issues.
- Dynamic SQL query execution with customizable, user-defined parameters.
- Configuration validation using Pydantic.
- Integrated logging for easy debugging and monitoring.

## Installation
To install `sqltodf`, you can use pip:

```bash

pip install git+https://github.com/jacobdwyer16/sqltodf.git

```
Ensure you have the necessary drivers for `pyodbc` and `jaydebeapi` based on your database.

## Usage
Here's a quick example of how to use `sqltodf`:

```python
from sqltodf import DatabaseEngine

# Configuration for the database connection
config = {
    "DB_HOST"="MYDB",
    "DB_USER"="user",
    "DB_PORT"="5555",
    "DB_PASSWORD"="password",
    "DB_DRIVER"="ODBC+Driver+17+for+SQL+Server",
    "DB_CONNECTION"="mysql+pymysql",
    "DB_DATABASE"="DATABASE",
    "DB_CONN_DRIVER"= "{ODBC Driver 17 for SQL Server}",
    "JAVA_HOME"="path/to/java" # optional if pyodbc fails - currently specific to MacOS
}

# Initialize the DatabaseEngine
engine = DatabaseEngine(config)

# Custom parameters of any key/value combination (or None)
# This allows users to have queries update at run-time
params = {
    "StartDate": formatted_date_str,
}

# Execute a query from a SQL file with parameters
df = engine.query("path/to/your/sqlfile.sql", **params)

# Work with the returned DataFrame
print(df)
```

## Configuration
The configuration for `sqltodf` should be provided as a dictionary. The following keys are required:

- `DB_CONN_DRIVER`: Database driver for the connection.
- `DB_HOST`: Hostname of the database server.
- `DB_PORT`: Port number for the database connection.
- `DB_DATABASE`: Name of the database.
- `DB_USER`: Username for database authentication.
- `DB_PASSWORD`: Password for database authentication.
- `JAVA_HOME`: *Optional* Path to Java.exe to use JDBC instead of ODBC (ODBC is recommended)

Note: To use a JDBC, TLSv1 and TLSv1.1 have to be removed from Java's security file as disabled algorithms. This is a *backup* only in the event the ODBC fails.

## Logging
`sqltodf` uses Python's built-in logging. You can pass a custom logger to the `sqltodf` if you want to integrate its logs with your application's logging system.

Requirements
Python 3.9+
`pyodbc`
`jaydebeapi`
`polars`
`pandas`
`Pydantic`

## Contributing
Contributions to `sqltodf` are welcome!