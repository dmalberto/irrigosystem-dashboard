from datetime import date, time

import pandas as pd

from src.amostras import (
    format_datetime as amostras_format_datetime,
    rename_columns as amostras_rename,
)
from src.dashboard import (
    format_datetime as dashboard_format_datetime,
    rename_columns as dashboard_rename,
)


def test_format_datetime_amostras_with_time():
    d = date(2024, 1, 1)
    t = time(0, 0, 0)
    assert amostras_format_datetime(d, t) == "2024-01-01T00:00:00Z"


def test_format_datetime_amostras_without_time():
    d = date(2024, 1, 1)
    assert amostras_format_datetime(d, None) == "2024-01-01T00:00:00Z"


def test_format_datetime_amostras_none_date():
    assert amostras_format_datetime(None, None) is None


def test_format_datetime_dashboard_with_time():
    d = date(2024, 1, 1)
    t = time(23, 59, 59)
    assert dashboard_format_datetime(d, t) == "2024-01-01T23:59:59Z"


def test_format_datetime_dashboard_without_time():
    d = date(2024, 1, 1)
    assert dashboard_format_datetime(d, None) == "2024-01-01T00:00:00Z"


def build_sample_df():
    return pd.DataFrame(
        {
            "id": [1],
            "date": ["2024-01-01T00:00:00Z"],
            "sensorId": [10],
            "batteryVoltage": [3.7],
            "boardTemperature": [25.0],
            "sensorTemperature": [24.5],
            "sampleTemperature": [24.0],
            "moisture": [0.5],
            "salinity": [100],
            "conductivity": [200],
        }
    )


def test_rename_columns_mappings_amostras():
    df = build_sample_df()
    amostras_rename(df)
    expected_cols = {
        "ID",
        "Data",
        "ID do Sensor",
        "Tensão da Bateria (V)",
        "Temperatura da Placa (°C)",
        "Temperatura do Sensor (°C)",
        "Temperatura da Amostra (°C)",
        "Umidade",
        "Salinidade (uS/cm)",
        "Condutividade",
    }
    assert expected_cols.issubset(set(df.columns))


def test_rename_columns_mappings_dashboard():
    df = build_sample_df()
    dashboard_rename(df)
    expected_cols = {
        "ID",
        "Data",
        "ID do Sensor",
        "Tensão da Bateria (V)",
        "Temperatura da Placa (°C)",
        "Temperatura do Sensor (°C)",
        "Temperatura da Amostra (°C)",
        "Umidade",
        "Salinidade (uS/cm)",
        "Condutividade",
    }
    assert expected_cols.issubset(set(df.columns))


