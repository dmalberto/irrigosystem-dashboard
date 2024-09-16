# src/amostras.py

import io
from datetime import datetime, time

import pandas as pd
import streamlit as st
from requests import request

from config import base_url


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


# Função para exibir data e hora formatadas
def display_datetime(date_value, time_value):
    if date_value:
        if time_value:
            return datetime.combine(date_value, time_value).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        else:
            return datetime.combine(date_value, time.min).strftime("%d/%m/%Y %H:%M:%S")
    else:
        return "Não especificado"


# Função para buscar dados da API
def fetch_data(
    page=None, page_size=15, start_date=None, end_date=None, station_id=None
):
    url = f"{base_url}/api/measurements?"
    params = []

    if page is not None:
        params.append(f"page={page}")
        params.append(f"pageSize={page_size}")

    if start_date:
        params.append(f"startDate={start_date}")
    if end_date:
        params.append(f"endDate={end_date}")

    if station_id:
        params.append(f"stationId={station_id}")

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
                .dt.strftime("%d/%m/%Y %H:%M:%S")
            )
        rename_columns(df)
        return df
    else:
        st.error("Falha ao buscar dados da API.")
        return pd.DataFrame()


def obter_sensores_cadastrados(estacao_id):
    url = f"{base_url}/api/monitoring-stations/{estacao_id}/sensors"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        sensors = response.json()
        sensor_ids = [sensor["id"] for sensor in sensors]
        return sensor_ids
    else:
        st.error("Falha ao obter sensores da estação selecionada.")
        return []


# Função para carregar mais dados
def load_more():
    st.session_state.page += 1
    df_new = fetch_data(
        page=st.session_state.page,
        station_id=st.session_state.estacao_id,
    )
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
            "moisture": "Umidade",
            "salinity": "Salinidade (uS/cm)",
            "conductivity": "Condutividade",
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
    st.title("Amostras dos Sensores")

    if "page" not in st.session_state:
        st.session_state.page = 1
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()
    if "filtered" not in st.session_state:
        st.session_state.filtered = False
    if "estacao_id" not in st.session_state:
        st.session_state.estacao_id = None
    if "previous_estacao_id" not in st.session_state:
        st.session_state.previous_estacao_id = None
    if "start_date" not in st.session_state:
        st.session_state.start_date = None
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "end_date" not in st.session_state:
        st.session_state.end_date = None
    if "end_time" not in st.session_state:
        st.session_state.end_time = None

    # Obter estações cadastradas
    estacoes = obter_estacoes_cadastradas()
    if not estacoes:
        st.warning("Nenhuma estação cadastrada.")
        return

    estacao_options = {estacao["name"]: estacao["id"] for estacao in estacoes}

    # Selecionar estação (fora do expander)
    estacao_nome = st.selectbox("Selecione a Estação", estacao_options.keys())
    estacao_id = estacao_options[estacao_nome]
    st.session_state.estacao_id = estacao_id  # Salva o ID da estação selecionada

    # Se a estação selecionada mudou, resetar os dados
    if st.session_state.estacao_id != st.session_state.previous_estacao_id:
        st.session_state.page = 1
        st.session_state.data = pd.DataFrame()
        st.session_state.filtered = False
        st.session_state.previous_estacao_id = st.session_state.estacao_id

    with st.expander("Filtrar por data e hora"):
        # Filtros de data e hora
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data de Início", value=None, key="start_date")
            start_time = st.time_input("Hora de Início", value=None, key="start_time")
        with col2:
            end_date = st.date_input("Data de Fim", value=None, key="end_date")
            end_time = st.time_input("Hora de Fim", value=None, key="end_time")

        if st.button("Aplicar Filtros"):
            st.session_state.page = 1
            st.session_state.filtered = True
            st.session_state.start_date = start_date
            st.session_state.start_time = start_time
            st.session_state.end_date = end_date
            st.session_state.end_time = end_time
            start_date_str = format_datetime(start_date, start_time)
            end_date_str = format_datetime(end_date, end_time)
            st.session_state.data = fetch_data(
                start_date=start_date_str,
                end_date=end_date_str,
                station_id=st.session_state.estacao_id,
            )

    # Se o usuário não aplicou filtros, carregar dados iniciais
    if st.session_state.page == 1 and st.session_state.data.empty:
        df = fetch_data(
            page=st.session_state.page,
            station_id=st.session_state.estacao_id,
        )
        st.session_state.data = df

    if not st.session_state.data.empty:
        # Exibir cabeçalho com informações dos filtros
        estacao_info = f"**Estação Selecionada:** {estacao_nome}"
        start_dt_display = display_datetime(
            st.session_state.start_date, st.session_state.start_time
        )
        end_dt_display = display_datetime(
            st.session_state.end_date, st.session_state.end_time
        )
        data_info = f"**Período:** {start_dt_display} **até** {end_dt_display}"
        st.markdown(f"{estacao_info}  \n{data_info}")

        st.dataframe(st.session_state.data, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

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


def obter_estacoes_cadastradas():
    url = f"{base_url}/api/monitoring-stations"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        stations = response.json()
        return stations
    else:
        st.error("Falha ao obter estações cadastradas.")
        return []


# Executa a função show
if __name__ == "__main__":
    show()
