"""
Testes unitários/contratuais para o endpoint GET /api/controllers/{controllerId}/activations
Seguindo especificação Swagger com parâmetros exatos e tipos corretos
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from controller_activations import fetch_activations


class TestControllerActivationsContract:
    """Testes contratuais para GET /api/controllers/{controllerId}/activations"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_success_response = Mock()
        self.mock_success_response.status_code = 200
        self.mock_success_response.json.return_value = [
            {
                "id": 1,
                "controllerId": 123,
                "timestamp": "2024-01-01T10:00:00Z",
                "action": "start_irrigation", 
                "duration": 1800,
                "valveId": 1
            },
            {
                "id": 2,
                "controllerId": 123,
                "timestamp": "2024-01-01T12:00:00Z",
                "action": "stop_irrigation",
                "duration": 0,
                "valveId": 1
            }
        ]
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_success_200(self, mock_api_request):
        """Teste: Fetch activations com sucesso - status 200"""
        mock_api_request.return_value = self.mock_success_response
        
        # Parâmetros conforme Swagger
        controller_id = 123  # int64
        period = "month"     # string (day, week, month, year)
        
        result = fetch_activations('test_token', controller_id, period)
        
        # Verificações contratuais
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Verificar estrutura dos dados retornados
        activation = result[0]
        assert "id" in activation
        assert "controllerId" in activation
        assert "timestamp" in activation
        assert "action" in activation
        assert activation["controllerId"] == 123
        
        # Verificar chamada à API
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'GET'
        assert f'/{controller_id}/activations' in call_args[0][1]
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_different_periods(self, mock_api_request):
        """Teste: Diferentes valores de period conforme Swagger"""
        mock_api_request.return_value = self.mock_success_response
        
        valid_periods = ["day", "week", "month", "year"]
        controller_id = 123
        
        for period in valid_periods:
            result = fetch_activations('test_token', controller_id, period)
            assert result is not None
            
    @patch('controller_activations.api_request')
    def test_fetch_activations_empty_list_200(self, mock_api_request):
        """Teste: Response com lista vazia"""
        mock_empty = Mock()
        mock_empty.status_code = 200
        mock_empty.json.return_value = []
        mock_api_request.return_value = mock_empty
        
        result = fetch_activations('test_token', 123, "month")
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_controller_not_found_404(self, mock_api_request):
        """Teste: Controller não encontrado - status 404"""
        mock_not_found = Mock()
        mock_not_found.status_code = 404
        mock_not_found.text = "Controller not found"
        mock_api_request.return_value = mock_not_found
        
        result = fetch_activations('test_token', 999, "month")  # ID inexistente
        
        # Deve retornar None para erro 404
        assert result is None
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_bad_request_400(self, mock_api_request):
        """Teste: Bad request - period inválido - status 400"""
        mock_bad_request = Mock()
        mock_bad_request.status_code = 400
        mock_bad_request.text = "Invalid period parameter"
        mock_api_request.return_value = mock_bad_request
        
        result = fetch_activations('test_token', 123, "invalid_period")
        
        assert result is None
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_server_error_500(self, mock_api_request):
        """Teste: Erro interno do servidor - status 500"""
        mock_error = Mock()
        mock_error.status_code = 500
        mock_error.text = "Internal Server Error"
        mock_api_request.return_value = mock_error
        
        result = fetch_activations('test_token', 123, "month")
        
        assert result is None
        
    @patch('controller_activations.api_request')
    def test_fetch_activations_type_casting(self, mock_api_request):
        """Teste: Type casting do controllerId conforme Swagger (int64)"""
        mock_api_request.return_value = self.mock_success_response
        
        # Passar controller_id como string que deve ser convertido para int64
        controller_id_str = "123"
        result = fetch_activations('test_token', controller_id_str, "month")
        
        assert result is not None
        
        # Verificar se a URL foi construída corretamente
        call_args = mock_api_request.call_args
        url = call_args[0][1]
        assert "/123/activations" in url  # ID convertido corretamente
        
    def test_fetch_activations_required_parameters(self):
        """Teste: Parâmetros obrigatórios conforme Swagger"""
        # token é obrigatório
        with pytest.raises(TypeError):
            fetch_activations(controller_id=123, period="month")
            
        # controllerId é obrigatório (path parameter)
        with pytest.raises(TypeError):
            fetch_activations('test_token', period="month")  # Sem controllerId
            
        # period é obrigatório (query parameter)  
        with pytest.raises(TypeError):
            fetch_activations('test_token', controller_id=123)  # Sem period
            
    @patch('controller_activations.api_request')
    def test_fetch_activations_response_structure(self, mock_api_request):
        """Teste: Estrutura da resposta conforme Swagger schema"""
        # Mock com estrutura completa esperada
        expected_structure = [
            {
                "id": 1,
                "controllerId": 123, 
                "timestamp": "2024-01-01T10:00:00Z",
                "action": "start_irrigation",
                "duration": 1800,
                "valveId": 1,
                "status": "completed"
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_structure
        mock_api_request.return_value = mock_response
        
        result = fetch_activations('test_token', 123, "month")
        
        # Verificar campos obrigatórios do schema
        activation = result[0]
        required_fields = ["id", "controllerId", "timestamp", "action"]
        for field in required_fields:
            assert field in activation
            assert activation[field] is not None
            
        # Verificar tipos conforme Swagger
        assert isinstance(activation["id"], int)
        assert isinstance(activation["controllerId"], int)  # int64 
        assert isinstance(activation["timestamp"], str)     # date-time
        assert isinstance(activation["action"], str)        # string