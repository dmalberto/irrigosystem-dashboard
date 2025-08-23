# src/water_consumptions.py
"""
Consumo de Água - Padronizado com UI Foundations v2
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from api import api_request
from src.ui_components import (
    controller_selector,
    date_range_filter,
    handle_api_response_v2,
    show_loading_state
)


def get_water_consumption(token: str, controller_id=None, period=None, start_date=None, end_date=None):
    """GET /api/consumptions/water com tratamento padronizado.
    
    Responses: 200 (Success), 400 (Bad Request), 500 (Server Error)
    """
    params = {}
    if controller_id:
        params["controllerId"] = controller_id
    if period:
        params["period"] = period
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    
    response = api_request("GET", "/api/consumptions/water", token=token, params=params)
    return response


def fetch_water_consumption(token: str, controller_id=None, period=None, start_date=None, end_date=None):
    """Busca dados de consumo de água com tratamento padronizado."""
    response = get_water_consumption(token, controller_id, period, start_date, end_date)
    
    if not response:
        st.error("Erro ao conectar com a API de consumo de água.")
        return pd.DataFrame()
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                if "date" in df.columns:
                    # Converte a data de UTC para UTC-3
                    df["date"] = pd.to_datetime(df["date"])
                    if df["date"].dt.tz is None:
                        df["date"] = df["date"].dt.tz_localize("UTC")
                    df["date"] = df["date"].dt.tz_convert("America/Sao_Paulo")
                    
                    # Formata a data para exibição no formato brasileiro
                    df["date_display"] = df["date"].dt.strftime("%d/%m/%Y %H:%M:%S")
                
                return df
            else:
                st.info("📭 Nenhum dado de consumo de água disponível para os filtros selecionados.")
                return pd.DataFrame()
        except ValueError:
            st.error("Erro ao processar resposta JSON da API de consumo de água.")
            return pd.DataFrame()
    elif response.status_code == 400:
        st.error("Parâmetros de filtro inválidos.")
        return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar consumo de água.")
        return pd.DataFrame()
    else:
        st.error(f"Erro inesperado: {response.status_code}")
        return pd.DataFrame()


# Função para processar dados de consumo de água conforme OpenAPI
def process_water_consumption(df_consumption):
    if df_consumption.empty:
        st.warning("Nenhum dado de consumo disponível.")
        return df_consumption

    # A API retorna dados conforme OpenAPI schema: WaterConsumption
    # com campos: date e consumption

    if "consumption" in df_consumption.columns:
        # Dados já têm o campo consumption, usar diretamente
        return df_consumption
    else:
        st.warning("Dados de água não possuem campo 'consumption'.")
        return df_consumption


# Função para exibir gráficos de consumo de água
def display_graphs(df):
    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return

    # Gráficos temporais
    if "consumption" in df.columns and "date_display" in df.columns:
        st.markdown("### Consumo de Água ao Longo do Tempo")
        fig1 = px.line(
            df,
            x="date_display",
            y="consumption",
            labels={"consumption": "Consumo (L)", "date_display": "Data"},
            title="Consumo de Água ao Longo do Tempo",
            markers=True,
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico de barras por período
        if len(df) > 1:
            st.markdown("### Distribuição do Consumo de Água")
            fig2 = px.bar(
                df,
                x="date_display",
                y="consumption",
                labels={"consumption": "Consumo (L)", "date_display": "Data"},
                title="Distribuição do Consumo de Água por Período",
            )
            st.plotly_chart(fig2, use_container_width=True)


# Função para exibir análise de consumo
def display_consumption_analysis(df):
    if df.empty:
        st.warning("Nenhum dado disponível para análise de consumo.")
        return

    total_consumption = df["consumption"].sum()
    avg_consumption = df["consumption"].mean()
    max_consumption = df["consumption"].max()
    min_consumption = df["consumption"].min()

    st.markdown("### Análise de Consumo de Água")
    st.markdown(f"**Consumo Total:** {total_consumption:.2f} L")
    st.markdown(f"**Consumo Médio:** {avg_consumption:.2f} L")
    st.markdown(f"**Consumo Máximo:** {max_consumption:.2f} L")
    st.markdown(f"**Consumo Mínimo:** {min_consumption:.2f} L")


def show():
    st.title("Consumo de Água")

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return

    # Filtros padronizados
    st.sidebar.header("Filtros")
    
    # Seletor de controlador padronizado
    controller_id, controller_name = controller_selector(
        token, "Controlador (Opcional)", include_all_option=True
    )
    
    # Filtro de período (conforme Swagger)
    period = st.sidebar.selectbox(
        "Período",
        ["daily", "monthly", "yearly"],
        help="Período de agregação dos dados"
    )

    # Filtros de data usando componente padronizado
    start_date, end_date = date_range_filter(max_days=90)
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

    # Botão para buscar dados
    if st.sidebar.button("🔍 Buscar Dados"):
        with show_loading_state("Carregando dados de consumo..."):
            df_consumption = fetch_water_consumption(
                token=token,
                controller_id=controller_id,
                period=period,
                start_date=start_date_str,
                end_date=end_date_str
            )

        if not df_consumption.empty:
            # Cabeçalho informativo
            if controller_id:
                st.markdown(f"**Controlador:** {controller_name}")
            st.markdown(f"**Período:** {period}")

            # Processar dados de consumo
            df_calculado = process_water_consumption(df_consumption)

            # Exibir dados
            st.subheader("💧 Dados de Consumo de Água")
            display_columns = [
                "date_display" if col == "date" else col
                for col in ["date", "consumption"]
                if col in df_calculado.columns
            ]
            st.dataframe(df_calculado[display_columns], use_container_width=True)

            # Exibir gráficos e análise
            display_graphs(df_calculado)
            display_consumption_analysis(df_calculado)
        else:
            st.info("📭 Nenhum dado disponível para os filtros selecionados.")


if __name__ == "__main__":
    show()
