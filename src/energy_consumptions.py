# src/energy_consumptions.py
"""
Consumo de Energia - Modernizado com UI Foundations v3
ComponentLibrary, LoadingStates e design tokens aplicados.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    controller_selector,
)


def selecionar_controlador():
    """Componente de seleção de controlador usando seletor padronizado

    Retorna: (controller_id, controller_name) ou (None, None) se nenhum selecionado
    """
    token = st.session_state.get("token", None)
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return None, None

    # Usar seletor padronizado com opção "Todos"
    controller_id, controller_name = controller_selector(
        token,
        "Filtrar por Controlador (Opcional)",
        include_all_option=True,
        context="energy_consumption",
    )

    return controller_id, controller_name


# Função para buscar dados de consumo de energia da API
def fetch_energy_consumption(
    start_date=None, end_date=None, controller_id=None, period=None
):
    endpoint = "/api/consumptions/energy"
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
        st.error("Erro ao conectar com a API de consumo de energia.")
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

                    # Verifica se existe coluna de consumo para compatibilidade com UI existente
                    if "totalCost" in df.columns and "consumption" not in df.columns:
                        # Se não tem consumption mas tem totalCost, cria uma coluna estimada
                        st.info(
                            "Dados de energia recebidos com estrutura atualizada da API."
                        )

                    return df
                else:
                    st.warning("Dados retornados não possuem a coluna 'date'.")
                    return df
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
    elif response.status_code == 400:
        st.error("Requisição inválida. Verifique filtros.")
        return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno ao consultar consumo de energia.")
        return pd.DataFrame()
    else:
        st.error(
            f"Falha ao buscar dados de consumo de energia. Status Code: {response.status_code}"
        )
        st.write("Resposta da API:", response.text)
        return pd.DataFrame()


# Função para buscar tarifas vigentes da API
def fetch_current_tariffs():
    endpoint = "/api/tariff-schedules/current"

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return {}

    response = api_request("GET", endpoint, token=token)
    if not response:
        st.error("Erro ao conectar com a API de tarifas vigentes.")
        return {}

    if response.status_code == 200:
        try:
            data = response.json()
            # Campos conforme OpenAPI: daytimeTariff, nighttimeTariff, nighttimeDiscount
            if "daytimeTariff" in data and "nighttimeTariff" in data:
                return data
            else:
                st.error(
                    "Dados de tarifas retornados não possuem os campos esperados do OpenAPI."
                )
                st.write("Estrutura dos dados retornados:", data)
                return {}
        except ValueError:
            st.error("Falha ao decodificar a resposta JSON da API de tarifas vigentes.")
            st.write("Conteúdo da resposta:", response.text)
            return {}
    elif response.status_code == 404:
        st.warning("Nenhuma tarifa atual encontrada.")
        return {}
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar tarifas.")
        return {}
    else:
        st.error(
            f"Falha ao buscar tarifas vigentes. Status Code: {response.status_code}"
        )
        st.write("Resposta da API:", response.text)
        return {}


# Função para processar dados de consumo de energia conforme OpenAPI
def process_energy_consumption(df_consumption, tariffs):
    if df_consumption.empty:
        st.warning("Nenhum dado de consumo disponível.")
        return df_consumption

    # A API já retorna dados calculados conforme OpenAPI schema:
    # daytimePower, daytimeCost, nighttimePower, nighttimeCost, nighttimeDiscount, totalCost

    # Se os dados já têm custos calculados, usar diretamente
    if (
        "totalCost" in df_consumption.columns
        and "daytimeCost" in df_consumption.columns
    ):
        # Adicionar colunas compatíveis com UI existente
        df_consumption["custo"] = df_consumption["totalCost"]

        # Criar coluna de período baseada nos dados da API
        df_consumption["periodo"] = df_consumption.apply(
            lambda row: (
                "Diurno"
                if row.get("daytimePower", 0) > row.get("nighttimePower", 0)
                else "Noturno"
            ),
            axis=1,
        )

        # Para compatibilidade, usar totalCost como consumption se não existir
        if "consumption" not in df_consumption.columns:
            # Somar potências diurna e noturna para ter valor total
            df_consumption["consumption"] = df_consumption.get(
                "daytimePower", 0
            ) + df_consumption.get("nighttimePower", 0)

        return df_consumption

    # Fallback: se API não retornar dados calculados, calcular manualmente (não deveria acontecer)
    if tariffs and "daytimeTariff" in tariffs and "nighttimeTariff" in tariffs:
        st.warning(
            "Calculando custos localmente - API deveria retornar dados processados."
        )

        diurna = tariffs.get("daytimeTariff", 0)
        noturna = tariffs.get("nighttimeTariff", 0)

        # Usar horários da tarifa ou padrão
        try:
            daytime_start = int(tariffs.get("daytimeStart", "06:00:00").split(":")[0])
            daytime_end = int(tariffs.get("daytimeEnd", "18:00:00").split(":")[0])
        except (ValueError, IndexError, TypeError):
            daytime_start, daytime_end = 6, 18

        # Classificar período baseado no horário
        df_consumption["periodo"] = df_consumption["date"].dt.hour.apply(
            lambda x: "Diurno" if daytime_start <= x < daytime_end else "Noturno"
        )

        # Calcular custo manualmente
        if "consumption" in df_consumption.columns:
            df_consumption["custo"] = df_consumption.apply(
                lambda row: (
                    row["consumption"] * diurna
                    if row["periodo"] == "Diurno"
                    else row["consumption"] * noturna
                ),
                axis=1,
            )
        else:
            df_consumption["custo"] = 0

    return df_consumption


# Função para exibir gráficos de consumo e custos usando dados da API
def display_graphs(df):
    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return

    # Usar dados reais da API quando disponíveis
    has_api_data = "daytimePower" in df.columns and "nighttimePower" in df.columns

    if has_api_data:
        # Gráficos usando dados estruturados da API
        st.markdown("### Consumo de Energia Diurno vs Noturno (Dados da API)")

        # Somar todos os registros para comparação diurno/noturno
        total_daytime = df["daytimePower"].sum()
        total_nighttime = df["nighttimePower"].sum()

        period_data = pd.DataFrame(
            {
                "periodo": ["Diurno", "Noturno"],
                "power": [total_daytime, total_nighttime],
            }
        )

        fig1 = px.bar(
            period_data,
            x="periodo",
            y="power",
            labels={"power": "Potência (kW)", "periodo": "Período"},
            title="Consumo de Energia por Período",
            color="periodo",
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico de custos usando dados da API
        if "daytimeCost" in df.columns and "nighttimeCost" in df.columns:
            total_daytime_cost = df["daytimeCost"].sum()
            total_nighttime_cost = df["nighttimeCost"].sum()

            cost_data = pd.DataFrame(
                {
                    "periodo": ["Diurno", "Noturno"],
                    "custo": [total_daytime_cost, total_nighttime_cost],
                }
            )

            st.markdown("### Custos de Energia Diurno vs Noturno")
            fig2 = px.bar(
                cost_data,
                x="periodo",
                y="custo",
                labels={"custo": "Custo (R$)", "periodo": "Período"},
                title="Custo de Energia por Período",
                color="periodo",
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Gráficos temporais (compatibilidade com implementação anterior)
    if "consumption" in df.columns and "date_display" in df.columns:
        st.markdown("### Consumo ao Longo do Tempo")
        fig3 = px.line(
            df,
            x="date_display",
            y="consumption",
            color="periodo" if "periodo" in df.columns else None,
            labels={"consumption": "Consumo (kWh)", "date_display": "Data"},
            title="Consumo de Energia ao Longo do Tempo",
            markers=True,
        )
        st.plotly_chart(fig3, use_container_width=True)

    if "custo" in df.columns and "date_display" in df.columns:
        st.markdown("### Custo ao Longo do Tempo")
        fig4 = px.line(
            df,
            x="date_display",
            y="custo",
            color="periodo" if "periodo" in df.columns else None,
            labels={"custo": "Custo (R$)", "date_display": "Data"},
            title="Custo de Energia ao Longo do Tempo",
            markers=True,
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Se tem dados da API, mostrar também gráfico de custo total
    if "totalCost" in df.columns and "date_display" in df.columns:
        st.markdown("### Custo Total ao Longo do Tempo (API)")
        fig5 = px.line(
            df,
            x="date_display",
            y="totalCost",
            labels={"totalCost": "Custo Total (R$)", "date_display": "Data"},
            title="Custo Total de Energia (Dados da API)",
            markers=True,
        )
        st.plotly_chart(fig5, use_container_width=True)


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


# Função para simular custos futuros usando tarifas do OpenAPI
def simulate_future_costs(
    tariffs, projected_consumption_diurno, projected_consumption_noturno
):
    # Usar campos corretos do OpenAPI
    diurna = tariffs.get("daytimeTariff", 0)
    noturna = tariffs.get("nighttimeTariff", 0)
    desconto = tariffs.get("nighttimeDiscount", 0)

    # Aplicar desconto na tarifa noturna se especificado
    tarifa_noturna_com_desconto = noturna * (1 - desconto / 100)

    custo_diurno = projected_consumption_diurno * diurna
    custo_noturno = projected_consumption_noturno * tarifa_noturna_com_desconto
    custo_total = custo_diurno + custo_noturno

    st.markdown("### Simulação de Custos Futuros")
    st.markdown(f"**Consumo Projetado Diurno:** {projected_consumption_diurno} kWh")
    st.markdown(f"**Consumo Projetado Noturno:** {projected_consumption_noturno} kWh")
    st.markdown(f"**Tarifa Diurna:** R${diurna:.4f} por kWh")
    st.markdown(f"**Tarifa Noturna:** R${noturna:.4f} por kWh")
    if desconto > 0:
        st.markdown(f"**Desconto Noturno:** {desconto:.1f}%")
        st.markdown(
            f"**Tarifa Noturna com Desconto:** R${tarifa_noturna_com_desconto:.4f} por kWh"
        )
    st.markdown(f"**Custo Projetado Diurno:** R${custo_diurno:.2f}")
    st.markdown(f"**Custo Projetado Noturno:** R${custo_noturno:.2f}")
    st.markdown(f"**Custo Total Projetado:** R${custo_total:.2f}")


# Função principal para exibir os relatórios de consumo de energia
def show():
    st.title("⚡ Relatórios de Consumo de Energia")

    # Filtros com layout melhorado
    with st.expander("🔍 Filtros de Consulta", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Data de Início", value=None, key="energia_start_date"
            )

        with col2:
            end_date = st.date_input("Data de Fim", value=None, key="energia_end_date")

        start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None

        # Filtro por controlador usando seletor padronizado
        controller_id, controller_name = selecionar_controlador()

    # Botão para buscar dados com melhor visual
    if st.button("📊 Buscar Dados de Consumo", type="primary"):
        # Buscar dados com loading states melhorados
        with LoadingStates.progress_with_status(
            "Consultando dados de energia...", 100
        ) as (progress, status, container):
            progress.progress(30)
            status.text("Buscando dados de consumo...")

            df_consumption = fetch_energy_consumption(
                start_date=start_date_str,
                end_date=end_date_str,
                controller_id=controller_id,
            )

            progress.progress(70)
            status.text("Obtendo tarifas vigentes...")

            tariffs = fetch_current_tariffs()

            progress.progress(100)
            status.text("Processando dados...")

        # Cards informativos das tarifas
        if tariffs:
            st.markdown("### 💰 Tarifas Vigentes")

            col1, col2, col3 = st.columns(3)

            with col1:
                ComponentLibrary.metric_card(
                    title="Tarifa Diurna",
                    value=f"R$ {tariffs.get('daytimeTariff', 0):.4f}/kWh",
                    icon="☀️",
                )

            with col2:
                ComponentLibrary.metric_card(
                    title="Tarifa Noturna",
                    value=f"R$ {tariffs.get('nighttimeTariff', 0):.4f}/kWh",
                    icon="🌙",
                )

            with col3:
                discount = tariffs.get("nighttimeDiscount", 0)
                ComponentLibrary.metric_card(
                    title="Desconto Noturno",
                    value=f"{discount:.1f}%" if discount > 0 else "N/A",
                    icon="💸",
                )
        else:
            ComponentLibrary.alert(
                "Não foi possível obter as tarifas vigentes.", "warning"
            )

        # Processar dados de consumo
        df_calculado = process_energy_consumption(df_consumption, tariffs)

        if not df_calculado.empty:
            # Card informativo do controlador selecionado
            if controller_id and controller_name != "Todos os Controladores":
                ComponentLibrary.card(
                    title="⚙️ Controlador Selecionado",
                    content=f"Dados filtrados para: **{controller_name}**",
                    color="info",
                )

            # Análise resumida com cards
            if (
                "consumption" in df_calculado.columns
                and "custo" in df_calculado.columns
            ):
                total_consumption = df_calculado["consumption"].sum()
                total_cost = df_calculado["custo"].sum()
                avg_cost = df_calculado["custo"].mean()

                col1, col2, col3 = st.columns(3)

                with col1:
                    ComponentLibrary.metric_card(
                        title="Consumo Total",
                        value=f"{total_consumption:.2f} kWh",
                        icon="⚡",
                    )

                with col2:
                    ComponentLibrary.metric_card(
                        title="Custo Total", value=f"R$ {total_cost:.2f}", icon="💰"
                    )

                with col3:
                    ComponentLibrary.metric_card(
                        title="Custo Médio",
                        value=f"R$ {avg_cost:.2f} (por registro)",
                        icon="📊",
                    )

                st.markdown("---")

            # Exibir dados em tabela
            st.markdown("### 📋 Dados Detalhados de Consumo")
            display_columns = [
                "date_display" if col == "date" else col
                for col in ["date", "consumption", "periodo", "custo"]
            ]

            # Filtrar apenas colunas que existem
            available_columns = [
                col for col in display_columns if col in df_calculado.columns
            ]
            if available_columns:
                st.dataframe(df_calculado[available_columns], use_container_width=True)

            # Exibir gráficos
            display_graphs(df_calculado)

            # Exibir análise de custos
            display_cost_analysis(df_calculado)
        else:
            enhanced_empty_state(
                title="Nenhum Dado de Consumo Encontrado",
                description="Não há registros de consumo de energia para os filtros selecionados. Tente ajustar o período ou o controlador.",
                icon="⚡",
                action_button={
                    "label": "🔄 Ajustar Filtros",
                    "key": "adjust_energy_filters",
                },
            )

        st.markdown("---")

    # Seção de simulação com melhor visual
    st.markdown("---")
    st.markdown("### 🔮 Simulação de Custos Futuros")

    with st.expander("💡 Simular Consumo Projetado", expanded=False):
        with st.form("Simular Custos"):
            col1, col2 = st.columns(2)

            with col1:
                projected_consumption_diurno = st.number_input(
                    "Consumo Projetado Diurno (kWh)",
                    min_value=0.0,
                    step=1.0,
                    value=100.0,
                    help="Consumo esperado durante o período diurno",
                )

            with col2:
                projected_consumption_noturno = st.number_input(
                    "Consumo Projetado Noturno (kWh)",
                    min_value=0.0,
                    step=1.0,
                    value=50.0,
                    help="Consumo esperado durante o período noturno",
                )

            submitted = st.form_submit_button("🧮 Calcular Simulação", type="primary")

            if submitted:
                with LoadingStates.spinner_with_cancel("Calculando simulação..."):
                    tariffs = fetch_current_tariffs()

                if tariffs:
                    simulate_future_costs(
                        tariffs,
                        projected_consumption_diurno,
                        projected_consumption_noturno,
                    )
                else:
                    ComponentLibrary.alert(
                        "Não é possível simular custos sem tarifas vigentes. Verifique a configuração das tarifas.",
                        "error",
                    )


if __name__ == "__main__":
    show()
