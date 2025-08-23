# src/monitoring_stations.py
"""
Estações de Monitoramento - Padronizado com UI Foundations v2
"""

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (cast_to_double, cast_to_int32, cast_to_int64,
                               clear_form_state, controller_selector,
                               geographic_coordinates_input,
                               handle_api_response_v2,
                               invalidate_caches_after_mutation,
                               moisture_limit_input, save_form_state,
                               validate_coordinates, validate_id_positive,
                               validate_moisture_limits)


def get_controllers():
    """GET /api/controllers para obter lista de controladores"""
    token = st.session_state.get("token", None)
    if not token:
        return []

    response = api_request("GET", "/api/controllers", token=token)
    if response and response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return []
    return []


def fetch_equipments():
    """GET /api/monitoring-stations

    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    response = api_request("GET", "/api/monitoring-stations", token=token)

    if not response:
        st.error("Erro ao conectar com a API de estações.")
        return pd.DataFrame()

    if response.status_code == 200:
        try:
            return pd.DataFrame(response.json())
        except ValueError:
            st.error("Erro ao processar resposta JSON.")
            return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar estações.")
        return pd.DataFrame()
    else:
        st.error(f"Erro inesperado: {response.status_code}")
        return pd.DataFrame()


def get_monitoring_stations(token: str):
    """GET /api/monitoring-stations para uso em seletores."""
    response = api_request("GET", "/api/monitoring-stations", token=token)
    if response and response.status_code == 200:
        try:
            data = response.json()
            return data if isinstance(data, list) else []
        except ValueError:
            return []
    return []


def create_monitoring_station(token: str, data: dict):
    """POST /api/monitoring-stations com tratamento padronizado."""
    response = api_request("POST", "/api/monitoring-stations", token=token, json=data)
    return response


def create_sensor(token: str, station_id: int, sensor_data: dict):
    """POST /api/monitoring-stations/{stationId}/sensors com casting correto."""
    # Cast stationId para int64 conforme swagger
    station_id = cast_to_int64(station_id)
    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("POST", endpoint, token=token, json=sensor_data)
    return response


def show():
    st.title("Cadastro de Equipamentos")

    equipments_df = fetch_equipments()
    if not equipments_df.empty:
        st.subheader("Estações de Monitoramento Cadastradas")
        # Renomear colunas para português
        display_df = equipments_df.copy()
        if not display_df.empty:
            column_mapping = {
                "id": "ID",
                "name": "Nome",
                "latitude": "Latitude",
                "longitude": "Longitude",
                "moistureUpperLimit": "Limite Superior (%)",
                "moistureLowerLimit": "Limite Inferior (%)",
                "controllerId": "ID do Controlador",
            }
            display_df = display_df.rename(columns=column_mapping)
        st.dataframe(display_df, use_container_width=True)

    tab1, tab2 = st.tabs(["🏗️ Estação de Monitoramento", "📡 Sensor"])

    with tab1:
        st.subheader("Cadastrar Nova Estação de Monitoramento")

        with st.form("NovaEstacao"):
            # Campos obrigatórios conforme Swagger MonitoringStation schema
            name = st.text_input(
                "Nome da Estação *",
                placeholder="Ex: Estação Setor Norte",
                help="Nome identificador da estação (obrigatório)",
            )

            # Usar componente padronizado para coordenadas
            latitude, longitude = geographic_coordinates_input(
                lat_value=None, lon_value=None
            )

            col1, col2 = st.columns(2)
            with col1:
                moisture_lower_limit = moisture_limit_input(
                    "Limite Inferior de Umidade (%) *",
                    value=30.0,
                    help_text="Limite inferior para acionamento",
                )
            with col2:
                moisture_upper_limit = moisture_limit_input(
                    "Limite Superior de Umidade (%) *",
                    value=70.0,
                    help_text="Limite superior para desacionamento",
                )

            # Usar seletor padronizado de controlador
            token = st.session_state.get("token")
            controller_id, controller_name = controller_selector(
                token, "Controlador (Opcional)", include_all_option=False
            )
            # Permitir "nenhum controlador"
            if st.checkbox("Sem controlador associado", value=controller_id is None):
                controller_id = None

            submitted = st.form_submit_button("✅ Cadastrar Estação")

            if submitted:
                # Salvar estado do formulário para recuperação em caso de erro
                form_data = {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "moisture_lower": moisture_lower_limit,
                    "moisture_upper": moisture_upper_limit,
                    "controller_id": controller_id,
                }
                save_form_state("station_create", form_data)

                # Validações padronizadas
                if not name.strip():
                    st.error("Nome da estação é obrigatório.")
                    return

                coords_valid, coords_msg = validate_coordinates(latitude, longitude)
                if not coords_valid:
                    st.error(coords_msg)
                    return

                limits_valid, limits_msg = validate_moisture_limits(
                    moisture_lower_limit, moisture_upper_limit
                )
                if not limits_valid:
                    st.error(limits_msg)
                    return

                # Dados conforme schema MonitoringStation com casting correto
                data = {
                    "name": name.strip(),
                    "latitude": cast_to_double(latitude),
                    "longitude": cast_to_double(longitude),
                    "moistureUpperLimit": cast_to_double(moisture_upper_limit),
                    "moistureLowerLimit": cast_to_double(moisture_lower_limit),
                    "controllerId": (
                        cast_to_int64(controller_id) if controller_id else None
                    ),
                }

                resp = create_monitoring_station(token, data)
                if handle_api_response_v2(
                    resp, "Estação de monitoramento criada com sucesso!"
                ):
                    clear_form_state("station_create")
                    invalidate_caches_after_mutation("stations")
                    st.rerun()

    with tab2:
        st.subheader("Cadastrar Novo Sensor")

        # Obter estações para seleção usando componente padronizado
        token = st.session_state.get("token")
        stations = get_monitoring_stations(token)
        if not stations:
            st.warning("⚠️ Nenhuma estação cadastrada. Cadastre uma estação primeiro.")
            return

        with st.form("NovoSensor"):
            # Usar seletor padronizado com formato "Nome (ID: X)"
            station_options = {
                f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
                for station in stations
            }

            station_choice = st.selectbox(
                "Estação de Monitoramento *",
                station_options.keys(),
                help="Selecione a estação onde o sensor será instalado",
            )
            station_id = station_options[station_choice]

            sensor_id = st.number_input(
                "ID do Sensor *",
                min_value=1,
                step=1,
                value=1,
                help="ID único do sensor (int32 conforme swagger)",
            )

            submitted = st.form_submit_button("✅ Cadastrar Sensor")

            if submitted:
                # Validação de ID positivo
                id_valid, id_msg = validate_id_positive(sensor_id)
                if not id_valid:
                    st.error(id_msg)
                    return

                # Dados conforme schema Sensor com casting correto
                sensor_data = {
                    "id": cast_to_int32(sensor_id),  # int32 conforme swagger
                    "monitoringStationId": cast_to_int64(
                        station_id
                    ),  # int64 conforme swagger
                }

                resp = create_sensor(token, station_id, sensor_data)
                if handle_api_response_v2(resp, "Sensor criado com sucesso!"):
                    invalidate_caches_after_mutation("sensors")
                    st.rerun()


if __name__ == "__main__":
    show()
