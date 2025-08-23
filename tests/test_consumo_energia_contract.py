# tests/test_energy_consumptions_contract.py

from unittest.mock import MagicMock, Mock

import pandas as pd
import streamlit as st

# Mock streamlit session_state before importing the module
st.session_state = MagicMock()

from src.energy_consumptions import fetch_energy_consumption


class TestEnergyConsumptionContract:
    """Testes para validar conformidade do endpoint de consumo de energia com Swagger."""

    def setup_method(self):
        """Setup para cada teste."""
        st.session_state.get.return_value = "mock_token"

    def test_fetch_energy_consumption_success_200(self, monkeypatch):
        """Testa resposta 200 com dados válidos."""
        # Mock response 200 com dados válidos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "date": "2023-12-01T10:00:00Z",
                "daytimePower": 150.5,
                "daytimeCost": 50.2,
                "nighttimePower": 80.3,
                "nighttimeCost": 20.1,
                "nighttimeDiscount": 0.3,
                "totalCost": 70.3,
            }
        ]

        # Mock api_request para retornar mock_response
        def mock_api_request(method, endpoint, token=None, params=None):
            assert method == "GET"
            assert endpoint == "/api/consumptions/energy"
            assert token == "mock_token"
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Executa função
        result = fetch_energy_consumption(controller_id=123, period="daily")

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "date" in result.columns
        assert "totalCost" in result.columns
        # Data deve ter sido convertida para timezone São Paulo
        assert str(result["date"].dtype) == "datetime64[ns, America/Sao_Paulo]"

    def test_fetch_energy_consumption_bad_request_400(self, monkeypatch):
        """Testa tratamento de erro 400 - Bad Request."""
        # Mock response 400
        mock_response = Mock()
        mock_response.status_code = 400

        def mock_api_request(method, endpoint, token=None, params=None):
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Mock st.error para verificar se foi chamado
        mock_error = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.error", mock_error)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_error.assert_called_with("Requisição inválida. Verifique filtros.")

    def test_fetch_energy_consumption_server_error_500(self, monkeypatch):
        """Testa tratamento de erro 500 - Internal Server Error."""
        # Mock response 500
        mock_response = Mock()
        mock_response.status_code = 500

        def mock_api_request(method, endpoint, token=None, params=None):
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Mock st.error para verificar se foi chamado
        mock_error = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.error", mock_error)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_error.assert_called_with("Erro interno ao consultar consumo de energia.")

    def test_fetch_energy_consumption_api_request_failure(self, monkeypatch):
        """Testa quando api_request retorna None (falha de conexão)."""

        def mock_api_request(method, endpoint, token=None, params=None):
            return None

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Mock st.error para verificar se foi chamado
        mock_error = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.error", mock_error)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_error.assert_called_with(
            "Erro ao conectar com a API de consumo de energia."
        )

    def test_fetch_energy_consumption_swagger_params(self, monkeypatch):
        """Testa se parâmetros são passados corretamente conforme Swagger."""
        captured_params = {}

        def mock_api_request(method, endpoint, token=None, params=None):
            captured_params.update(params or {})
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)
        monkeypatch.setattr("src.energy_consumptions.st.warning", Mock())

        # Executa com parâmetros do Swagger
        fetch_energy_consumption(
            controller_id=456,
            period="weekly",
            start_date="2023-12-01",
            end_date="2023-12-31",
        )

        # Validações dos parâmetros conforme Swagger
        assert captured_params["controllerId"] == 456  # int64
        assert captured_params["period"] == "weekly"  # string
        # Parâmetros de data mantidos para compatibilidade
        assert captured_params["startDate"] == "2023-12-01"
        assert captured_params["endDate"] == "2023-12-31"

    def test_fetch_energy_consumption_no_token(self, monkeypatch):
        """Testa comportamento quando não há token de autenticação."""
        st.session_state.get.return_value = None

        # Mock st.error para verificar se foi chamado
        mock_error = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.error", mock_error)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_error.assert_called_with("Usuário não autenticado.")

    def test_fetch_energy_consumption_empty_response_200(self, monkeypatch):
        """Testa resposta 200 com array vazio - cenário válido sem dados."""
        # Mock response 200 com array vazio
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        def mock_api_request(method, endpoint, token=None, params=None):
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Mock st.warning para verificar se foi chamado
        mock_warning = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.warning", mock_warning)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_warning.assert_called_with(
            "Nenhum dado de consumo de energia disponível para os filtros selecionados."
        )

    def test_fetch_energy_consumption_malformed_json(self, monkeypatch):
        """Testa resposta com JSON inválido."""
        # Mock response 200 com JSON malformado
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON content"

        def mock_api_request(method, endpoint, token=None, params=None):
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)

        # Mock st.error para verificar se foi chamado
        mock_error = Mock()
        monkeypatch.setattr("src.energy_consumptions.st.error", mock_error)

        # Executa função
        result = fetch_energy_consumption()

        # Validações
        assert isinstance(result, pd.DataFrame)
        assert result.empty
        mock_error.assert_called_with(
            "Falha ao decodificar a resposta JSON da API de consumo de energia."
        )

    def test_fetch_energy_consumption_optional_params_omitted(self, monkeypatch):
        """Verifica que parâmetros None não são incluídos na requisição."""
        captured_params = {}

        def mock_api_request(method, endpoint, token=None, params=None):
            captured_params.update(params or {})
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            return mock_response

        monkeypatch.setattr("src.energy_consumptions.api_request", mock_api_request)
        monkeypatch.setattr("src.energy_consumptions.st.warning", Mock())

        # Executa com parâmetros None (devem ser omitidos)
        fetch_energy_consumption(
            controller_id=None, period=None, start_date=None, end_date=None
        )

        # Validações - parâmetros None não devem estar na requisição
        assert "controllerId" not in captured_params
        assert "period" not in captured_params
        assert "startDate" not in captured_params
        assert "endDate" not in captured_params
        assert len(captured_params) == 0  # Nenhum parâmetro deve ser enviado
