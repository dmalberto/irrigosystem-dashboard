# src/monitoring_stations.py
"""
Estações de Monitoramento - Modernizado com UI Foundations v3
Sistema completo com ComponentLibrary, LoadingStates e design tokens.
"""

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    cast_to_double,
    cast_to_int32,
    cast_to_int64,
    clear_form_state,
    controller_selector,
    geographic_coordinates_input,
    handle_api_response_v2,
    invalidate_caches_after_mutation,
    moisture_limit_input,
    save_form_state,
    validate_coordinates,
    validate_id_positive,
    validate_moisture_limits,
)


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


def update_monitoring_station(token: str, station_id: int, data: dict):
    """PUT /api/monitoring-stations/{id}"""
    station_id = cast_to_int64(station_id)
    endpoint = f"/api/monitoring-stations/{station_id}"
    return api_request("PUT", endpoint, token=token, json=data)


def delete_monitoring_station(token: str, station_id: int):
    """DELETE /api/monitoring-stations/{id}"""
    station_id = cast_to_int64(station_id)
    endpoint = f"/api/monitoring-stations/{station_id}"
    return api_request("DELETE", endpoint, token=token)


def get_sensors(token: str, station_id: int):
    """GET /api/monitoring-stations/{stationId}/sensors"""
    station_id = cast_to_int64(station_id)
    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    return api_request("GET", endpoint, token=token)


def update_sensor(token: str, station_id: int, sensor_id: int, sensor_data: dict):
    """PUT /api/monitoring-stations/{stationId}/sensors/{id}"""
    station_id = cast_to_int64(station_id)
    sensor_id = cast_to_int32(sensor_id)
    endpoint = f"/api/monitoring-stations/{station_id}/sensors/{sensor_id}"
    return api_request("PUT", endpoint, token=token, json=sensor_data)


def delete_sensor(token: str, station_id: int, sensor_id: int):
    """DELETE /api/monitoring-stations/{stationId}/sensors/{id}"""
    station_id = cast_to_int64(station_id)
    sensor_id = cast_to_int32(sensor_id)
    endpoint = f"/api/monitoring-stations/{station_id}/sensors/{sensor_id}"
    return api_request("DELETE", endpoint, token=token)


def show():
    st.title("🏭 Estações de Monitoramento")

    # Tabs principais para melhor organização
    tab_stations, tab_sensors = st.tabs([
        "🏭 Estações", 
        "📡 Sensores"
    ])

    with tab_stations:
        show_stations_tab()
    
    with tab_sensors:
        show_sensors_tab()


def show_stations_tab():
    """Tab principal para gerenciar estações de monitoramento"""
    st.markdown("### 🏭 Gerenciamento de Estações")
    
    # Sub-tabs para operações de estações
    list_tab, create_tab, edit_tab, delete_tab = st.tabs([
        "📋 Estações Cadastradas",
        "🏗️ Criar Nova", 
        "✏️ Editar Existente", 
        "🗑️ Deletar Estação"
    ])
    
    with list_tab:
        show_list_stations_tab()
    
    with create_tab:
        show_create_station_tab()
    
    with edit_tab:
        show_edit_station_tab()
        
    with delete_tab:
        show_delete_station_tab()


def show_create_sensor_tab():
    """Sub-tab para criar novo sensor"""
    st.markdown("#### 🆕 Cadastrar Novo Sensor")
    
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
            key="create_sensor_station_selector"
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
                "monitoringStationId": cast_to_int64(station_id),  # int64 conforme swagger
            }

            resp = create_sensor(token, station_id, sensor_data)
            if handle_api_response_v2(resp, "Sensor criado com sucesso!"):
                invalidate_caches_after_mutation("sensors")
                st.rerun()


def show_edit_sensor_tab():
    """Sub-tab para editar sensor existente"""
    st.markdown("#### ✏️ Editar Sensor Existente")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada. Cadastre uma estação primeiro.")
        return
    
    st.info("🚧 Funcionalidade de edição de sensores - requer seleção de sensor específico")
    
    # Seletor de estação primeiro
    station_options = {
        f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
        for station in stations
    }
    
    station_choice = st.selectbox(
        "Estação de Monitoramento",
        station_options.keys(),
        help="Selecione a estação para ver seus sensores",
        key="edit_sensor_station_selector"
    )
    station_id = station_options[station_choice]
    
    # Buscar sensores da estação selecionada
    sensors_response = get_sensors(token, station_id)
    if sensors_response and sensors_response.status_code == 200:
        sensors = sensors_response.json()
        if sensors:
            sensor_options = {
                f"Sensor ID: {sensor['id']}": sensor
                for sensor in sensors
            }
            
            selected_sensor_key = st.selectbox(
                "Sensor para Editar",
                sensor_options.keys(),
                key="edit_sensor_selector"
            )
            selected_sensor = sensor_options[selected_sensor_key]
            
            with st.form("EditarSensor"):
                new_sensor_id = st.number_input(
                    "Novo ID do Sensor *",
                    min_value=1,
                    value=selected_sensor['id'],
                    help="Novo ID para o sensor (int32)"
                )
                
                submitted = st.form_submit_button("💾 Salvar Alterações")
                
                if submitted:
                    sensor_data = {
                        "id": cast_to_int32(new_sensor_id),
                        "monitoringStationId": cast_to_int64(station_id)
                    }
                    
                    resp = update_sensor(token, station_id, selected_sensor['id'], sensor_data)
                    if handle_api_response_v2(resp, "Sensor atualizado com sucesso!"):
                        invalidate_caches_after_mutation("sensors")
                        st.rerun()
        else:
            st.info("Esta estação não possui sensores cadastrados.")
    else:
        st.error("Erro ao carregar sensores da estação.")


def show_delete_sensor_tab():
    """Sub-tab para deletar sensor"""
    st.markdown("#### 🗑️ Deletar Sensor")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada. Cadastre uma estação primeiro.")
        return
    
    # Seletor de estação primeiro
    station_options = {
        f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
        for station in stations
    }
    
    station_choice = st.selectbox(
        "Estação de Monitoramento",
        station_options.keys(),
        help="Selecione a estação para ver seus sensores",
        key="delete_sensor_station_selector"
    )
    station_id = station_options[station_choice]
    
    # Buscar sensores da estação selecionada
    sensors_response = get_sensors(token, station_id)
    if sensors_response and sensors_response.status_code == 200:
        sensors = sensors_response.json()
        if sensors:
            sensor_options = {
                f"Sensor ID: {sensor['id']}": sensor
                for sensor in sensors
            }
            
            selected_sensor_key = st.selectbox(
                "Sensor para Deletar",
                sensor_options.keys(),
                help="⚠️ Esta ação não pode ser desfeita",
                key="delete_sensor_selector"
            )
            selected_sensor = sensor_options[selected_sensor_key]
            
            st.warning("⚠️ **ATENÇÃO**: Você está prestes a deletar o sensor:")
            st.info(f"**ID:** {selected_sensor['id']}\n**Estação:** {station_choice}")
            
            if st.button("🗑️ Confirmar Exclusão", type="primary", key="delete_sensor_confirm"):
                resp = delete_sensor(token, station_id, selected_sensor['id'])
                if handle_api_response_v2(resp, "Sensor deletado com sucesso!"):
                    invalidate_caches_after_mutation("sensors")
                    st.rerun()
        else:
            st.info("Esta estação não possui sensores cadastrados.")
    else:
        st.error("Erro ao carregar sensores da estação.")


def show_list_stations_tab():
    """Sub-tab para listar estações cadastradas com cards informativos"""
    st.markdown("#### 📋 Estações Cadastradas")
    
    # Carregar dados das estações
    equipments_df = fetch_equipments()
    
    if not equipments_df.empty:
        # Cards informativos
        col1, col2, col3 = st.columns(3)

        with col1:
            ComponentLibrary.metric_card(
                title="Total de Estações", value=str(len(equipments_df)), icon="🏭"
            )

        with col2:
            avg_upper = (
                equipments_df["moistureUpperLimit"].mean()
                if "moistureUpperLimit" in equipments_df.columns
                else 0
            )
            ComponentLibrary.metric_card(
                title="Limite Médio Superior", value=f"{avg_upper:.1f}%", icon="💧"
            )

        with col3:
            stations_with_controller = (
                len(equipments_df[equipments_df["controllerId"].notna()])
                if "controllerId" in equipments_df.columns
                else 0
            )
            ComponentLibrary.metric_card(
                title="Com Controlador", value=str(stations_with_controller), icon="⚙️"
            )

        st.markdown("---")

        # Lista das estações com layout melhorado
        st.markdown("##### 🏭 Lista Completa de Estações")

        # Renomear colunas para português
        display_df = equipments_df.copy()
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

    else:
        # Estado vazio melhorado
        enhanced_empty_state(
            icon="🏭",
            title="Nenhuma estação cadastrada",
            message="Comece criando sua primeira estação de monitoramento para acompanhar os dados do seu sistema de irrigação.",
            action_label="Criar Primeira Estação",
            action_params={
                "key": "create_first_station_from_list",
            },
        )


def show_sensors_tab():
    """Tab principal para gerenciar sensores"""
    st.markdown("### 📡 Gerenciamento de Sensores")
    
    # Primeiro: Listar sensores por estação
    show_list_sensors_tab()
    
    st.markdown("---")
    
    # Depois: Funcionalidades de gerenciamento (CRUD)
    st.markdown("### ⚙️ Operações com Sensores")
    
    # Sub-tabs para operações CRUD diretamente
    create_tab, edit_tab, delete_tab = st.tabs([
        "🆕 Criar Sensor",
        "✏️ Editar Sensor", 
        "🗑️ Deletar Sensor"
    ])
    
    with create_tab:
        show_create_sensor_tab()
        
    with edit_tab:
        show_edit_sensor_tab()
        
    with delete_tab:
        show_delete_sensor_tab()


def show_create_station_tab():
    """Sub-tab para criar nova estação"""
    st.markdown("#### Cadastrar Nova Estação de Monitoramento")

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
            token,
            "Controlador (Opcional)",
            include_all_option=False,
            context="monitoring_station",
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


def show_edit_station_tab():
    """Tab para editar estação de monitoramento existente"""
    st.markdown("### ✏️ Editar Estação de Monitoramento")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada para editar.")
        return
    
    # Seletor de estação para editar
    station_options = {
        f"{station['name']} (ID: {station['id']})": station
        for station in stations
    }
    
    selected_option = st.selectbox(
        "Selecione a estação para editar",
        station_options.keys(),
        help="Selecione pela estação que deseja modificar",
        key="edit_station_selector"
    )
    selected_station = station_options[selected_option]
    
    # Card informativo da estação selecionada
    ComponentLibrary.card(
        title=f"Editando: {selected_station['name']}",
        content=f"""**ID:** {selected_station['id']}
**Coordenadas:** ({selected_station['latitude']}, {selected_station['longitude']})
**Limite Superior:** {selected_station['moistureUpperLimit']}%
**Limite Inferior:** {selected_station['moistureLowerLimit']}%""",
        icon="✏️",
        color="warning"
    )
    
    with st.form("EditarEstacao"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Nome da Estação *",
                value=selected_station['name'],
                help="Nome descritivo para identificação"
            )
            
            controller_id, controller_name = controller_selector(
                token, 
                "Controlador (Opcional)",
                include_all_option=True,
                context="edit_station"
            )
        
        with col2:
            lat_value = st.number_input(
                "Latitude *",
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
                value=float(selected_station['latitude']),
                help="Coordenada de latitude (-90 a 90)",
            )
            
            lon_value = st.number_input(
                "Longitude *",
                min_value=-180.0,
                max_value=180.0,
                format="%.6f", 
                value=float(selected_station['longitude']),
                help="Coordenada de longitude (-180 a 180)",
            )
        
        col3, col4 = st.columns(2)
        with col3:
            moisture_upper = moisture_limit_input(
                "Limite Superior de Umidade (%)",
                value=float(selected_station['moistureUpperLimit'])
            )
        
        with col4:
            moisture_lower = moisture_limit_input(
                "Limite Inferior de Umidade (%)", 
                value=float(selected_station['moistureLowerLimit'])
            )
        
        submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
        
        if submitted:
            # Validações
            coord_valid, coord_msg = validate_coordinates(lat_value, lon_value)
            if not coord_valid:
                st.error(coord_msg)
                return
                
            limits_valid, limits_msg = validate_moisture_limits(moisture_lower, moisture_upper)
            if not limits_valid:
                st.error(limits_msg)
                return
            
            # Dados para atualização conforme schema MonitoringStation
            data = {
                "id": cast_to_int64(selected_station['id']),
                "name": nome.strip(),
                "latitude": cast_to_double(lat_value),
                "longitude": cast_to_double(lon_value),
                "moistureUpperLimit": cast_to_double(moisture_upper),
                "moistureLowerLimit": cast_to_double(moisture_lower),
                "controllerId": cast_to_int64(controller_id) if controller_id else None
            }
            
            resp = update_monitoring_station(token, selected_station['id'], data)
            if handle_api_response_v2(resp, "Estação atualizada com sucesso!"):
                invalidate_caches_after_mutation("stations")
                st.rerun()


def show_delete_station_tab():
    """Tab para deletar estação de monitoramento"""
    st.markdown("### 🗑️ Deletar Estação de Monitoramento")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada para deletar.")
        return
    
    # Seletor de estação para deletar
    station_options = {
        f"{station['name']} (ID: {station['id']})": station
        for station in stations
    }
    
    selected_option = st.selectbox(
        "Selecione a estação para deletar",
        station_options.keys(),
        help="⚠️ Esta ação não pode ser desfeita",
        key="delete_station_selector"
    )
    selected_station = station_options[selected_option]
    
    # Card de confirmação
    st.warning("⚠️ **ATENÇÃO**: Você está prestes a deletar a estação:")
    ComponentLibrary.card(
        title="🗑️ Estação a ser Deletada",
        content=f"""**Nome:** {selected_station['name']}
**ID:** {selected_station['id']}
**Coordenadas:** ({selected_station['latitude']}, {selected_station['longitude']})
**Limites:** {selected_station['moistureLowerLimit']}% - {selected_station['moistureUpperLimit']}%""",
        color="error"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:  # Centralizar o botão
        if st.button("🗑️ Confirmar Exclusão", type="primary", key="delete_station_confirm"):
            with LoadingStates.spinner_with_cancel("Deletando estação..."):
                resp = delete_monitoring_station(token, selected_station['id'])
                
            if handle_api_response_v2(resp, "Estação deletada com sucesso!"):
                invalidate_caches_after_mutation("stations")
                st.rerun()


def show_manage_sensors_tab():
    """Tab para gerenciar sensores (criar, editar, deletar)"""
    st.markdown("### 📡 Gerenciar Sensores")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada. Cadastre uma estação primeiro.")
        return
    
    # Subtabs para operações de sensores
    sensor_tab1, sensor_tab2, sensor_tab3 = st.tabs(["➕ Criar Sensor", "✏️ Editar Sensor", "🗑️ Deletar Sensor"])
    
    with sensor_tab1:
        st.markdown("#### Cadastrar Novo Sensor")
        
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
                key="create_sensor_station_selector"
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
    
    with sensor_tab2:
        st.markdown("#### Editar Sensor Existente")
        st.info("🚧 Funcionalidade de edição de sensores - requer seleção de sensor específico")
        
        # Seletor de estação primeiro
        station_options = {
            f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
            for station in stations
        }
        
        station_choice = st.selectbox(
            "Estação de Monitoramento",
            station_options.keys(),
            help="Selecione a estação para ver seus sensores",
            key="edit_sensor_station_selector"
        )
        station_id = station_options[station_choice]
        
        # Buscar sensores da estação selecionada
        sensors_response = get_sensors(token, station_id)
        if sensors_response and sensors_response.status_code == 200:
            sensors = sensors_response.json()
            if sensors:
                sensor_options = {
                    f"Sensor ID: {sensor['id']}": sensor
                    for sensor in sensors
                }
                
                selected_sensor_key = st.selectbox(
                    "Sensor para Editar",
                    sensor_options.keys(),
                    key="edit_sensor_selector"
                )
                selected_sensor = sensor_options[selected_sensor_key]
                
                with st.form("EditarSensor"):
                    new_sensor_id = st.number_input(
                        "Novo ID do Sensor *",
                        min_value=1,
                        value=selected_sensor['id'],
                        help="Novo ID para o sensor (int32)"
                    )
                    
                    submitted = st.form_submit_button("💾 Salvar Alterações")
                    
                    if submitted:
                        sensor_data = {
                            "id": cast_to_int32(new_sensor_id),
                            "monitoringStationId": cast_to_int64(station_id)
                        }
                        
                        resp = update_sensor(token, station_id, selected_sensor['id'], sensor_data)
                        if handle_api_response_v2(resp, "Sensor atualizado com sucesso!"):
                            invalidate_caches_after_mutation("sensors")
                            st.rerun()
            else:
                st.info("Esta estação não possui sensores cadastrados.")
        else:
            st.error("Erro ao carregar sensores da estação.")
    
    with sensor_tab3:
        st.markdown("#### Deletar Sensor")
        
        # Seletor de estação primeiro
        station_choice = st.selectbox(
            "Estação de Monitoramento",
            station_options.keys(),
            help="Selecione a estação para ver seus sensores",
            key="delete_sensor_station_selector"
        )
        station_id = station_options[station_choice]
        
        # Buscar sensores da estação selecionada
        sensors_response = get_sensors(token, station_id)
        if sensors_response and sensors_response.status_code == 200:
            sensors = sensors_response.json()
            if sensors:
                sensor_options = {
                    f"Sensor ID: {sensor['id']}": sensor
                    for sensor in sensors
                }
                
                selected_sensor_key = st.selectbox(
                    "Sensor para Deletar",
                    sensor_options.keys(),
                    help="⚠️ Esta ação não pode ser desfeita",
                    key="delete_sensor_selector"
                )
                selected_sensor = sensor_options[selected_sensor_key]
                
                st.warning("⚠️ **ATENÇÃO**: Você está prestes a deletar o sensor:")
                st.info(f"**ID:** {selected_sensor['id']}\n**Estação:** {station_choice}")
                
                if st.button("🗑️ Confirmar Exclusão", type="primary", key="delete_sensor_confirm"):
                    resp = delete_sensor(token, station_id, selected_sensor['id'])
                    if handle_api_response_v2(resp, "Sensor deletado com sucesso!"):
                        invalidate_caches_after_mutation("sensors")
                        st.rerun()
            else:
                st.info("Esta estação não possui sensores cadastrados.")
        else:
            st.error("Erro ao carregar sensores da estação.")


def show_list_sensors_tab():
    """Tab para listar sensores de uma estação"""
    st.markdown("### 📋 Listar Sensores por Estação")
    
    token = st.session_state.get("token")
    stations = get_monitoring_stations(token)
    if not stations:
        st.warning("⚠️ Nenhuma estação cadastrada.")
        return
    
    # Seletor de estação
    station_options = {
        f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
        for station in stations
    }
    
    station_choice = st.selectbox(
        "Estação de Monitoramento",
        station_options.keys(),
        help="Selecione a estação para ver seus sensores",
        key="list_sensors_station_selector"
    )
    station_id = station_options[station_choice]
    
    # Buscar e exibir sensores
    with LoadingStates.spinner_with_cancel("Carregando sensores..."):
        sensors_response = get_sensors(token, station_id)
    
    if sensors_response and sensors_response.status_code == 200:
        sensors = sensors_response.json()
        
        if sensors:
            st.markdown(f"#### 📡 Sensores da Estação: {station_choice}")
            
            # Cards de métricas
            col1, col2 = st.columns(2)
            with col1:
                ComponentLibrary.metric_card(
                    title="Total de Sensores",
                    value=str(len(sensors)),
                    icon="📡"
                )
            
            with col2:
                ComponentLibrary.metric_card(
                    title="Estação",
                    value=station_choice.split(" (ID:")[0],
                    icon="🏭"
                )
            
            # Tabela de sensores
            df_sensors = pd.DataFrame(sensors)
            if not df_sensors.empty:
                # Renomear colunas para português
                column_mapping = {
                    "id": "ID do Sensor",
                    "monitoringStationId": "ID da Estação"
                }
                display_df = df_sensors.rename(columns=column_mapping)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("Nenhum sensor encontrado.")
        else:
            enhanced_empty_state(
                title="Nenhum Sensor Cadastrado",
                description="Esta estação não possui sensores cadastrados. Use a aba 'Gerenciar Sensores' para adicionar sensores.",
                icon="📡"
            )
    else:
        error_msg = "Erro ao carregar sensores da estação."
        if sensors_response:
            error_msg += f" Status: {sensors_response.status_code}"
        ComponentLibrary.alert(error_msg, "error")


if __name__ == "__main__":
    show()
