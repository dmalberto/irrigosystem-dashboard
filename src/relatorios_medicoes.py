# src/relatorios_medicoes.py

import json

import pandas as pd
import streamlit as st

from api import api_request


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

    st.markdown("### Filtros para Relatórios (POST)")

    with st.form("FiltrosDeMedicoes"):
        station_id = st.number_input("ID da Estação", min_value=1, step=1)
        sensor_ids_str = st.text_input("IDs dos Sensores (separados por vírgula)", "")
        variable = st.selectbox(
            "Variável", ["moisture", "salinity", "batteryVoltage", "temperature"]
        )
        period = st.selectbox(
            "Período", ["daily", "weekly", "monthly", "yearly", "last-year"]
        )
        submitted = st.form_submit_button("Gerar Relatórios")

    if submitted:
        # Converter sensor_ids
        sensor_ids = []
        if sensor_ids_str.strip():
            sensor_ids = [
                int(x.strip()) for x in sensor_ids_str.split(",") if x.strip().isdigit()
            ]

        filter_body = {
            "stationId": station_id,
            "sensorIds": sensor_ids if sensor_ids else None,
            "variable": variable,
            "period": period,
        }

        st.subheader("Resultado: current-average")
        resp_avg = post_current_average(token, filter_body)
        if resp_avg and resp_avg.status_code == 200:
            data_avg = resp_avg.json()
            if isinstance(data_avg, list):
                st.dataframe(pd.DataFrame(data_avg))
            elif isinstance(data_avg, dict):
                st.json(data_avg)
        else:
            st.error("Falha ao obter 'current-average'.")

        st.subheader("Resultado: report")
        resp_report = post_measurements_report(token, filter_body)
        if resp_report and resp_report.status_code == 200:
            data_report = resp_report.json()
            if isinstance(data_report, list):
                df_report = pd.DataFrame(data_report)
                st.dataframe(df_report)
            elif isinstance(data_report, dict):
                st.json(data_report)
        else:
            st.error("Falha ao obter 'report'.")


if __name__ == "__main__":
    show()
