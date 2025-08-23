# tests/test_tariff_schedules_contract.py

from unittest.mock import MagicMock, Mock

import streamlit as st

# Mock streamlit session_state before importing the module
st.session_state = MagicMock()

from src.tariff_schedules import (create_tariff, delete_tariff,
                                  get_all_tariffs, get_current_tariff,
                                  update_tariff)


class TestTariffSchedulesContract:
    """Testes para validar conformidade dos endpoints de tarifas com OpenAPI."""

    def setup_method(self):
        """Setup para cada teste."""
        st.session_state.get.return_value = "mock_token"

    def test_get_all_tariffs_success_200_object(self, monkeypatch):
        """Testa GET /api/tariff-schedules retornando objeto singular (conforme Swagger)."""
        # Mock response 200 com objeto TariffSchedule
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "date": "2023-12-01T00:00:00Z",
            "daytimeStart": "06:00:00",
            "daytimeEnd": "18:00:00",
            "nighttimeStart": "18:00:00",
            "nighttimeEnd": "06:00:00",
            "daytimeTariff": 0.15,
            "nighttimeTariff": 0.10,
            "nighttimeDiscount": 30.0,
        }

        def mock_api_request(method, endpoint, token=None):
            assert method == "GET"
            assert endpoint == "/api/tariff-schedules"
            assert token == "mock_token"
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = get_all_tariffs("mock_token")

        # Validações - deve retornar array com um objeto
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert "daytimeTariff" in result[0]
        assert "nighttimeTariff" in result[0]
        assert "nighttimeDiscount" in result[0]

    def test_get_all_tariffs_success_200_array(self, monkeypatch):
        """Testa GET /api/tariff-schedules retornando array (diverge do Swagger mas compatível)."""
        # Mock response 200 com array
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "date": "2023-12-01T00:00:00Z",
                "daytimeStart": "06:00:00",
                "daytimeEnd": "18:00:00",
                "nighttimeStart": "18:00:00",
                "nighttimeEnd": "06:00:00",
                "daytimeTariff": 0.15,
                "nighttimeTariff": 0.10,
                "nighttimeDiscount": 30.0,
            }
        ]

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = get_all_tariffs("mock_token")

        # Validações - deve retornar array como recebido
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_get_all_tariffs_server_error_500(self, monkeypatch):
        """Testa GET /api/tariff-schedules erro 500."""
        mock_response = Mock()
        mock_response.status_code = 500

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Mock st.error
        mock_error = Mock()
        monkeypatch.setattr("src.tariff_schedules.st.error", mock_error)

        # Executa função
        result = get_all_tariffs("mock_token")

        # Validações
        assert result == []
        mock_error.assert_called_with("Erro interno do servidor ao buscar tarifas.")

    def test_get_current_tariff_success_200(self, monkeypatch):
        """Testa GET /api/tariff-schedules/current retorno 200."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "date": "2023-12-01T00:00:00Z",
            "daytimeTariff": 0.15,
            "nighttimeTariff": 0.10,
            "nighttimeDiscount": 30.0,
        }

        def mock_api_request(method, endpoint, token=None):
            assert method == "GET"
            assert endpoint == "/api/tariff-schedules/current"
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = get_current_tariff("mock_token")

        # Validações
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert "daytimeTariff" in result
        assert "nighttimeTariff" in result

    def test_get_current_tariff_not_found_404(self, monkeypatch):
        """Testa GET /api/tariff-schedules/current retorno 404."""
        mock_response = Mock()
        mock_response.status_code = 404

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Mock st.info
        mock_info = Mock()
        monkeypatch.setattr("src.tariff_schedules.st.info", mock_info)

        # Executa função
        result = get_current_tariff("mock_token")

        # Validações
        assert result == {}
        mock_info.assert_called_with("Nenhuma tarifa atual encontrada.")

    def test_get_current_tariff_server_error_500(self, monkeypatch):
        """Testa GET /api/tariff-schedules/current retorno 500."""
        mock_response = Mock()
        mock_response.status_code = 500

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Mock st.error
        mock_error = Mock()
        monkeypatch.setattr("src.tariff_schedules.st.error", mock_error)

        # Executa função
        result = get_current_tariff("mock_token")

        # Validações
        assert result == {}
        mock_error.assert_called_with(
            "Erro interno do servidor ao buscar tarifa atual."
        )

    def test_create_tariff_success_200(self, monkeypatch):
        """Testa POST /api/tariff-schedules retorno 200."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 2}

        def mock_api_request(method, endpoint, token=None, json=None):
            assert method == "POST"
            assert endpoint == "/api/tariff-schedules"
            assert token == "mock_token"
            # Validar estrutura do payload
            assert "daytimeTariff" in json
            assert "nighttimeTariff" in json
            assert "nighttimeDiscount" in json
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        tariff_data = {
            "date": "2023-12-01T00:00:00Z",
            "daytimeStart": "06:00:00",
            "daytimeEnd": "18:00:00",
            "nighttimeStart": "18:00:00",
            "nighttimeEnd": "06:00:00",
            "daytimeTariff": 0.15,
            "nighttimeTariff": 0.10,
            "nighttimeDiscount": 30.0,
        }
        result = create_tariff("mock_token", tariff_data)

        # Validações
        assert result.status_code == 200

    def test_create_tariff_bad_request_400(self, monkeypatch):
        """Testa POST /api/tariff-schedules retorno 400."""
        mock_response = Mock()
        mock_response.status_code = 400

        def mock_api_request(method, endpoint, token=None, json=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = create_tariff("mock_token", {})

        # Validações
        assert result.status_code == 400

    def test_create_tariff_conflict_409(self, monkeypatch):
        """Testa POST /api/tariff-schedules retorno 409 (Conflict)."""
        mock_response = Mock()
        mock_response.status_code = 409

        def mock_api_request(method, endpoint, token=None, json=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = create_tariff("mock_token", {})

        # Validações
        assert result.status_code == 409

    def test_update_tariff_success_200(self, monkeypatch):
        """Testa PUT /api/tariff-schedules/{id} retorno 200."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}

        def mock_api_request(method, endpoint, token=None, json=None):
            assert method == "PUT"
            assert endpoint == "/api/tariff-schedules/1"
            assert token == "mock_token"
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = update_tariff("mock_token", 1, {})

        # Validações
        assert result.status_code == 200

    def test_update_tariff_not_found_404(self, monkeypatch):
        """Testa PUT /api/tariff-schedules/{id} retorno 404."""
        mock_response = Mock()
        mock_response.status_code = 404

        def mock_api_request(method, endpoint, token=None, json=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = update_tariff("mock_token", 999, {})

        # Validações
        assert result.status_code == 404

    def test_delete_tariff_success_200_or_204(self, monkeypatch):
        """Testa DELETE /api/tariff-schedules/{id} retorno 200 ou 204."""
        mock_response = Mock()
        mock_response.status_code = 204  # No Content conforme OpenAPI

        def mock_api_request(method, endpoint, token=None):
            assert method == "DELETE"
            assert endpoint == "/api/tariff-schedules/1"
            assert token == "mock_token"
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = delete_tariff("mock_token", 1)

        # Validações
        assert result.status_code == 204

    def test_delete_tariff_not_found_404(self, monkeypatch):
        """Testa DELETE /api/tariff-schedules/{id} retorno 404."""
        mock_response = Mock()
        mock_response.status_code = 404

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = delete_tariff("mock_token", 999)

        # Validações
        assert result.status_code == 404

    def test_api_request_failure_none(self, monkeypatch):
        """Testa quando api_request retorna None."""

        def mock_api_request(method, endpoint, token=None):
            return None

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Executa função
        result = get_all_tariffs("mock_token")

        # Validações
        assert result == []

    def test_get_current_tariff_malformed_json(self, monkeypatch):
        """Testa resposta com JSON inválido."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        def mock_api_request(method, endpoint, token=None):
            return mock_response

        monkeypatch.setattr("src.tariff_schedules.api_request", mock_api_request)

        # Mock st.error
        mock_error = Mock()
        monkeypatch.setattr("src.tariff_schedules.st.error", mock_error)

        # Executa função
        result = get_current_tariff("mock_token")

        # Validações
        assert result == {}
        mock_error.assert_called_with(
            "Erro ao processar resposta JSON da tarifa atual."
        )
