# src/equipamentos.py

import pandas as pd
import streamlit as st

from api import api_request
from src.utils import handle_api_response, validate_required_fields, safe_dataframe_display, create_form_section


def fetch_equipments():
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)
    data = handle_api_response(response, error_message="Falha ao buscar estações de monitoramento")
    return data if data else []


def create_monitoring_station(data):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    response = api_request("POST", "/api/monitoring-stations", token=token, json=data)
    result = handle_api_response(response, 
                                success_message="Estação de monitoramento criada com sucesso!",
                                error_message="Falha ao criar estação")
    return result is not None


def update_monitoring_station(station_id, data):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    response = api_request("PUT", f"/api/monitoring-stations/{station_id}", token=token, json=data)
    result = handle_api_response(response, 
                                success_message="Estação de monitoramento atualizada com sucesso!",
                                error_message="Falha ao atualizar estação")
    return result is not None


def delete_monitoring_station(station_id):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    response = api_request("DELETE", f"/api/monitoring-stations/{station_id}", token=token)
    result = handle_api_response(response, 
                                success_message="Estação de monitoramento excluída com sucesso!",
                                error_message="Falha ao excluir estação")
    return result is not None


def create_sensor(station_id, sensor_data):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("POST", endpoint, token=token, json=sensor_data)
    result = handle_api_response(response, 
                                success_message="Sensor criado com sucesso!",
                                error_message="Falha ao criar sensor")
    return result is not None


def update_sensor(station_id, sensor_id, sensor_data):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    endpoint = f"/api/monitoring-stations/{station_id}/sensors/{sensor_id}"
    response = api_request("PUT", endpoint, token=token, json=sensor_data)
    result = handle_api_response(response, 
                                success_message="Sensor atualizado com sucesso!",
                                error_message="Falha ao atualizar sensor")
    return result is not None


def delete_sensor(station_id, sensor_id):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return False

    endpoint = f"/api/monitoring-stations/{station_id}/sensors/{sensor_id}"
    response = api_request("DELETE", endpoint, token=token)
    result = handle_api_response(response, 
                                success_message="Sensor excluído com sucesso!",
                                error_message="Falha ao excluir sensor")
    return result is not None


def get_sensors_by_station(station_id):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)
    data = handle_api_response(response, error_message="Falha ao buscar sensores")
    return data if data else []


def show_list_stations():
    st.subheader("Estações de Monitoramento Cadastradas")
    stations = fetch_equipments()
    
    columns_mapping = {
        "id": "ID",
        "name": "Nome",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "moistureUpperLimit": "Limite Superior Umidade",
        "moistureLowerLimit": "Limite Inferior Umidade",
        "controllerId": "ID Controlador"
    }
    
    safe_dataframe_display(stations, columns_mapping, 
                          "Nenhuma estação de monitoramento cadastrada.",
                          set_index="ID")


def show_create_station():
    fields = [
        {"name": "name", "label": "Nome da Estação", "type": "text"},
        {"name": "latitude", "label": "Latitude", "type": "number", "step": 0.000001},
        {"name": "longitude", "label": "Longitude", "type": "number", "step": 0.000001},
        {"name": "moistureUpperLimit", "label": "Limite Superior de Umidade", "type": "number"},
        {"name": "moistureLowerLimit", "label": "Limite Inferior de Umidade", "type": "number"},
        {"name": "controllerId", "label": "ID do Controlador (opcional)", "type": "number", "min_value": 1}
    ]
    
    form_data = create_form_section("Criar Estação de Monitoramento", fields, "Criar")
    
    if form_data:
        required_fields = ["name", "latitude", "longitude", "moistureUpperLimit", "moistureLowerLimit"]
        if validate_required_fields(form_data, required_fields):
            # Converter controllerId para None se for 0
            if form_data["controllerId"] == 0:
                form_data["controllerId"] = None
            
            if create_monitoring_station(form_data):
                st.rerun()


def show_edit_station():
    st.subheader("Editar Estação de Monitoramento")
    stations = fetch_equipments()
    
    if not stations:
        st.info("Nenhuma estação cadastrada para editar.")
        return
    
    station_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in stations}
    selected_station_label = st.selectbox("Selecione a Estação", list(station_options.keys()))
    selected_station_id = station_options[selected_station_label]
    
    # Encontrar dados da estação
    station_data = next((s for s in stations if s['id'] == selected_station_id), None)
    
    if station_data:
        with st.form("edit_station_form"):
            name = st.text_input("Nome", value=station_data["name"])
            latitude = st.number_input("Latitude", value=float(station_data["latitude"]), step=0.000001)
            longitude = st.number_input("Longitude", value=float(station_data["longitude"]), step=0.000001)
            upper_limit = st.number_input("Limite Superior Umidade", value=float(station_data["moistureUpperLimit"]))
            lower_limit = st.number_input("Limite Inferior Umidade", value=float(station_data["moistureLowerLimit"]))
            controller_id = st.number_input("ID Controlador", value=int(station_data.get("controllerId") or 0), min_value=0)
            
            if st.form_submit_button("Atualizar"):
                update_data = {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "moistureUpperLimit": upper_limit,
                    "moistureLowerLimit": lower_limit,
                    "controllerId": int(controller_id) if controller_id > 0 else None
                }
                
                if update_monitoring_station(selected_station_id, update_data):
                    st.rerun()


def show_delete_station():
    st.subheader("Excluir Estação de Monitoramento")
    stations = fetch_equipments()
    
    if not stations:
        st.info("Nenhuma estação cadastrada para excluir.")
        return
    
    station_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in stations}
    selected_station_label = st.selectbox("Selecione a Estação", list(station_options.keys()))
    selected_station_id = station_options[selected_station_label]
    
    if st.button("Confirmar Exclusão", type="primary"):
        if delete_monitoring_station(selected_station_id):
            st.rerun()


def show_manage_sensors():
    st.subheader("Gerenciar Sensores")
    stations = fetch_equipments()
    
    if not stations:
        st.info("Nenhuma estação cadastrada.")
        return
    
    station_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in stations}
    selected_station_label = st.selectbox("Selecione a Estação", list(station_options.keys()))
    selected_station_id = station_options[selected_station_label]
    
    # Mostrar sensores existentes
    sensors = get_sensors_by_station(selected_station_id)
    if sensors:
        st.write("**Sensores da Estação:**")
        sensor_df = pd.DataFrame(sensors)
        sensor_df.rename(columns={"id": "ID", "monitoringStationId": "ID Estação"}, inplace=True)
        st.dataframe(sensor_df, use_container_width=True)
    
    # Tabs para operações
    tab1, tab2, tab3 = st.tabs(["Criar Sensor", "Editar Sensor", "Excluir Sensor"])
    
    with tab1:
        with st.form("create_sensor"):
            sensor_id = st.number_input("ID do Sensor", min_value=1, step=1)
            if st.form_submit_button("Criar"):
                sensor_data = {
                    "id": int(sensor_id),
                    "monitoringStationId": selected_station_id
                }
                if create_sensor(selected_station_id, sensor_data):
                    st.rerun()
    
    with tab2:
        if sensors:
            sensor_ids = [s["id"] for s in sensors]
            selected_sensor_id = st.selectbox("Sensor a Editar", sensor_ids)
            
            with st.form("edit_sensor"):
                new_sensor_id = st.number_input("Novo ID do Sensor", value=selected_sensor_id, min_value=1, step=1)
                if st.form_submit_button("Atualizar"):
                    sensor_data = {
                        "id": int(new_sensor_id),
                        "monitoringStationId": selected_station_id
                    }
                    if update_sensor(selected_station_id, selected_sensor_id, sensor_data):
                        st.rerun()
        else:
            st.info("Nenhum sensor para editar.")
    
    with tab3:
        if sensors:
            sensor_ids = [s["id"] for s in sensors]
            selected_sensor_id = st.selectbox("Sensor a Excluir", sensor_ids, key="delete_sensor")
            
            if st.button("Confirmar Exclusão Sensor", type="primary"):
                if delete_sensor(selected_station_id, selected_sensor_id):
                    st.rerun()
        else:
            st.info("Nenhum sensor para excluir.")


def show():
    st.title("Gerenciamento de Equipamentos")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Listar", "Criar Estação", "Editar Estação", "Excluir Estação", "Gerenciar Sensores"
    ])
    
    with tab1:
        show_list_stations()
    
    with tab2:
        show_create_station()
    
    with tab3:
        show_edit_station()
    
    with tab4:
        show_delete_station()
    
    with tab5:
        show_manage_sensors()


if __name__ == "__main__":
    show()
