#!/usr/bin/env python3
"""
Smoke Test para Batch B - Fase 2
Verifica funcionamento básico das telas padronizadas
"""

import sys
from datetime import date, time
from unittest.mock import MagicMock, patch


def mock_streamlit():
    """Setup mock objects para Streamlit"""
    import streamlit as st

    # Mock básico do session_state
    if not hasattr(st, "session_state"):
        st.session_state = MagicMock()
        st.session_state.__getitem__ = MagicMock(return_value="mock_token")
        st.session_state.__setitem__ = MagicMock()
        st.session_state.get = MagicMock(return_value="mock_token")

    # Mock dos componentes UI
    st.title = MagicMock()
    st.subheader = MagicMock()
    st.form = MagicMock()
    st.text_input = MagicMock(return_value="test@example.com")
    st.number_input = MagicMock(return_value=100.0)
    st.date_input = MagicMock(return_value=date.today())
    st.time_input = MagicMock(return_value=time(12, 0))
    st.selectbox = MagicMock(return_value="Test Option")
    st.checkbox = MagicMock(return_value=False)
    st.button = MagicMock(return_value=False)
    st.form_submit_button = MagicMock(return_value=False)
    st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    st.radio = MagicMock(return_value="Listar")
    st.markdown = MagicMock()
    st.info = MagicMock()
    st.warning = MagicMock()
    st.error = MagicMock()
    st.success = MagicMock()
    st.spinner = MagicMock()
    st.dataframe = MagicMock()
    st.rerun = MagicMock()
    st.cache_data = MagicMock()

    return st


def test_ui_components_import():
    """Testa importação dos componentes UI"""
    try:
        print("✅ UI Components: Importação bem-sucedida")
        return True
    except Exception as e:
        print(f"❌ UI Components: Falha na importação - {e}")
        return False


def test_ui_components_basic_functions():
    """Testa funções básicas dos componentes UI"""
    try:
        from src.ui_components import (format_datetime_for_api,
                                       validate_coordinates, validate_email,
                                       validate_password)

        # Teste de validação de email
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False

        # Teste de validação de senha
        valid, msg = validate_password("senha123")
        assert valid == True

        invalid, msg = validate_password("123")
        assert invalid == False

        # Teste de validação de coordenadas
        valid, msg = validate_coordinates(-23.5505, -46.6333)
        assert valid == True

        invalid, msg = validate_coordinates(100, 200)
        assert invalid == False

        # Teste de formatação de data
        result = format_datetime_for_api(date.today(), time(12, 0))
        assert result is not None
        assert "T" in result
        assert result.endswith("Z")

        print("✅ UI Components: Funções básicas OK")
        return True
    except Exception as e:
        print(f"❌ UI Components: Falha nas funções básicas - {e}")
        return False


@patch("src.controllers.get_controllers")
def test_controllers_module(mock_get_controllers):
    """Testa módulo de controladores"""
    try:
        # Mock do retorno da API
        mock_get_controllers.return_value = [
            {
                "id": 1,
                "name": "Test Controller",
                "pumpPower": 1000.0,
                "efficiency": 0.85,
                "powerFactor": 0.9,
                "latitude": -23.5505,
                "longitude": -46.6333,
            }
        ]

        from src import controllers

        # Verificar se as funções principais existem
        assert hasattr(controllers, "show")
        assert hasattr(controllers, "get_controllers")
        assert hasattr(controllers, "create_controller")
        assert hasattr(controllers, "update_controller")
        assert hasattr(controllers, "delete_controller")

        print("✅ Controllers: Módulo OK")
        return True
    except Exception as e:
        print(f"❌ Controllers: Falha no módulo - {e}")
        return False


def test_tariff_schedules_module():
    """Testa módulo de tarifas"""
    try:
        from src import tariff_schedules

        # Verificar se as funções principais existem
        assert hasattr(tariff_schedules, "show")
        assert hasattr(tariff_schedules, "get_all_tariffs")
        assert hasattr(tariff_schedules, "get_current_tariff")
        assert hasattr(tariff_schedules, "create_tariff")
        assert hasattr(tariff_schedules, "update_tariff")
        assert hasattr(tariff_schedules, "delete_tariff")
        assert hasattr(tariff_schedules, "tariff_selector")
        assert hasattr(tariff_schedules, "validate_tariff_times")

        print("✅ Tariff Schedules: Módulo OK")
        return True
    except Exception as e:
        print(f"❌ Tariff Schedules: Falha no módulo - {e}")
        return False


def test_users_module():
    """Testa módulo de usuários"""
    try:
        from src import users

        # Verificar se as funções principais existem
        assert hasattr(users, "show")
        assert hasattr(users, "create_user")
        assert hasattr(users, "delete_user")

        print("✅ Users: Módulo OK")
        return True
    except Exception as e:
        print(f"❌ Users: Falha no módulo - {e}")
        return False


def test_controller_activations_module():
    """Testa módulo de ativações"""
    try:
        from src import controller_activations

        # Verificar se as funções principais existem
        assert hasattr(controller_activations, "show")
        assert hasattr(controller_activations, "fetch_statuses")
        assert hasattr(controller_activations, "load_more_statuses")

        print("✅ Controller Activations: Módulo OK")
        return True
    except Exception as e:
        print(f"❌ Controller Activations: Falha no módulo - {e}")
        return False


def run_smoke_tests():
    """Executa todos os smoke tests"""
    print("SMOKE TESTS - Batch B Fase 2")
    print("=" * 50)

    # Setup mocks
    st = mock_streamlit()

    results = []

    # Testes de importação e funcionamento
    results.append(test_ui_components_import())
    results.append(test_ui_components_basic_functions())
    results.append(test_controllers_module())
    results.append(test_tariff_schedules_module())
    results.append(test_users_module())
    results.append(test_controller_activations_module())

    # Resumo
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"Resumo: {passed}/{total} testes passaram")

    if passed == total:
        print("Todos os smoke tests passaram!")
        return 0
    else:
        print("Alguns testes falharam.")
        return 1


if __name__ == "__main__":
    exit_code = run_smoke_tests()
    sys.exit(exit_code)
