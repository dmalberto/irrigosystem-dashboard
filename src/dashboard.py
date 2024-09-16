# src/dashboard.py

from datetime import datetime, time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from requests import request

from config import base_url

# src/dashboard.py


# Definir a função obter_estacoes_cadastradas
def obter_estacoes_cadastradas():
    url = f"{base_url}/api/monitoring-stations"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        stations = response.json()
        return stations
    else:
        st.error("Falha ao obter estações cadastradas.")
        return []


def obter_sensores_por_estacao(station_id):
    if not station_id:
        return []
    url = f"{base_url}/api/monitoring-stations/{station_id}/sensors"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sensors = response.json()
        sensor_ids = [sensor["id"] for sensor in sensors]
        return sensor_ids
    else:
        st.error("Falha ao obter sensores da estação selecionada.")
        return []


def rename_columns(df):
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "date": "Data",
            "sensorId": "ID do Sensor",
            "batteryVoltage": "Tensão da Bateria (V)",
            "boardTemperature": "Temperatura da Placa (°C)",
            "sensorTemperature": "Temperatura do Sensor (°C)",
            "sampleTemperature": "Temperatura da Amostra (°C)",
            "moisture": "Umidade",
            "salinity": "Salinidade (uS/cm)",
            "conductivity": "Condutividade",
        }
        df.rename(columns=columns_mapping, inplace=True)


# Função para formatar data e hora
def format_datetime(date_value, time_value):
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        return None


# Função para buscar dados da API
def fetch_data(start_date=None, end_date=None, station_id=None):
    url = f"{base_url}/api/measurements?pageSize=10000"
    params = []

    if start_date:
        params.append(f"startDate={start_date}")
    if end_date:
        params.append(f"endDate={end_date}")

    # Filtrar pelos sensores cadastrados pelo usuário
    sensor_ids = obter_sensores_por_estacao(station_id)
    if sensor_ids:
        sensor_ids_str = ",".join(map(str, sensor_ids))
        params.append(f"sensorIds={sensor_ids_str}")
    else:
        st.warning("Nenhum sensor encontrado para a estação selecionada.")
        return pd.DataFrame()

    if params:
        url += "&" + "&".join(params)

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty and "date" in df.columns:
            # Converte a data de UTC para UTC-3
            df["date"] = (
                pd.to_datetime(df["date"])
                .dt.tz_localize("UTC")
                .dt.tz_convert("America/Sao_Paulo")
            )
        rename_columns(df)
        return df
    else:
        st.error("Falha ao buscar dados da API.")
        return pd.DataFrame()


# Função para mostrar gráficos no dashboard
def show():
    st.title("Dashboard de Sensores")

    # Obter estações cadastradas
    estacoes = obter_estacoes_cadastradas()
    if not estacoes:
        st.warning("Nenhuma estação cadastrada.")
        return

    estacao_options = {estacao["name"]: estacao["id"] for estacao in estacoes}

    # Filtros de data e hora
    with st.expander("Filtrar por data e hora"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data de Início", value=None)
            start_time = st.time_input("Hora de Início", value=None)
        with col2:
            end_date = st.date_input("Data de Fim", value=None)
            end_time = st.time_input("Hora de Fim", value=None)

        start_date_str = format_datetime(start_date, start_time)
        end_date_str = format_datetime(end_date, end_time)

    view_option = st.selectbox(
        "Selecione a visualização",
        ["Todos os sensores por estação", "Um sensor específico"],
    )

    # Exibir cabeçalho com as informações dos filtros aplicados
    start_dt_display = (
        f"{start_date.strftime('%d/%m/%Y')} {start_time.strftime('%H:%M:%S')}"
        if start_date and start_time
        else "Não especificado"
    )
    end_dt_display = (
        f"{end_date.strftime('%d/%m/%Y')} {end_time.strftime('%H:%M:%S')}"
        if end_date and end_time
        else "Não especificado"
    )
    st.markdown(f"**Período:** {start_dt_display} **até** {end_dt_display}")

    if view_option == "Um sensor específico":
        estacao_nome = st.selectbox("Selecione a Estação", estacao_options.keys())
        estacao_id = estacao_options[estacao_nome]

        df = fetch_data(
            start_date=start_date_str, end_date=end_date_str, station_id=estacao_id
        )

        if df.empty:
            st.warning("Nenhum dado disponível.")
            return

        sensor_id = st.selectbox(
            "Selecione o ID do Sensor", df["ID do Sensor"].sort_values().unique()
        )
        sensor_data = df[df["ID do Sensor"] == sensor_id]
        st.subheader(f"Estação: {estacao_nome} | Sensor ID: {sensor_id}")

        variables = st.multiselect(
            "Selecione as variáveis para plotar",
            [
                "Tensão da Bateria (V)",
                "Temperatura da Placa (°C)",
                "Temperatura do Sensor (°C)",
                "Umidade",
                "Salinidade (uS/cm)",
                "Condutividade",
            ],
            default=["Umidade"],
        )

        for column in variables:
            fig = px.line(
                sensor_data,
                x="Data",
                y=column,
                title=f"{column}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Todos os sensores por estação":
        estacao_nome = st.selectbox("Selecione a Estação", estacao_options.keys())
        estacao_id = estacao_options[estacao_nome]

        df = fetch_data(
            start_date=start_date_str, end_date=end_date_str, station_id=estacao_id
        )

        if df.empty:
            st.warning("Nenhum dado disponível.")
            return

        st.subheader(f"Estação: {estacao_nome}")

        variables = st.multiselect(
            "Selecione as variáveis para plotar",
            [
                "Tensão da Bateria (V)",
                "Temperatura da Placa (°C)",
                "Temperatura do Sensor (°C)",
                "Umidade",
                "Salinidade (uS/cm)",
                "Condutividade",
            ],
            default=["Umidade"],
        )

        for column in variables:
            fig = px.line(
                df,
                x="Data",
                y=column,
                color="ID do Sensor",
                title=f"{column}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show()
