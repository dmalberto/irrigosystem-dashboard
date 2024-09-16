# src/health_check.py

import streamlit as st
from requests import request

from config import base_url


# Função para buscar dados do health check da API
def fetch_health_check():
    url = f"{base_url}/api/health"

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return {}
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Falha ao buscar dados do health check.")
        return {}


# Função para mostrar dados de health check
def show_health_check():
    st.title("Health Check da Aplicação e Sensores")

    data = fetch_health_check()

    if data:
        # Exibir o status do broker
        broker_status = data.get("broker", False)
        broker_icon = "✅" if broker_status else "❌"
        st.markdown(f"**Broker**: {broker_icon}")

        # Exibir o status das estações de monitoramento e sensores
        for station in data.get("monitoringStations", []):
            st.subheader(f"Estação: {station['name']}")
            for sensor in station.get("sensors", []):
                sensor_status = sensor.get("status", False)
                sensor_icon = "✅" if sensor_status else "❌"
                st.markdown(f"**Sensor ID {sensor['id']}**: {sensor_icon}")


# Executa a função show_health_check
if __name__ == "__main__":
    show_health_check()
