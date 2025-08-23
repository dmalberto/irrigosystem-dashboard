# src/water_consumptions.py


import pandas as pd
import plotly.express as px
import streamlit as st

from api import api_request
from src.controllers import get_controllers


def selecionar_controlador():
    """Componente de seleção de controlador

    Retorna: (controller_id, controller_name) ou (None, None) se nenhum selecionado
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return None, None

    controllers = get_controllers(token)
    if not controllers:
        st.warning("Nenhum controlador cadastrado.")
        return None, None

    # Opção "Todos os Controladores" para não filtrar
    controller_options = {"Todos os Controladores": None}
    controller_options.update(
        {
            f"{controller['name']} (ID: {controller['id']})": controller["id"]
            for controller in controllers
        }
    )

    controller_choice = st.sidebar.selectbox(
        "Filtrar por Controlador (Opcional)",
        controller_options.keys(),
        key="agua_controller_selector",
    )
    controller_id = controller_options[controller_choice]

    return controller_id, controller_choice


# Função para buscar dados de consumo de água da API
def fetch_water_consumption(
    start_date=None, end_date=None, controller_id=None, period=None
):
    endpoint = "/api/consumptions/water"
    params = {}

    # Parâmetros conforme Swagger: controllerId (int64), period (string)
    if controller_id:
        params["controllerId"] = controller_id
    if period:
        params["period"] = period

    # Mantém compatibilidade com parâmetros de data existentes (não estão no Swagger, mas podem ser úteis)
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    response = api_request("GET", endpoint, token=token, params=params)
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
                    st.warning("Dados retornados não possuem a coluna 'date'.")
                    return df
            else:
                st.warning(
                    "Nenhum dado de consumo de água disponível para os filtros selecionados."
                )
                return pd.DataFrame()
        except ValueError:
            st.error("Falha ao decodificar a resposta JSON da API de consumo de água.")
            st.write("Conteúdo da resposta:", response.text)
            return pd.DataFrame()
    elif response.status_code == 400:
        st.error("Requisição inválida. Verifique filtros.")
        return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno ao consultar consumo de água.")
        return pd.DataFrame()
    else:
        st.error(
            f"Falha ao buscar dados de consumo de água. Status Code: {response.status_code}"
        )
        st.write("Resposta da API:", response.text)
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


# Função principal para exibir os relatórios de consumo de água
def show():
    st.title("Relatórios de Consumo de Água")

    # Filtros de data
    st.sidebar.header("Filtros de Data")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.sidebar.date_input(
            "Data de Início", value=None, key="agua_start_date"
        )
    with col2:
        end_date = st.sidebar.date_input("Data de Fim", value=None, key="agua_end_date")

    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

    # Filtro por controlador usando seletor
    st.sidebar.header("Filtros por Controlador")
    controller_id, controller_name = selecionar_controlador()

    # Botão para buscar dados
    if st.sidebar.button("Buscar Dados"):
        # Buscar dados de consumo de água
        df_consumption = fetch_water_consumption(
            start_date=start_date_str,
            end_date=end_date_str,
            controller_id=controller_id,
        )

        # Processar dados de consumo
        df_calculado = process_water_consumption(df_consumption)

        if not df_calculado.empty:
            # Exibir cabeçalho com info do controlador selecionado
            if controller_id:
                st.markdown(f"**Controlador Selecionado:** {controller_name}")

            # Exibir dados
            st.subheader("Dados de Consumo de Água")
            # Usar a coluna formatada para exibição
            display_columns = [
                "date_display" if col == "date" else col
                for col in ["date", "consumption"]
                if col in df_calculado.columns
            ]
            st.dataframe(df_calculado[display_columns])

            # Exibir gráficos
            display_graphs(df_calculado)

            # Exibir análise de consumo
            display_consumption_analysis(df_calculado)
        else:
            st.warning("Nenhum dado disponível para os filtros selecionados.")


if __name__ == "__main__":
    show()
