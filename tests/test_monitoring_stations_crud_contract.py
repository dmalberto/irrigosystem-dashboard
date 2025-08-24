"""
Testes unitários/contratuais para endpoints CRUD de MonitoringStations
- PUT /api/monitoring-stations/{id}
- DELETE /api/monitoring-stations/{id}  
- GET /api/monitoring-stations/{stationId}/sensors
- PUT /api/monitoring-stations/{stationId}/sensors/{id}
- DELETE /api/monitoring-stations/{stationId}/sensors/{id}
Seguindo especificação Swagger com tipos exatos
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitoring_stations import (
    update_monitoring_station, 
    delete_monitoring_station,
    get_sensors,
    update_sensor, 
    delete_sensor
)


class TestMonitoringStationsCRUDContract:
    """Testes contratuais para CRUD de MonitoringStations"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_success_response = Mock()
        self.mock_success_response.status_code = 200
        self.mock_success_response.json.return_value = {"message": "Success"}
        
        self.mock_not_found_response = Mock()
        self.mock_not_found_response.status_code = 404
        self.mock_not_found_response.text = "Not Found"
        
    @patch('monitoring_stations.api_request')
    def test_update_monitoring_station_success_200(self, mock_api_request):
        """Teste: PUT /api/monitoring-stations/{id} - sucesso"""
        mock_api_request.return_value = self.mock_success_response
        
        # Parâmetros conforme Swagger
        station_id = 123  # int64 conforme Swagger
        data = {
            "name": "Estação Atualizada",
            "location": "Nova Localização", 
            "latitude": -23.550520,  # double
            "longitude": -46.633308   # double
        }
        
        result = update_monitoring_station('test_token', station_id, data)
        
        # Verificações contratuais
        assert result is True
        
        # Verificar chamada à API
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'PUT'
        assert f'/{station_id}' in call_args[0][1]
        
    @patch('monitoring_stations.api_request')
    def test_update_monitoring_station_not_found_404(self, mock_api_request):
        """Teste: PUT /api/monitoring-stations/{id} - não encontrado"""
        mock_api_request.return_value = self.mock_not_found_response
        
        station_id = 999  # ID inexistente
        data = {"name": "Test"}
        
        result = update_monitoring_station('test_token', station_id, data)
        assert result is False
        
    @patch('monitoring_stations.api_request')
    def test_delete_monitoring_station_success_200(self, mock_api_request):
        """Teste: DELETE /api/monitoring-stations/{id} - sucesso"""
        mock_api_request.return_value = self.mock_success_response
        
        station_id = 123  # int64 conforme Swagger
        result = delete_monitoring_station('test_token', station_id)
        
        assert result is True
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'DELETE'
        assert f'/{station_id}' in call_args[0][1]
        
    @patch('monitoring_stations.api_request')
    def test_delete_monitoring_station_not_found_404(self, mock_api_request):
        """Teste: DELETE /api/monitoring-stations/{id} - não encontrado"""
        mock_api_request.return_value = self.mock_not_found_response
        
        station_id = 999
        result = delete_monitoring_station('test_token', station_id)
        assert result is False
        
    @patch('monitoring_stations.api_request')
    def test_get_sensors_success_200(self, mock_api_request):
        """Teste: GET /api/monitoring-stations/{stationId}/sensors - sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Sensor 1", "type": "temperature"},
            {"id": 2, "name": "Sensor 2", "type": "humidity"}
        ]
        mock_api_request.return_value = mock_response
        
        station_id = 123  # int64 conforme Swagger
        result = get_sensors('test_token', station_id)
        
        # Verificações contratuais
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        
        # Verificar chamada à API
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'GET'
        assert f'/{station_id}/sensors' in call_args[0][1]
        
    @patch('monitoring_stations.api_request')
    def test_get_sensors_empty_list_200(self, mock_api_request):
        """Teste: GET sensors - lista vazia"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_api_request.return_value = mock_response
        
        result = get_sensors('test_token', 123)
        assert result == []
        
    @patch('monitoring_stations.api_request')
    def test_update_sensor_success_200(self, mock_api_request):
        """Teste: PUT /api/monitoring-stations/{stationId}/sensors/{id} - sucesso"""
        mock_api_request.return_value = self.mock_success_response
        
        # Parâmetros conforme Swagger
        station_id = 123    # int64 
        sensor_id = 456     # int32
        data = {
            "name": "Sensor Atualizado",
            "type": "pressure",
            "unit": "kPa"
        }
        
        result = update_sensor('test_token', station_id, sensor_id, data)
        
        assert result is True
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'PUT'
        assert f'/{station_id}/sensors/{sensor_id}' in call_args[0][1]
        
    @patch('monitoring_stations.api_request')
    def test_update_sensor_not_found_404(self, mock_api_request):
        """Teste: PUT sensor - não encontrado"""
        mock_api_request.return_value = self.mock_not_found_response
        
        result = update_sensor('test_token', 123, 999, {"name": "Test"})
        assert result is False
        
    @patch('monitoring_stations.api_request')
    def test_delete_sensor_success_200(self, mock_api_request):
        """Teste: DELETE /api/monitoring-stations/{stationId}/sensors/{id} - sucesso"""
        mock_api_request.return_value = self.mock_success_response
        
        station_id = 123  # int64
        sensor_id = 456   # int32
        result = delete_sensor('test_token', station_id, sensor_id)
        
        assert result is True
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args
        assert call_args[0][0] == 'DELETE'
        assert f'/{station_id}/sensors/{sensor_id}' in call_args[0][1]
        
    @patch('monitoring_stations.api_request')
    def test_delete_sensor_not_found_404(self, mock_api_request):
        """Teste: DELETE sensor - não encontrado"""
        mock_api_request.return_value = self.mock_not_found_response
        
        result = delete_sensor('test_token', 123, 999)
        assert result is False
        
    @patch('monitoring_stations.api_request')
    def test_update_monitoring_station_server_error_500(self, mock_api_request):
        """Teste: Erro do servidor - status 500"""
        mock_error = Mock()
        mock_error.status_code = 500
        mock_api_request.return_value = mock_error
        
        result = update_monitoring_station('test_token', 123, {"name": "Test"})
        assert result is False
        
    @patch('monitoring_stations.api_request')  
    def test_get_sensors_server_error_500(self, mock_api_request):
        """Teste: GET sensors - erro do servidor"""
        mock_error = Mock()
        mock_error.status_code = 500
        mock_api_request.return_value = mock_error
        
        result = get_sensors('test_token', 123)
        assert result is None