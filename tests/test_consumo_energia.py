from datetime import datetime

import pandas as pd

from src.consumo_energia import calculate_costs


def test_calculate_costs_classification_and_values():
    df = pd.DataFrame(
        {
            "date": [
                datetime(2024, 1, 1, 10, 0, 0),  # Diurno
                datetime(2024, 1, 1, 19, 0, 0),  # Noturno
            ],
            "consumption": [5.0, 5.0],
        }
    )

    tariffs = {"diurnalRate": 2.0, "nightRate": 1.0}
    result = calculate_costs(df.copy(), tariffs)

    assert result.loc[0, "periodo"] == "Diurno"
    assert result.loc[1, "periodo"] == "Noturno"

    # Custos
    assert result.loc[0, "custo"] == 10.0
    assert result.loc[1, "custo"] == 5.0


def test_calculate_costs_edge_cases():
    # Teste com DataFrame vazio
    empty_df = pd.DataFrame()
    tariffs = {"diurnalRate": 2.0, "nightRate": 1.0}
    result = calculate_costs(empty_df, tariffs)
    assert result.equals(empty_df)
    
    # Teste com tarifas vazias
    df = pd.DataFrame({
        "date": [datetime(2024, 1, 1, 10, 0, 0)],
        "consumption": [5.0]
    })
    result = calculate_costs(df.copy(), {})
    assert result.equals(df)
    
    # Teste horários limítrofes
    df_boundary = pd.DataFrame({
        "date": [
            datetime(2024, 1, 1, 5, 59, 59),  # Noturno (antes de 06:00)
            datetime(2024, 1, 1, 6, 0, 0),   # Diurno (exatamente 06:00)
            datetime(2024, 1, 1, 17, 59, 59), # Diurno (antes de 18:00)
            datetime(2024, 1, 1, 18, 0, 0),   # Noturno (exatamente 18:00)
        ],
        "consumption": [1.0, 1.0, 1.0, 1.0]
    })
    
    result_boundary = calculate_costs(df_boundary.copy(), tariffs)
    assert result_boundary.loc[0, "periodo"] == "Noturno"
    assert result_boundary.loc[1, "periodo"] == "Diurno"  
    assert result_boundary.loc[2, "periodo"] == "Diurno"
    assert result_boundary.loc[3, "periodo"] == "Noturno"
    
    # Teste com valores de consumo zero e negativos
    df_zero_negative = pd.DataFrame({
        "date": [
            datetime(2024, 1, 1, 10, 0, 0),  # Diurno
            datetime(2024, 1, 1, 20, 0, 0),  # Noturno
        ],
        "consumption": [0.0, -1.0]  # Zero e negativo
    })
    
    result_zero_negative = calculate_costs(df_zero_negative.copy(), tariffs)
    assert result_zero_negative.loc[0, "custo"] == 0.0  # 0 * 2.0
    assert result_zero_negative.loc[1, "custo"] == -1.0  # -1 * 1.0


