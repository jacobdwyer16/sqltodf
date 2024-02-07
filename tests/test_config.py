# tests/test_config.py
import pytest
from sqltodf.engine import DatabaseConfig
from typing import Dict, Union

def test_valid_config()->None:
    config: Dict[str, Union[str, int]]  = {
        "DB_CONN_DRIVER": "driver",
        "DB_PORT": 1234,
        "DB_DATABASE": "test_db",
        "DB_USER": "user",
        "DB_PASSWORD": "password"
    }
    db_config = DatabaseConfig(**config)
    assert db_config.DB_CONN_DRIVER == "driver"

def test_invalid_config()->None:
    config = {
        "DB_PORT": 1234,
        "DB_DATABASE": "test_db",
        "DB_USER": "user",
        "DB_PASSWORD": "password"
    }
    with pytest.raises(ValueError):
        DatabaseConfig(**config)
