# src/equipamentos.py

import pandas as pd
import streamlit as st

from api import api_request


def fetch_equipments():
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    response = api_request("GET", "/api/monitoring-stations", token=token)
    if response and response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Falha ao buscar equipamentos.")
        return pd.DataFrame()


def create_equipment(data):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return

    headers = {"Content-Type": "application/json"}
    response = api_request(
        "POST", "/api/monitoring-stations", token=token, headers=headers, json=data
    )
    if response and response.status_code == 200:
        st.success("Equipamento cadastrado com sucesso!")
    else:
        st.error("Falha ao cadastrar equipamento.")


def show():
    st.title("Cadastro de Equipamentos")

    equipments_df = fetch_equipments()
    if not equipments_df.empty:
        st.subheader("Estações de Monitoramento Cadastradas")
        st.dataframe(equipments_df)

    with st.form("Novo Equipamento"):
        equipamento_tipo = st.selectbox(
            "Tipo de Equipamento", ["Estação de Monitoramento", "Sensor"]
        )
        if equipamento_tipo == "Estação de Monitoramento":
            name = st.text_input("Nome da Estação")
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")
            moisture_upper_limit = st.number_input("Limite Superior de Umidade")
            moisture_lower_limit = st.number_input("Limite Inferior de Umidade")
            controller_id = st.number_input("ID do Controlador", min_value=0, step=1)
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                if name:
                    data = {
                        "name": name,
                        "latitude": latitude,
                        "longitude": longitude,
                        "moistureUpperLimit": moisture_upper_limit,
                        "moistureLowerLimit": moisture_lower_limit,
                        "controllerId": int(controller_id) if controller_id else None,
                    }
                    create_equipment(data)
                    st.rerun()
                else:
                    st.error("Por favor, preencha ao menos o nome da Estação.")
        else:
            # Sensor
            station_id = st.number_input("ID da Estação de Monitoramento", min_value=0)
            sensor_id = st.number_input("ID do Sensor", min_value=0)
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                if station_id and sensor_id:
                    token = st.session_state.get("token", None)
                    if not token:
                        st.error("Usuário não autenticado.")
                        return
                    headers = {"Content-Type": "application/json"}
                    endpoint = f"/api/monitoring-stations/{int(station_id)}/sensors"
                    data = {
                        "id": int(sensor_id),
                        "monitoringStationId": int(station_id),
                    }
                    response = api_request(
                        "POST", endpoint, token=token, headers=headers, json=data
                    )
                    if response and response.status_code == 200:
                        st.success("Sensor cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Falha ao cadastrar sensor.")
                else:
                    st.error("Por favor, preencha o ID da Estação e o ID do Sensor.")


if __name__ == "__main__":
    show()
