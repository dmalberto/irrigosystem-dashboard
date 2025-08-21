import io
from datetime import datetime, time

import pandas as pd
import streamlit as st

from api import api_request
from src.utils import handle_api_response, validate_date_range


def format_datetime(date_value, time_value):
    """Formata data e hora em ISO8601 UTC Z"""
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def display_datetime(date_value, time_value):
    """Mostra data e hora em formato DD/MM/YYYY HH:MM:SS (ou 'Não especificado')."""
    if date_value:
        if time_value:
            return datetime.combine(date_value, time_value).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        return datetime.combine(date_value, time.min).strftime("%d/%m/%Y %H:%M:%S")
    return "Não especificado"


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


def obter_estacoes_cadastradas():
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)
    if response:
        return response.json()
    st.error("Falha ao obter estações cadastradas.")
    return []


def fetch_data(
    page=None, page_size=15, start_date=None, end_date=None, station_id=None
):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    endpoint = "/api/measurements?"
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
        endpoint += "&".join(params)

    with st.spinner("Carregando dados..."):
        response = api_request("GET", endpoint, token=token)
    if not response:
        return pd.DataFrame()

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty and "date" in df.columns:
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


def load_more():
    st.session_state.page += 1
    df_new = fetch_data(
        page=st.session_state.page,
        station_id=st.session_state.estacao_id,
    )
    st.session_state.data = pd.concat(
        [st.session_state.data, df_new], ignore_index=True
    )


def export_to_excel(df, selected_columns):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df[selected_columns].to_excel(writer, index=False, sheet_name="Amostras")
    writer.close()
    processed_data = output.getvalue()
    return processed_data


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

    # Obter estações
    estacoes = obter_estacoes_cadastradas()
    if not estacoes:
        st.warning("Nenhuma estação cadastrada.")
        return

    estacao_options = {estacao["name"]: estacao["id"] for estacao in estacoes}
    estacao_nome = st.selectbox("Selecione a Estação", estacao_options.keys())
    estacao_id = estacao_options[estacao_nome]
    st.session_state.estacao_id = estacao_id

    # Resetar dados se a estação mudar
    if st.session_state.estacao_id != st.session_state.previous_estacao_id:
        st.session_state.page = 1
        st.session_state.data = pd.DataFrame()
        st.session_state.filtered = False
        st.session_state.previous_estacao_id = st.session_state.estacao_id

    # Filtro de datas
    with st.expander("Filtros de Data e Hora"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data de Início", value=None, key="amostras_start_date"
            )
            start_time = st.time_input(
                "Hora de Início", value=None, key="amostras_start_time"
            )
        with col2:
            end_date = st.date_input("Data de Fim", value=None, key="amostras_end_date")
            end_time = st.time_input("Hora de Fim", value=None, key="amostras_end_time")

        if st.button("Aplicar Filtros"):
            # Valida se ambas as datas foram preenchidas
            if (start_date and end_date) and (start_date <= end_date):
                st.session_state.page = 1
                st.session_state.filtered = True
                start_date_str = format_datetime(start_date, start_time)
                end_date_str = format_datetime(end_date, end_time)
                st.session_state.data = fetch_data(
                    start_date=start_date_str,
                    end_date=end_date_str,
                    station_id=st.session_state.estacao_id,
                )
            else:
                st.error(
                    "Por favor, preencha corretamente a Data de Início e Data de Fim (Início <= Fim)."
                )

    # Se o usuário não aplicou filtros e não há dados carregados ainda, carregar a primeira página
    if st.session_state.page == 1 and st.session_state.data.empty:
        df = fetch_data(
            page=st.session_state.page,
            station_id=st.session_state.estacao_id,
        )
        st.session_state.data = df

    if not st.session_state.data.empty:
        # Exibir cabeçalho com infos
        start_dt_display = display_datetime(
            st.session_state.get("amostras_start_date"),
            st.session_state.get("amostras_start_time"),
        )
        end_dt_display = display_datetime(
            st.session_state.get("amostras_end_date"),
            st.session_state.get("amostras_end_time"),
        )
        estacao_info = f"**Estação Selecionada:** {estacao_nome}"
        # Exibe o período apenas se ele não estiver "Não especificado"
        if ("Não especificado" not in start_dt_display) or (
            "Não especificado" not in end_dt_display
        ):
            data_info = f"**Período:** {start_dt_display} até {end_dt_display}"
            st.markdown(f"{estacao_info}  \n{data_info}")
        else:
            st.markdown(estacao_info)

        st.dataframe(st.session_state.data, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

    if not st.session_state.filtered and not st.session_state.data.empty:
        if st.button("Carregar mais"):
            load_more()
            st.rerun()

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


if __name__ == "__main__":
    show()
