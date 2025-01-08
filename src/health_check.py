import streamlit as st

from api import api_request


def fetch_health_check():
    token = st.session_state.get("token", None)
    if not token:
        return {}
    response = api_request("GET", "/api/health", token=token)
    if response and response.status_code == 200:
        return response.json()
    return {}


def show_health_in_sidebar():
    # Obter dados
    data = fetch_health_check()
    if not data:
        st.write("Falha ao obter Health Check.")
        return

    st.markdown("## Status")

    # Mostrando status do broker
    broker_status = data.get("broker", False)
    broker_icon = "✅" if broker_status else "❌"
    st.write(f"Broker: {broker_icon}")

    monitoring_stations = data.get("monitoringStations", [])
    if not monitoring_stations:
        st.write("Nenhuma estação encontrada.")
    else:
        grouped_stations = {}
        for station in monitoring_stations:
            station_name = station["name"]
            grouped_stations.setdefault(station_name, [])
            for sensor in station.get("sensors", []):
                sensor_icon = "✅" if sensor.get("status", False) else "❌"
                grouped_stations[station_name].append(
                    f"Sensor #{sensor['id']}: {sensor_icon}"
                )

        for group, sensors in grouped_stations.items():
            st.markdown(f"### {group}")
            for sensor in sensors:
                st.write(sensor)
