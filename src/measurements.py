import io
from datetime import datetime, time

import pandas as pd
import streamlit as st

from api import api_request


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


def listar_estacoes():
    """GET /api/monitoring-stations

    Responses: 200 (Success), 500 (Server Error)
    Retorna lista de estações para alimentar seletor
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)

    if not response:
        st.error("Erro ao conectar com a API de estações.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON das estações.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar estações.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar estações: {response.status_code}")
        return []


def listar_sensores_por_estacao(station_id):
    """GET /api/monitoring-stations/{stationId}/sensors

    Parâmetro: stationId (int64) no path
    Responses: 200 (Success), 500 (Server Error)
    Retorna lista de sensores para alimentar seletor
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)

    if not response:
        st.error("Erro ao conectar com a API de sensores.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON dos sensores.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar sensores.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar sensores: {response.status_code}")
        return []


def selecionar_estacao():
    """Componente de seleção de estação

    Retorna: (estacao_id, estacao_nome) ou (None, None) se nenhuma selecionada
    """
    estacoes = listar_estacoes()
    if not estacoes:
        st.warning("Nenhuma estação cadastrada.")
        return None, None

    # Criar opções com nome + ID visível
    estacao_options = {
        f"{estacao['name']} (ID: {estacao['id']})": estacao["id"]
        for estacao in estacoes
    }
    estacao_nome = st.selectbox("Selecione a Estação", estacao_options.keys())
    estacao_id = estacao_options[estacao_nome]

    return estacao_id, estacao_nome


def selecionar_sensor(estacao_id):
    """Componente de seleção de sensor

    Args:
        estacao_id: ID da estação selecionada

    Retorna: sensor_id ou None se nenhum selecionado
    """
    if not estacao_id:
        st.info("Selecione uma estação primeiro para carregar os sensores.")
        return None

    sensores = listar_sensores_por_estacao(estacao_id)
    if not sensores:
        st.warning("Nenhum sensor encontrado para esta estação.")
        return None

    # Criar opções com ID visível
    sensor_options = {"Todos os Sensores": None}
    sensor_options.update(
        {f"Sensor ID: {sensor['id']}": sensor["id"] for sensor in sensores}
    )

    sensor_choice = st.selectbox("Filtrar por Sensor (Opcional)", sensor_options.keys())
    sensor_id = sensor_options[sensor_choice]

    return sensor_id


def obter_estacoes_cadastradas():
    """GET /api/monitoring-stations

    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)

    if not response:
        st.error("Erro ao conectar com a API de estações.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON das estações.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar estações.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar estações: {response.status_code}")
        return []


def obter_sensores_por_estacao(station_id):
    """GET /api/monitoring-stations/{stationId}/sensors

    Parâmetro: stationId (int64) no path
    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)

    if not response:
        st.error("Erro ao conectar com a API de sensores.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON dos sensores.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar sensores.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar sensores: {response.status_code}")
        return []


def fetch_data(
    start_date=None,
    end_date=None,
    station_id=None,
    sensor_id=None,
    page=1,
    page_size=15,
    sort="desc",
):
    """
    GET /api/measurements

    Parâmetros conforme Swagger:
    - startDate (string, date-time)
    - endDate (string, date-time)
    - stationId (integer, int32)
    - sensorId (integer, int32)
    - page (integer, int32, default: 1)
    - pageSize (integer, int32, default: 15)
    - sort (string, default: desc)

    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    endpoint = "/api/measurements"
    params = {}

    # Parâmetros conforme nomes exatos do Swagger
    if page is not None:
        params["page"] = page
        params["pageSize"] = page_size

    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    # stationId como int32 conforme Swagger
    if station_id:
        params["stationId"] = int(station_id)

    # sensorId como int32 conforme Swagger
    if sensor_id:
        params["sensorId"] = int(sensor_id)

    # sort parameter conforme Swagger
    if sort:
        params["sort"] = sort

    with st.spinner("Carregando dados..."):
        response = api_request("GET", endpoint, token=token, params=params)

    if not response:
        st.error("Erro ao conectar com a API de medições.")
        return pd.DataFrame()

    if response.status_code == 200:
        try:
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
        except ValueError:
            st.error("Erro ao processar resposta JSON da API.")
            return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar medições.")
        return pd.DataFrame()
    else:
        st.error(f"Erro inesperado ao buscar dados: {response.status_code}")
        return pd.DataFrame()


def load_more():
    """
    Carrega próxima página de dados de medições de sensores.

    Implementa paginação incremental concatenando novos dados aos existentes.

    Side Effects:
        - Incrementa st.session_state.page em 1
        - Modifica st.session_state.data via pd.concat() com ignore_index=True
        - Utiliza st.session_state.estacao_id para filtrar dados por estação
        - Utiliza st.session_state.sensor_id para filtrar por sensor específico

    Behavior:
        - Busca dados da próxima página usando fetch_data()
        - Concatena resultados aos dados já carregados
        - Mantém ordem cronológica através de ignore_index=True
    """
    st.session_state.page += 1
    df_new = fetch_data(
        page=st.session_state.page,
        station_id=st.session_state.estacao_id,
        sensor_id=st.session_state.sensor_id,
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
    st.title("Medições dos Sensores")

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
    if "sensor_id" not in st.session_state:
        st.session_state.sensor_id = None

    # Seleção de estação usando seletor
    estacao_id, estacao_nome = selecionar_estacao()
    if estacao_id is None:
        return
    st.session_state.estacao_id = estacao_id

    # Seleção de sensor usando seletor (depende da estação)
    sensor_id = selecionar_sensor(estacao_id)
    st.session_state.sensor_id = sensor_id

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
                    sensor_id=sensor_id,
                    page=1,  # Reset para primeira página
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
            sensor_id=sensor_id,
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

        # Exibir dados
        st.dataframe(st.session_state.data, use_container_width=True)

        # Botão para carregar mais dados
        if len(st.session_state.data) >= 15:  # Se há pelo menos uma página completa
            if st.button("Carregar Mais Dados"):
                load_more()
                st.rerun()

        # Exportar dados
        if not st.session_state.data.empty:
            st.markdown("### Exportar Dados")
            selected_columns = st.multiselect(
                "Selecione as colunas para exportar:",
                st.session_state.data.columns.tolist(),
                default=st.session_state.data.columns.tolist(),
            )

            if selected_columns:
                excel_data = export_to_excel(st.session_state.data, selected_columns)
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="amostras_sensores.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")


if __name__ == "__main__":
    show()
