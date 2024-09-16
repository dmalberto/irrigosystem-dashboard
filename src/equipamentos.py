# src/equipamentos.py

import pandas as pd
import streamlit as st
from requests import request

from config import base_url


def fetch_equipments():
    url = f"{base_url}/api/monitoring-stations"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Falha ao buscar equipamentos.")
        return pd.DataFrame()


def create_equipment(data):
    url = f"{base_url}/api/monitoring-stations"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        st.success("Equipamento cadastrado com sucesso!")
    else:
        st.error("Falha ao cadastrar equipamento.")


def show():
    st.title("Cadastro de Equipamentos")

    # Exibir equipamentos cadastrados
    equipments_df = fetch_equipments()
    if not equipments_df.empty:
        st.subheader("Estações de Monitoramento Cadastradas")
        st.dataframe(equipments_df)

    # Formulário para cadastro de novo equipamento
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
                data = {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "moistureUpperLimit": moisture_upper_limit,
                    "moistureLowerLimit": moisture_lower_limit,
                    "controllerId": int(controller_id) if controller_id else None,
                }
                create_equipment(data)
                st.experimental_rerun()
        elif equipamento_tipo == "Sensor":
            station_id = st.number_input("ID da Estação de Monitoramento", min_value=0)
            sensor_id = st.number_input("ID do Sensor", min_value=0)
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                url = f"{base_url}/api/monitoring-stations/{int(station_id)}/sensors"
                token = st.session_state.get("token")
                if not token:
                    st.error("Usuário não autenticado.")
                    return
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                data = {
                    "id": int(sensor_id),
                    "monitoringStationId": int(station_id),
                }
                response = request("POST", url, headers=headers, json=data)
                if response.status_code == 200:
                    st.success("Sensor cadastrado com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Falha ao cadastrar sensor.")


if __name__ == "__main__":
    show()
