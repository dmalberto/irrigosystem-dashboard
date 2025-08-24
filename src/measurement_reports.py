# src/measurement_reports.py


import pandas as pd
import streamlit as st

from api import api_request


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


def selecionar_sensores_multiplos(estacao_id):
    """Componente de seleção múltipla de sensores

    Args:
        estacao_id: ID da estação selecionada

    Retorna: lista de sensor_ids ou [] se nenhum selecionado
    """
    if not estacao_id:
        st.info("Selecione uma estação primeiro para carregar os sensores.")
        return []

    sensores = listar_sensores_por_estacao(estacao_id)
    if not sensores:
        st.warning("Nenhum sensor encontrado para esta estação.")
        return []

    # Criar opções com ID visível
    sensor_options = {f"Sensor ID: {sensor['id']}": sensor["id"] for sensor in sensores}

    sensor_choices = st.multiselect("Selecione os Sensores", sensor_options.keys())
    sensor_ids = [sensor_options[choice] for choice in sensor_choices]

    return sensor_ids


def post_current_average(token, filter_body):
    endpoint = "/api/measurements/current-average"
    resp = api_request("POST", endpoint, token=token, json=filter_body)
    return resp


def post_measurements_report(token, filter_body):
    endpoint = "/api/measurements/report"
    resp = api_request("POST", endpoint, token=token, json=filter_body)
    return resp


def show():
    st.title("Relatórios de Medições")

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return

    st.markdown("### Filtros para Relatórios")

    # Seleção de estação usando seletor
    station_id, station_name = selecionar_estacao()
    if station_id is None:
        return

    # Seleção múltipla de sensores usando seletor (depende da estação)
    sensor_ids = selecionar_sensores_multiplos(station_id)

    with st.form("FiltrosDeMedicoes"):
        variable = st.selectbox(
            "Variável", ["moisture", "salinity", "batteryVoltage", "temperature"]
        )
        period = st.selectbox(
            "Período", ["daily", "weekly", "monthly", "yearly", "last-year"]
        )
        submitted = st.form_submit_button("Gerar Relatórios")

    if submitted:
        # Montar filter_body conforme Swagger
        filter_body = {
            "stationId": station_id,  # int64 conforme Swagger
            "sensorIds": (
                sensor_ids if sensor_ids else None
            ),  # array de int64 conforme Swagger
            "variable": variable,
            "period": period,
        }

        st.markdown("### Resultado: current-average")
        resp_avg = post_current_average(token, filter_body)
        if resp_avg and resp_avg.status_code == 200:
            data_avg = resp_avg.json()
            if isinstance(data_avg, list):
                df_avg = pd.DataFrame(data_avg)
                # Formatar datas se existirem
                if "date" in df_avg.columns:
                    df_avg["date"] = pd.to_datetime(df_avg["date"]).dt.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                st.dataframe(df_avg)
            elif isinstance(data_avg, dict):
                st.json(data_avg)
        else:
            st.error("Falha ao obter 'current-average'.")

        st.markdown("### Resultado: report")
        resp_report = post_measurements_report(token, filter_body)
        if resp_report and resp_report.status_code == 200:
            data_report = resp_report.json()
            if isinstance(data_report, list):
                df_report = pd.DataFrame(data_report)
                # Formatar datas se existirem
                if "date" in df_report.columns:
                    df_report["date"] = pd.to_datetime(df_report["date"]).dt.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                st.dataframe(df_report)
            elif isinstance(data_report, dict):
                st.json(data_report)
        else:
            st.error("Falha ao obter 'report'.")


if __name__ == "__main__":
    show()
