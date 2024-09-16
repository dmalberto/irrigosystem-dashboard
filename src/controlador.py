# src/controlador.py

from datetime import datetime, time

import pandas as pd
import plotly.express as px
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


# Função para buscar status dos controladores da API
def fetch_controller_statuses(controller_id, start_date=None, end_date=None):
    url = f"{base_url}/api/controllers/{controller_id}/statuses?pageSize=10000"
    params = []

    if start_date:
        params.append(f"startDate={start_date}")
    if end_date:
        params.append(f"endDate={end_date}")

    if params:
        url += "&" + "&".join(params)

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if not df.empty and "date" in df.columns:
            # Converte a data de UTC para UTC-3
            df["date"] = (
                pd.to_datetime(df["date"])
                .dt.tz_localize("UTC")
                .dt.tz_convert("America/Sao_Paulo")
            )
        return df
    else:
        st.error("Falha ao obter status do controlador.")
        return pd.DataFrame()


# Função para obter a lista de controladores
def obter_lista_controladores():
    url = f"{base_url}/api/controllers"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        controllers = response.json()
        return [controller["id"] for controller in controllers]
    else:
        st.error("Falha ao obter lista de controladores.")
        return []


# Função para exibir dados do controlador
def show():
    st.title("Dados do Controlador")

    # Selecionar controlador
    controlador_id = st.selectbox(
        "Selecione o Controlador", obter_lista_controladores()
    )

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

    df = fetch_controller_statuses(
        controlador_id,
        start_date=start_date_str,
        end_date=end_date_str,
    )

    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

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
    st.markdown(f"**Controlador ID:** {controlador_id}")
    st.markdown(f"**Período:** {start_dt_display} **até** {end_dt_display}")

    st.dataframe(df)

    # Processar dados para gráficos
    df.sort_values("date", inplace=True)

    # Gráfico do estado da bomba (operationMode)
    if "operationMode" in df.columns:
        fig = px.scatter(
            df,
            x="date",
            y="operationMode",
            title="Modo de Operação da Bomba",
            labels={"operationMode": "Modo de Operação"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gráficos dos estados das válvulas
    for valve in ["valve1", "valve2", "valve3", "valve4", "valve5"]:
        if valve in df.columns:
            df[valve + "_status"] = df[valve].apply(
                lambda x: x["status"] if pd.notnull(x) else None
            )
            fig = px.line(
                df,
                x="date",
                y=valve + "_status",
                title=f"Status da {valve}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show()
