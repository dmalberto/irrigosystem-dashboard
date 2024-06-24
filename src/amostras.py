import io
from datetime import datetime

import pandas as pd
import pytz
import streamlit as st
from requests import request

from config import base_url
from login import get_token


# Função para buscar dados da API
def fetch_data(page=None, page_size=15, start_date=None, end_date=None):
    url = f"{base_url}/api/measurements?"
    params = []

    if page is not None:
        params.append(f"page={page}")
        params.append(f"pageSize={page_size}")

    if start_date and end_date:
        params.append(f"startDate={start_date}")
        params.append(f"endDate={end_date}")

    url += "&".join(params)

    token = get_token()
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
                .dt.strftime("%d/%m/%Y %H:%M:%S")
            )
        rename_columns(df)
        df.drop(columns=["Umidade"], inplace=True)
        return df
    else:
        st.error("Falha ao buscar dados da API.")
        return pd.DataFrame()


# Função para carregar mais dados
def load_more():
    st.session_state.page += 1
    df_new = fetch_data(page=st.session_state.page)
    st.session_state.data = pd.concat(
        [st.session_state.data, df_new], ignore_index=True
    )


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


# Função para exportar dados para Excel
def export_to_excel(df, selected_columns):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df[selected_columns].to_excel(writer, index=False, sheet_name="Amostras")
    writer.save()
    processed_data = output.getvalue()
    return processed_data


# Função para mostrar dados
def show():
    st.title("Amostras do sensor")

    if "page" not in st.session_state:
        st.session_state.page = 1
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()
    if "filtered" not in st.session_state:
        st.session_state.filtered = False

    with st.expander("Filtrar por data"):
        start_date = st.date_input("Data de Início", value=None)
        start_time = st.time_input("Hora de Início", value=None)
        end_date = st.date_input("Data de Fim", value=None)
        end_time = st.time_input("Hora de Fim", value=None)

        start_date_str = (
            f"{start_date}T{start_time}:00.000000"
            if start_date and start_time
            else None
        )
        end_date_str = (
            f"{end_date}T{end_time}:00.000000" if end_date and end_time else None
        )

        if st.button("Aplicar Filtro"):
            st.session_state.page = 1
            st.session_state.filtered = True
            st.session_state.data = fetch_data(
                start_date=start_date_str, end_date=end_date_str
            )

    if st.session_state.page == 1 and st.session_state.data.empty:
        df = fetch_data(page=st.session_state.page)
        st.session_state.data = df

    st.dataframe(st.session_state.data, use_container_width=True)

    if not st.session_state.filtered and st.button("Carregar mais"):
        load_more()
        st.experimental_rerun()

    if not st.session_state.data.empty:
        with st.expander("Selecionar colunas para exportação"):
            selected_columns = []
            for column in st.session_state.data.columns:
                if st.checkbox(column, value=True):
                    selected_columns.append(column)

        if st.button("Exportar para Excel"):
            excel_data = export_to_excel(st.session_state.data, selected_columns)
            st.download_button(
                label="Baixar Excel",
                data=excel_data,
                file_name="amostras_sensor.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


# Executa a função show
if __name__ == "__main__":
    show()
