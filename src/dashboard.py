import pandas as pd
import plotly.express as px
import streamlit as st
from requests import request

from config import base_url
from login import get_token


# Função para buscar dados da API
def fetch_data():
    url = f"{base_url}/api/measurements?pageSize=10000"
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        rename_columns(df)
        return df
    else:
        st.error("Falha ao buscar dados da API.")
        return pd.DataFrame()


# Função para renomear colunas
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
            "topp": "Umidade (m³/m³x100)",
            "hilhorst": "Salinidade (uS/cm)",
            "moisture": "Umidade",
        }
        df.rename(columns=columns_mapping, inplace=True)


# Função para mostrar gráficos no dashboard
def show():
    st.title("Dashboard de Sensores")

    df = fetch_data().sort_values(["ID do Sensor", "Data"])

    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    view_option = st.selectbox(
        "Selecione a visualização",
        ["Todos os sensores por coluna", "Um sensor específico"],
    )

    if view_option == "Um sensor específico":
        sensor_id = st.selectbox(
            "Selecione o ID do Sensor", df["ID do Sensor"].sort_values().unique()
        )
        sensor_data = df[df["ID do Sensor"] == sensor_id]
        st.subheader(f"Sensor ID: {sensor_id}")

        for column in [
            "Tensão da Bateria (V)",
            "Temperatura da Placa (°C)",
            "Temperatura do Sensor (°C)",
            "Temperatura da Amostra (°C)",
            "Umidade (m³/m³x100)",
            "Salinidade (uS/cm)",
            "Umidade",
        ]:
            fig = px.line(
                sensor_data,
                x="Data",
                y=column,
                title=f"{column}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

    elif view_option == "Todos os sensores por coluna":
        for column in [
            "Tensão da Bateria (V)",
            "Temperatura da Placa (°C)",
            "Temperatura do Sensor (°C)",
            "Temperatura da Amostra (°C)",
            "Umidade (m³/m³x100)",
            "Salinidade (uS/cm)",
            "Umidade",
        ]:
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
