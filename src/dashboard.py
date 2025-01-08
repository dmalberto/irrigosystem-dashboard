# src/dashboard.py

from datetime import date, datetime, time, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from api import api_request


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
    if response and response.status_code == 200:
        return response.json()
    else:
        st.error("Falha ao obter estações cadastradas.")
        return []


def obter_sensores_por_estacao(station_id):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []
    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)
    if response and response.status_code == 200:
        sensors = response.json()
        sensor_ids = [sensor["id"] for sensor in sensors]
        return sensor_ids
    else:
        st.error("Falha ao obter sensores da estação selecionada.")
        return []


def format_datetime(date_value, time_value):
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def fetch_data(start_date=None, end_date=None, station_id=None):
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    sensor_ids = obter_sensores_por_estacao(station_id)
    if not sensor_ids:
        st.warning("Nenhum sensor encontrado para a estação selecionada.")
        return pd.DataFrame()

    endpoint = "/api/measurements?pageSize=10000"
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    params["sensorIds"] = ",".join(map(str, sensor_ids))

    with st.spinner("Carregando dados..."):
        response = api_request("GET", endpoint, token=token, params=params)

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
            )
        rename_columns(df)
        return df
    else:
        st.error("Falha ao buscar dados da API.")
        return pd.DataFrame()


def show():
    st.title("Dashboard de Sensores")

    # Obter estações e selecionar
    estacoes = obter_estacoes_cadastradas()
    if not estacoes:
        st.warning("Nenhuma estação cadastrada.")
        return
    estacao_options = {estacao["name"]: estacao["id"] for estacao in estacoes}
    estacao_nome = st.selectbox("Selecione a Estação", list(estacao_options.keys()))
    estacao_id = estacao_options[estacao_nome]

    # Escolha de visualização
    view_option = st.selectbox(
        "Selecione a visualização",
        ["Todos os sensores por estação", "Um sensor específico"],
    )

    # Se visão for um sensor específico, selecionar o sensor
    sensor_id_selection = None
    if view_option == "Um sensor específico":
        sensor_ids = obter_sensores_por_estacao(estacao_id)
        if sensor_ids:
            # Cria um dicionário com rótulos amigáveis para os sensores
            sensor_dict = {f"Sensor #{i}": i for i in sensor_ids}
            sensor_label = st.selectbox(
                "Selecione o ID do Sensor", list(sensor_dict.keys())
            )
            sensor_id_selection = sensor_dict[sensor_label]
        else:
            st.warning("Nenhum sensor disponível para seleção.")

    # Filtros de data e hora
    end_date_default = date.today()
    start_date_default = end_date_default - timedelta(days=30)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data de Início", value=start_date_default)
    with col2:
        end_date = st.date_input("Data de Fim", value=end_date_default)

    filtrar_por_horario = st.checkbox("Deseja filtrar por horário?", value=False)
    if filtrar_por_horario:
        col3, col4 = st.columns(2)
        with col3:
            start_time = st.time_input("Hora de Início", value=time(0, 0, 0))
        with col4:
            end_time = st.time_input("Hora de Fim", value=time(23, 59, 59))
    else:
        start_time = time(0, 0, 0)
        end_time = time(23, 59, 59)

    st.markdown("---")

    variables = [
        "Tensão da Bateria (V)",
        "Temperatura da Placa (°C)",
        "Temperatura do Sensor (°C)",
        "Umidade",
        "Salinidade (uS/cm)",
        "Condutividade",
    ]
    # Todas as variáveis já selecionadas por padrão
    all_variables = variables

    # Botão para carregar dados
    if st.button("Carregar Dados"):
        if start_date > end_date:
            st.error("Data de início maior que data de fim.")
            return

        start_date_str = format_datetime(start_date, start_time)
        end_date_str = format_datetime(end_date, end_time)

        st.markdown(f"**Estação Selecionada:** {estacao_nome}")

        df = fetch_data(start_date_str, end_date_str, estacao_id)
        if df.empty:
            st.warning("Nenhum dado disponível.")
            return

        start_dt_display = (
            f"{start_date.strftime('%d/%m/%Y')} {start_time.strftime('%H:%M:%S')}"
        )
        end_dt_display = (
            f"{end_date.strftime('%d/%m/%Y')} {end_time.strftime('%H:%M:%S')}"
        )
        st.markdown(f"**Período Selecionado:** {start_dt_display} até {end_dt_display}")

        if view_option == "Um sensor específico" and sensor_id_selection is not None:
            sensor_data = df[df["ID do Sensor"] == sensor_id_selection]
            st.subheader(f"Estação: {estacao_nome} | Sensor ID: {sensor_id_selection}")

            selected_variables = st.multiselect(
                "Selecione as variáveis para plotar",
                all_variables,
                default=all_variables,
            )

            for column in selected_variables:
                fig = px.line(
                    sensor_data,
                    x="Data",
                    y=column,
                    title=column,
                    markers=True,
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.subheader(f"Estação: {estacao_nome}")

            selected_variables = st.multiselect(
                "Selecione as variáveis para plotar",
                all_variables,
                default=all_variables,
            )

            for column in selected_variables:
                fig = px.line(
                    df,
                    x="Data",
                    y=column,
                    color="ID do Sensor",
                    title=column,
                    markers=True,
                )
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show()
