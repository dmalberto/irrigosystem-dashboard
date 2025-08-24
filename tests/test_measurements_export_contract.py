"""
Testes unitários/contratuais para o endpoint GET /api/measurements/export
Seguindo especificação Swagger com parâmetros exatos e tipos corretos
"""
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from measurements import export_measurements_csv


class TestMeasurementsExportContract:
    """Testes contratuais para GET /api/measurements/export"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.text = "timestamp,station_id,sensor_id,value\n2024-01-01T00:00:00Z,1,1,25.5"
        
    @patch('measurements.api_request')
    def test_export_measurements_success_200(self, mock_api_request):
        """Teste: Export com sucesso - status 200"""
        mock_api_request.return_value = self.mock_response
        
        # Parâmetros conforme Swagger
        result = export_measurements_csv(
            token='test_token',
            start_date='2024-01-01T00:00:00Z',  # date-time
            end_date='2024-01-31T23:59:59Z',    # date-time  
            station_id=1,                       # int32
            sensor_id=1,                        # int32
            sort='timestamp:asc'                # string
        )
        
        # Verificações contratuais
        assert result is not None
        assert isinstance(result, str)
        assert 'timestamp,station_id,sensor_id,value' in result
        
        # Verificar chamada à API
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'GET'  # método
        assert '/api/measurements/export' in call_args[0][1]  # endpoint
        
    @patch('measurements.api_request')
    def test_export_measurements_minimal_params(self, mock_api_request):
        """Teste: Export com parâmetros mínimos obrigatórios"""
        mock_api_request.return_value = self.mock_response
        
        result = export_measurements_csv('test_token')
        
        assert result is not None
        mock_api_request.assert_called_once()
        
    @patch('measurements.api_request')  
    def test_export_measurements_api_error_500(self, mock_api_request):
        """Teste: Erro da API - status 500"""
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        mock_response_error.text = "Internal Server Error"
        mock_api_request.return_value = mock_response_error
        
        result = export_measurements_csv('test_token')
        
        # Deve retornar None em caso de erro
        assert result is None
        
    @patch('measurements.api_request')
    def test_export_measurements_api_error_400(self, mock_api_request):
        """Teste: Bad Request - status 400"""
        mock_response_error = Mock()
        mock_response_error.status_code = 400
        mock_response_error.text = "Bad Request - Invalid date format"
        mock_api_request.return_value = mock_response_error
        
        result = export_measurements_csv('test_token', start_date='invalid-date')
        assert result is None
        
    @patch('measurements.api_request')
    def test_export_measurements_type_casting(self, mock_api_request):
        """Teste: Verificar type casting correto conforme Swagger"""
        mock_api_request.return_value = self.mock_response
        
        # Passar tipos como string que devem ser convertidos
        result = export_measurements_csv(
            'test_token',
            start_date='2024-01-01T00:00:00Z',
            end_date='2024-01-31T23:59:59Z', 
            station_id='123',  # string que deve ser int32
            sensor_id='456',   # string que deve ser int32
            sort='value:desc'
        )
        
        assert result is not None
        mock_api_request.assert_called_once()
        
    @patch('measurements.api_request')
    def test_export_measurements_empty_response(self, mock_api_request):
        """Teste: Resposta vazia da API"""
        mock_empty = Mock()
        mock_empty.status_code = 200
        mock_empty.text = ""
        mock_api_request.return_value = mock_empty
        
        result = export_measurements_csv('test_token')
        assert result == ""  # Deve retornar string vazia
        
    def test_export_measurements_invalid_params(self):
        """Teste: Parâmetros inválidos"""
        # Teste sem token obrigatório
        with pytest.raises(TypeError):
            export_measurements_csv()