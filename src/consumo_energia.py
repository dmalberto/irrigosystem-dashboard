# src/consumo_energia.py

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from requests import request


# Função para buscar dados de consumo de energia da API
def fetch_energy_consumption(start_date=None, end_date=None):
    url = f"{base_url}/api/energy-consumptions"
    params = {}

    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = request("GET", url, headers=headers, params=params)
    except Exception as e:
        st.error(f"Erro ao conectar com a API de consumo de energia: {e}")
        return pd.DataFrame()

    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                if "date" in df.columns and "consumption" in df.columns:
                    # Converte a data de UTC para UTC-3
                    df["date"] = (
                        pd.to_datetime(df["date"])
                        .dt.tz_localize("UTC")
                        .dt.tz_convert("America/Sao_Paulo")
                    )
                    return df
                else:
                    st.error(
                        "Dados retornados não possuem as colunas 'date' e 'consumption'."
                    )
                    st.write("Estrutura dos dados retornados:", data)
                    return pd.DataFrame()
            else:
                st.warning(
                    "Nenhum dado de consumo de energia disponível para os filtros selecionados."
                )
                return pd.DataFrame()
        except ValueError:
            st.error(
                "Falha ao decodificar a resposta JSON da API de consumo de energia."
            )
            st.write("Conteúdo da resposta:", response.text)
            return pd.DataFrame()
    else:
        st.error(
            f"Falha ao buscar dados de consumo de energia. Status Code: {response.status_code}"
        )
        st.write("Resposta da API:", response.text)
        return pd.DataFrame()


# Função para buscar tarifas vigentes da API
def fetch_current_tariffs():
    url = f"{base_url}/api/tariff-schedules/current"

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return {}

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = request("GET", url, headers=headers)
    except Exception as e:
        st.error(f"Erro ao conectar com a API de tarifas vigentes: {e}")
        return {}

    if response.status_code == 200:
        try:
            data = response.json()
            # Verifique se os campos esperados estão presentes
            if "diurnalRate" in data and "nightRate" in data:
                return data
            else:
                st.error(
                    "Dados de tarifas retornados não possuem os campos 'diurnalRate' e 'nightRate'."
                )
                st.write("Estrutura dos dados retornados:", data)
                return {}
        except ValueError:
            st.error("Falha ao decodificar a resposta JSON da API de tarifas vigentes.")
            st.write("Conteúdo da resposta:", response.text)
            return {}
    else:
        st.error(
            f"Falha ao buscar tarifas vigentes. Status Code: {response.status_code}"
        )
        st.write("Resposta da API:", response.text)
        return {}


# Função para calcular custos com base no consumo e nas tarifas
def calculate_costs(df_consumption, tariffs):
    if df_consumption.empty or not tariffs:
        st.warning("Dados insuficientes para calcular custos.")
        return df_consumption

    # Supondo que a tarifa possui 'diurnalRate' e 'nightRate' com respectivos valores
    diurna = tariffs.get("diurnalRate", 0)
    noturna = tariffs.get("nightRate", 0)

    # Definir horário de corte (exemplo: 18:00 para diurno/noturno)
    corte_horario = 18

    # Separar consumo diurno e noturno
    df_consumption["periodo"] = df_consumption["date"].dt.hour.apply(
        lambda x: "Diurno" if x >= corte_horario else "Noturno"
    )

    # Calcular custo
    df_consumption["custo"] = df_consumption.apply(
        lambda row: (
            row["consumption"] * diurna
            if row["periodo"] == "Diurno"
            else row["consumption"] * noturna
        ),
        axis=1,
    )

    return df_consumption


# Função para exibir gráficos de consumo e custos
def display_graphs(df):
    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return

    st.markdown("### Consumo de Energia Diurno vs Noturno")
    fig1 = px.bar(
        df.groupby("periodo")["consumption"].sum().reset_index(),
        x="periodo",
        y="consumption",
        labels={"consumption": "Consumo (kWh)", "periodo": "Período"},
        title="Consumo de Energia por Período",
        color="periodo",
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Custos de Energia Diurno vs Noturno")
    fig2 = px.bar(
        df.groupby("periodo")["custo"].sum().reset_index(),
        x="periodo",
        y="custo",
        labels={"custo": "Custo (R$)", "periodo": "Período"},
        title="Custo de Energia por Período",
        color="periodo",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Consumo ao Longo do Tempo")
    fig3 = px.line(
        df,
        x="date",
        y="consumption",
        color="periodo",
        labels={"consumption": "Consumo (kWh)", "date": "Data"},
        title="Consumo de Energia ao Longo do Tempo",
        markers=True,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Custo ao Longo do Tempo")
    fig4 = px.line(
        df,
        x="date",
        y="custo",
        color="periodo",
        labels={"custo": "Custo (R$)", "date": "Data"},
        title="Custo de Energia ao Longo do Tempo",
        markers=True,
    )
    st.plotly_chart(fig4, use_container_width=True)


# Função para exibir análise de custos
def display_cost_analysis(df):
    if df.empty:
        st.warning("Nenhum dado disponível para análise de custos.")
        return

    total_consumption = df["consumption"].sum()
    total_cost = df["custo"].sum()

    st.markdown("### Análise de Custos")
    st.markdown(f"**Consumo Total:** {total_consumption:.2f} kWh")
    st.markdown(f"**Custo Total:** R${total_cost:.2f}")

    avg_consumption = df["consumption"].mean()
    avg_cost = df["custo"].mean()

    st.markdown(f"**Consumo Médio por Registro:** {avg_consumption:.2f} kWh")
    st.markdown(f"**Custo Médio por Registro:** R${avg_cost:.2f}")


# Função para simular custos futuros
def simulate_future_costs(
    tariffs, projected_consumption_diurno, projected_consumption_noturno
):
    diurna = tariffs.get("diurnalRate", 0)
    noturna = tariffs.get("nightRate", 0)

    custo_diurno = projected_consumption_diurno * diurna
    custo_noturno = projected_consumption_noturno * noturna
    custo_total = custo_diurno + custo_noturno

    st.markdown("### Simulação de Custos Futuros")
    st.markdown(f"**Consumo Projetado Diurno:** {projected_consumption_diurno} kWh")
    st.markdown(f"**Consumo Projetado Noturno:** {projected_consumption_noturno} kWh")
    st.markdown(f"**Custo Projetado Diurno:** R${custo_diurno:.2f}")
    st.markdown(f"**Custo Projetado Noturno:** R${custo_noturno:.2f}")
    st.markdown(f"**Custo Total Projetado:** R${custo_total:.2f}")


# Função principal para exibir os relatórios de consumo de energia
def show():
    st.title("Relatórios de Consumo de Energia")

    # Filtros de data
    st.sidebar.header("Filtros de Data")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.sidebar.date_input(
            "Data de Início", value=None, key="energia_start_date"
        )
    with col2:
        end_date = st.sidebar.date_input(
            "Data de Fim", value=None, key="energia_end_date"
        )

    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

    # Botão para buscar dados
    if st.sidebar.button("Buscar Dados"):
        # Buscar dados de consumo de energia
        df_consumption = fetch_energy_consumption(
            start_date=start_date_str, end_date=end_date_str
        )

        # Buscar tarifas vigentes
        tariffs = fetch_current_tariffs()

        if tariffs:
            st.markdown("### Tarifas Vigentes")
            st.markdown(
                f"**Tarifa Diurna:** R${tariffs.get('diurnalRate', 0):.2f} por kWh"
            )
            st.markdown(
                f"**Tarifa Noturna:** R${tariffs.get('nightRate', 0):.2f} por kWh"
            )
        else:
            st.warning("Não foi possível obter as tarifas vigentes.")

        # Calcular custos
        df_calculado = calculate_costs(df_consumption, tariffs)

        if not df_calculado.empty:
            # Exibir dados
            st.subheader("Dados de Consumo e Custo")
            st.dataframe(df_calculado[["date", "consumption", "periodo", "custo"]])

            # Exibir gráficos
            display_graphs(df_calculado)

            # Exibir análise de custos
            display_cost_analysis(df_calculado)
        else:
            st.warning("Nenhum dado disponível para os filtros selecionados.")

        st.markdown("---")

    # Simulação de custos futuros
    st.subheader("Simulação de Custos Futuros")
    with st.form("Simular Custos"):
        projected_consumption_diurno = st.number_input(
            "Consumo Projetado Diurno (kWh)", min_value=0.0, step=1.0
        )
        projected_consumption_noturno = st.number_input(
            "Consumo Projetado Noturno (kWh)", min_value=0.0, step=1.0
        )
        submitted = st.form_submit_button("Simular")
        if submitted:
            tariffs = fetch_current_tariffs()
            if tariffs:
                simulate_future_costs(
                    tariffs, projected_consumption_diurno, projected_consumption_noturno
                )
            else:
                st.error("Não é possível simular custos sem tarifas vigentes.")


if __name__ == "__main__":
    show()
