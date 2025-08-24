# src/consumptions.py
"""
Tela Unificada de Consumos - Energia e Água
Padronizada com UI Foundations v2 e ComponentLibrary
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date, timedelta

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    controller_selector,
    format_datetime_for_api,
    handle_api_response_v2,
)


# ============================================================================
# FUNÇÕES PARA CONSUMO DE ENERGIA
# ============================================================================

def get_energy_consumption(token: str, controller_id=None, period=None):
    """GET /api/consumptions/energy
    
    NOTA: Este endpoint pode não estar implementado na API atual.
    Swagger indica sua existência, mas API retorna 404.
    
    Parâmetros conforme Swagger:
    - controllerId (int64, opcional): ID do controlador
    - period (string, opcional): Período de agregação
    """
    params = {}
    if controller_id:
        params["controllerId"] = controller_id
    if period:
        params["period"] = period
    
    response = api_request("GET", "/api/consumptions/energy", token=token, params=params)
    return response


def fetch_energy_consumption(token: str, controller_id=None, period=None):
    """Busca dados de consumo de energia com tratamento padronizado."""
    response = get_energy_consumption(token, controller_id, period)
    
    if not response:
        ComponentLibrary.alert("Erro ao conectar com a API de consumo de energia.", "error")
        return pd.DataFrame()
    
    if response.status_code == 404:
        ComponentLibrary.alert(
            "Endpoint de consumo de energia não está disponível na API atual. "
            "Verifique se o endpoint /api/consumptions/energy foi implementado no servidor.",
            "warning"
        )
        return pd.DataFrame()
    elif response.status_code == 200:
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
                
                # Calcula consumo total a partir dos campos do swagger
                if "daytimePower" in df.columns and "nighttimePower" in df.columns:
                    df["total_power"] = df["daytimePower"] + df["nighttimePower"]
                
                return df
            else:
                return pd.DataFrame()
        except ValueError:
            ComponentLibrary.alert("Erro ao processar resposta JSON da API de energia.", "error")
            return pd.DataFrame()
    else:
        ComponentLibrary.alert(f"Erro na API de energia: HTTP {response.status_code}", "error")
        return pd.DataFrame()


# ============================================================================
# FUNÇÕES PARA CONSUMO DE ÁGUA
# ============================================================================

def get_water_consumption(token: str, controller_id=None, period=None):
    """GET /api/consumptions/water
    
    NOTA: Este endpoint pode não estar implementado na API atual.
    Swagger indica sua existência, mas API pode retornar 404.
    
    Parâmetros conforme Swagger:
    - controllerId (int64, opcional): ID do controlador
    - period (string, opcional): Período de agregação
    """
    params = {}
    if controller_id:
        params["controllerId"] = controller_id
    if period:
        params["period"] = period
    
    response = api_request("GET", "/api/consumptions/water", token=token, params=params)
    return response


def fetch_water_consumption(token: str, controller_id=None, period=None):
    """Busca dados de consumo de água com tratamento padronizado."""
    response = get_water_consumption(token, controller_id, period)
    
    if not response:
        ComponentLibrary.alert("Erro ao conectar com a API de consumo de água.", "error")
        return pd.DataFrame()
    
    if response.status_code == 404:
        ComponentLibrary.alert(
            "Endpoint de consumo de água não está disponível na API atual. "
            "Verifique se o endpoint /api/consumptions/water foi implementado no servidor.",
            "warning"
        )
        return pd.DataFrame()
    elif response.status_code == 200:
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
                return pd.DataFrame()
        except ValueError:
            ComponentLibrary.alert("Erro ao processar resposta JSON da API de água.", "error")
            return pd.DataFrame()
    else:
        ComponentLibrary.alert(f"Erro na API de água: HTTP {response.status_code}", "error")
        return pd.DataFrame()


# ============================================================================
# FUNÇÕES DE TARIFAS E SIMULAÇÃO
# ============================================================================

def fetch_current_tariffs(token):
    """Busca tarifas vigentes da API.
    
    GET /api/tariff-schedules/current
    Retorna objeto TariffSchedule conforme OpenAPI.
    """
    endpoint = "/api/tariff-schedules/current"
    response = api_request("GET", endpoint, token=token)
    
    if not response:
        ComponentLibrary.alert("Erro ao conectar com a API de tarifas vigentes.", "error")
        return {}
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Campos conforme OpenAPI: daytimeTariff, nighttimeTariff, nighttimeDiscount
            if "daytimeTariff" in data and "nighttimeTariff" in data:
                return data
            else:
                ComponentLibrary.alert("Dados de tarifas não possuem os campos esperados.", "error")
                return {}
        except ValueError:
            ComponentLibrary.alert("Erro ao processar resposta JSON da API de tarifas.", "error")
            return {}
    elif response.status_code == 404:
        ComponentLibrary.alert("Nenhuma tarifa atual encontrada.", "warning")
        return {}
    elif response.status_code == 500:
        ComponentLibrary.alert("Erro interno do servidor ao buscar tarifas.", "error")
        return {}
    else:
        ComponentLibrary.alert(f"Falha ao buscar tarifas. Status: {response.status_code}", "error")
        return {}


def simulate_future_costs(tariffs, projected_consumption_diurno, projected_consumption_noturno):
    """Simula custos futuros usando tarifas do OpenAPI."""
    # Usar campos corretos do OpenAPI
    diurna = tariffs.get("daytimeTariff", 0)
    noturna = tariffs.get("nighttimeTariff", 0)
    desconto = tariffs.get("nighttimeDiscount", 0)

    # Aplicar desconto na tarifa noturna se especificado
    tarifa_noturna_com_desconto = noturna * (1 - desconto / 100)

    custo_diurno = projected_consumption_diurno * diurna
    custo_noturno = projected_consumption_noturno * tarifa_noturna_com_desconto
    custo_total = custo_diurno + custo_noturno

    # Resultados em cards visuais
    st.markdown("### 📊 Resultados da Simulação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ComponentLibrary.metric_card(
            title="Custo Diurno",
            value=f"R$ {custo_diurno:.2f}",
            delta=f"{projected_consumption_diurno} kWh",
            icon="☀️"
        )
    
    with col2:
        ComponentLibrary.metric_card(
            title="Custo Noturno",
            value=f"R$ {custo_noturno:.2f}",
            delta=f"{projected_consumption_noturno} kWh",
            icon="🌙"
        )
    
    with col3:
        ComponentLibrary.metric_card(
            title="Custo Total",
            value=f"R$ {custo_total:.2f}",
            delta=f"Projetado",
            icon="💰"
        )
    
    # Detalhes da simulação
    ComponentLibrary.card(
        title="📋 Detalhes da Simulação",
        content=f"""**Tarifas Aplicadas:**
- **Diurna:** R$ {diurna:.4f}/kWh
- **Noturna:** R$ {noturna:.4f}/kWh

**Desconto:** {desconto:.1f}% (tarifa final noturna: R$ {tarifa_noturna_com_desconto:.4f}/kWh)

**Consumos Projetados:**
- **Diurno:** {projected_consumption_diurno} kWh
- **Noturno:** {projected_consumption_noturno} kWh""",
        color="info"
    )


# ============================================================================
# PROCESSAMENTO DE DADOS
# ============================================================================

def process_energy_consumption(df_consumption, tariffs=None):
    """Processa dados de energia para compatibilidade com UI existente."""
    if df_consumption.empty:
        return df_consumption

    # A API retorna dados conforme OpenAPI schema: daytimePower, nighttimePower, totalCost, etc.
    # Adicionar colunas de compatibilidade para análise detalhada
    
    # Se tem dados calculados da API, usar diretamente
    if "totalCost" in df_consumption.columns and "daytimeCost" in df_consumption.columns:
        # Adicionar coluna de custo compatível
        df_consumption["custo"] = df_consumption["totalCost"]
        
        # Criar coluna de período baseada nos dados da API
        df_consumption["periodo"] = df_consumption.apply(
            lambda row: (
                "Diurno" if row.get("daytimePower", 0) > row.get("nighttimePower", 0) else "Noturno"
            ),
            axis=1
        )
        
        # Criar coluna consumption para compatibilidade (somar potências)
        if "consumption" not in df_consumption.columns:
            df_consumption["consumption"] = (
                df_consumption.get("daytimePower", 0) + df_consumption.get("nighttimePower", 0)
            )
    
    # Fallback: se API não retornar dados calculados, tentar calcular manualmente
    elif tariffs and "daytimeTariff" in tariffs and "consumption" in df_consumption.columns:
        diurna = tariffs.get("daytimeTariff", 0)
        noturna = tariffs.get("nighttimeTariff", 0)
        
        # Classificar período baseado no horário (se temos timestamp)
        if "date" in df_consumption.columns:
            try:
                daytime_start = int(tariffs.get("daytimeStart", "06:00:00").split(":")[0])
                daytime_end = int(tariffs.get("daytimeEnd", "18:00:00").split(":")[0])
            except (ValueError, IndexError, TypeError):
                daytime_start, daytime_end = 6, 18
                
            df_consumption["periodo"] = pd.to_datetime(df_consumption["date"]).dt.hour.apply(
                lambda x: "Diurno" if daytime_start <= x < daytime_end else "Noturno"
            )
            
            # Calcular custo baseado no período
            df_consumption["custo"] = df_consumption.apply(
                lambda row: (
                    row["consumption"] * diurna if row["periodo"] == "Diurno" 
                    else row["consumption"] * noturna
                ),
                axis=1
            )
        else:
            # Sem dados de horário, assumir distribuição equilibrada
            df_consumption["custo"] = df_consumption.get("consumption", 0) * ((diurna + noturna) / 2)

    return df_consumption


# ============================================================================
# COMPONENTES DE VISUALIZAÇÃO
# ============================================================================

def display_energy_graphs(df):
    """Exibe gráficos de consumo de energia conforme swagger."""
    if df.empty:
        enhanced_empty_state(
            title="Nenhum Dado de Energia",
            description="Não há dados de consumo de energia para exibir gráficos.",
            icon="⚡"
        )
        return

    # Usar total_power calculado ou campos separados conforme swagger
    if "total_power" in df.columns and "date_display" in df.columns:
        st.markdown("### 📈 Consumo Total de Energia ao Longo do Tempo")
        fig1 = px.line(
            df,
            x="date_display",
            y="total_power",
            labels={"total_power": "Consumo Total (kWh)", "date_display": "Data"},
            title="Consumo Total de Energia (Diurno + Noturno)",
            markers=True,
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico com breakdown diurno/noturno
        if "daytimePower" in df.columns and "nighttimePower" in df.columns:
            st.markdown("### 📊 Breakdown: Consumo Diurno vs Noturno")
            fig2 = px.bar(
                df.melt(
                    id_vars=["date_display"], 
                    value_vars=["daytimePower", "nighttimePower"],
                    var_name="Período",
                    value_name="Consumo"
                ),
                x="date_display",
                y="Consumo",
                color="Período",
                labels={"Consumo": "Consumo (kWh)", "date_display": "Data"},
                title="Distribuição do Consumo: Diurno vs Noturno",
            )
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico de custos
        if "totalCost" in df.columns:
            st.markdown("### 💰 Custos de Energia")
            fig3 = px.line(
                df,
                x="date_display",
                y="totalCost",
                labels={"totalCost": "Custo Total (R$)", "date_display": "Data"},
                title="Custo Total de Energia ao Longo do Tempo",
                markers=True,
            )
            fig3.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig3, use_container_width=True)


def display_water_graphs(df):
    """Exibe gráficos de consumo de água."""
    if df.empty:
        enhanced_empty_state(
            title="Nenhum Dado de Água",
            description="Não há dados de consumo de água para exibir gráficos.",
            icon="💧"
        )
        return

    if "consumption" in df.columns and "date_display" in df.columns:
        st.markdown("### 📈 Consumo de Água ao Longo do Tempo")
        fig1 = px.line(
            df,
            x="date_display",
            y="consumption",
            labels={"consumption": "Consumo (L)", "date_display": "Data"},
            title="Consumo de Água ao Longo do Tempo",
            markers=True,
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

        if len(df) > 1:
            st.markdown("### 📊 Distribuição do Consumo de Água")
            fig2 = px.bar(
                df,
                x="date_display",
                y="consumption",
                labels={"consumption": "Consumo (L)", "date_display": "Data"},
                title="Distribuição do Consumo de Água por Período",
            )
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)


def display_consumption_analysis(df, consumption_type="Energia"):
    """Exibe análise estatística de consumo conforme swagger."""
    if df.empty:
        return

    icon = "⚡" if consumption_type == "Energia" else "💧"
    
    if consumption_type == "Energia":
        if "total_power" in df.columns:
            total_consumption = df["total_power"].sum()
            avg_consumption = df["total_power"].mean()
            max_consumption = df["total_power"].max()
            min_consumption = df["total_power"].min()
            unit = "kWh"
        else:
            return
            
        # Análise adicional de custos para energia
        cost_content = ""
        if "totalCost" in df.columns:
            total_cost = df["totalCost"].sum()
            avg_cost = df["totalCost"].mean()
            cost_content = f"""
- **Custo Total:** R$ {total_cost:.2f}
- **Custo Médio:** R$ {avg_cost:.2f}"""
        
        ComponentLibrary.card(
            title=f"{icon} Análise de Consumo de {consumption_type}",
            content=f"""- **Consumo Total:** {total_consumption:.2f} {unit}
- **Consumo Médio:** {avg_consumption:.2f} {unit}
- **Consumo Máximo:** {max_consumption:.2f} {unit}
- **Consumo Mínimo:** {min_consumption:.2f} {unit}{cost_content}""",
            color="info"
        )
    else:  # Água
        if "consumption" not in df.columns:
            return
            
        total_consumption = df["consumption"].sum()
        avg_consumption = df["consumption"].mean()
        max_consumption = df["consumption"].max()
        min_consumption = df["consumption"].min()
        unit = "L"
        
        ComponentLibrary.card(
            title=f"{icon} Análise de Consumo de {consumption_type}",
            content=f"""- **Consumo Total:** {total_consumption:.2f} {unit}
- **Consumo Médio:** {avg_consumption:.2f} {unit}
- **Consumo Máximo:** {max_consumption:.2f} {unit}
- **Consumo Mínimo:** {min_consumption:.2f} {unit}""",
            color="info"
        )


def display_cost_analysis_detailed(df):
    """Análise detalhada de custos para energia (complementar à análise genérica)."""
    if df.empty or "consumption" not in df.columns or "custo" not in df.columns:
        return

    total_consumption = df["consumption"].sum()
    total_cost = df["custo"].sum()
    avg_consumption = df["consumption"].mean()
    avg_cost = df["custo"].mean()
    
    # Análise por período se disponível
    periodo_analysis = ""
    if "periodo" in df.columns:
        periodo_stats = df.groupby("periodo").agg({
            "consumption": ["sum", "mean"],
            "custo": ["sum", "mean"]
        }).round(2)
        
        if len(periodo_stats) > 0:
            periodo_analysis = "\n\n**Análise por Período:**\n"
            for periodo in periodo_stats.index:
                cons_total = periodo_stats.loc[periodo, ("consumption", "sum")]
                cost_total = periodo_stats.loc[periodo, ("custo", "sum")]
                periodo_analysis += f"- **{periodo}:** {cons_total:.2f} kWh → R$ {cost_total:.2f}\n"

    ComponentLibrary.card(
        title="📊 Análise Detalhada de Custos",
        content=f"""**Resumo Geral:**
- **Consumo Total:** {total_consumption:.2f} kWh
- **Custo Total:** R$ {total_cost:.2f}
- **Consumo Médio:** {avg_consumption:.2f} kWh por registro
- **Custo Médio:** R$ {avg_cost:.2f} por registro
- **Custo por kWh:** R$ {(total_cost/total_consumption if total_consumption > 0 else 0):.4f}{periodo_analysis}""",
        color="success"
    )


# ============================================================================
# TAB DE CONSUMO DE ENERGIA
# ============================================================================

def show_energy_tab():
    """Tab de consumo de energia."""
    token = st.session_state.get("token")
    
    st.markdown("#### 🔍 Consulta de Consumo de Energia")
    
    # Seletor de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador (Opcional)", 
        include_all_option=True, context="energy_consumption"
    )

    # Filtros conforme swagger
    with st.expander("📅 Filtros de Consulta", expanded=True):
        st.markdown("**Configure os parâmetros para consulta do consumo de energia**")
        
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Período de Agregação (Opcional)",
                ["", "daily", "monthly", "yearly"],
                help="Período de agregação dos dados conforme API",
                key="energy_period_selector"
            )
        with col2:
            st.write(" ")  # Espaçamento

    # Botão de consulta
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚡ Buscar Consumo de Energia", type="primary", use_container_width=True, key="energy_search_button"):
            # Preparar parâmetros conforme swagger
            period_param = period if period else None

            # Buscar dados
            with LoadingStates.progress_with_status("Buscando consumo de energia...", 100) as (progress, status, container):
                progress.progress(50)
                status.text("Consultando base de dados...")
                
                df_energy = fetch_energy_consumption(
                    token=token,
                    controller_id=controller_id,
                    period=period_param
                )
                
                progress.progress(100)
                status.text("Processando resultados...")

            if not df_energy.empty:
                ComponentLibrary.alert("Consulta de energia realizada com sucesso!", "success")
                
                # Buscar tarifas para processamento
                with LoadingStates.spinner_with_cancel("Carregando tarifas..."):
                    tariffs = fetch_current_tariffs(token)
                
                # Processar dados para compatibilidade com análises detalhadas
                df_processed = process_energy_consumption(df_energy, tariffs)
                
                # Card informativo
                controller_info = f"**Controlador:** {controller_name}" if controller_id else "**Controlador:** Todos"
                period_info = f"**Agregação:** {period}" if period else "**Agregação:** Padrão"
                ComponentLibrary.card(
                    title="⚡ Dados de Energia Carregados",
                    content=f"""{controller_info}
- {period_info}
- **Registros:** {len(df_energy)} medições""",
                    icon="⚡",
                    color="success"
                )

                # Dados tabulares
                st.markdown("#### 📋 Dados Tabulares")
                # Mostrar colunas relevantes conforme swagger
                display_columns = []
                if "date_display" in df_energy.columns:
                    display_columns.append("date_display")
                if "total_power" in df_energy.columns:
                    display_columns.append("total_power")
                if "daytimePower" in df_energy.columns:
                    display_columns.extend(["daytimePower", "nighttimePower"])
                if "totalCost" in df_energy.columns:
                    display_columns.extend(["daytimeCost", "nighttimeCost", "totalCost"])
                
                if display_columns:
                    st.dataframe(df_energy[display_columns], use_container_width=True, key="energy_dataframe")
                else:
                    st.dataframe(df_energy, use_container_width=True, key="energy_dataframe")

                # Gráficos
                display_energy_graphs(df_energy)
                
                # Análise estatística básica
                display_consumption_analysis(df_energy, "Energia")
                
                # Análise detalhada de custos (se dados processados estão disponíveis)
                if "custo" in df_processed.columns and "consumption" in df_processed.columns:
                    display_cost_analysis_detailed(df_processed)
                
                # Exibir tarifas vigentes se conseguiu buscar dados
                with LoadingStates.spinner_with_cancel("Carregando tarifas vigentes..."):
                    tariffs = fetch_current_tariffs(token)
                
                if tariffs:
                    st.markdown("---")
                    st.markdown("### 💰 Tarifas Vigentes")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        ComponentLibrary.metric_card(
                            title="Tarifa Diurna",
                            value=f"R$ {tariffs.get('daytimeTariff', 0):.4f}/kWh",
                            icon="☀️"
                        )
                    
                    with col2:
                        ComponentLibrary.metric_card(
                            title="Tarifa Noturna", 
                            value=f"R$ {tariffs.get('nighttimeTariff', 0):.4f}/kWh",
                            icon="🌙"
                        )
                    
                    with col3:
                        discount = tariffs.get("nighttimeDiscount", 0)
                        ComponentLibrary.metric_card(
                            title="Desconto Noturno",
                            value=f"{discount:.1f}%" if discount > 0 else "N/A",
                            icon="💸"
                        )
            else:
                ComponentLibrary.alert("Nenhum dado de energia encontrado para os filtros selecionados.", "info")
    
    # Seção de simulação de custos
    st.markdown("---")
    st.markdown("### 🔮 Simulação de Custos Futuros")
    
    # Manter expander aberto se formulário foi submetido
    expanded_state = st.session_state.get("energy_simulation_expanded", False)
    
    with st.expander("💡 Simular Consumo Projetado", expanded=expanded_state):
        st.markdown("**Calcule custos estimados baseados nas tarifas vigentes**")
        
        with st.form("SimularCustosEnergia"):
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
                # Manter expander aberto após submissão
                st.session_state["energy_simulation_expanded"] = True
                
                with LoadingStates.spinner_with_cancel("Calculando simulação..."):
                    tariffs = fetch_current_tariffs(token)
                
                if tariffs and "daytimeTariff" in tariffs:
                    simulate_future_costs(
                        tariffs,
                        projected_consumption_diurno,
                        projected_consumption_noturno
                    )
                else:
                    ComponentLibrary.alert(
                        "Não é possível simular custos sem tarifas vigentes. Configure as tarifas primeiro.",
                        "error"
                    )


# ============================================================================
# TAB DE CONSUMO DE ÁGUA
# ============================================================================

def show_water_tab():
    """Tab de consumo de água."""
    token = st.session_state.get("token")
    
    st.markdown("#### 🔍 Consulta de Consumo de Água")
    
    # Seletor de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador (Opcional)", 
        include_all_option=True, context="water_consumption"
    )

    # Filtros conforme swagger
    with st.expander("📅 Filtros de Consulta", expanded=True):
        st.markdown("**Configure os parâmetros para consulta do consumo de água**")
        
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Período de Agregação (Opcional)",
                ["", "daily", "monthly", "yearly"],
                help="Período de agregação dos dados conforme API",
                key="water_period_selector"
            )
        
        with col2:
            st.write(" ")  # Espaçamento

    # Botão de consulta
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💧 Buscar Consumo de Água", type="primary", use_container_width=True, key="water_search_button"):
            # Preparar parâmetros conforme swagger
            period_param = period if period else None

            # Buscar dados
            with LoadingStates.progress_with_status("Buscando consumo de água...", 100) as (progress, status, container):
                progress.progress(50)
                status.text("Consultando base de dados...")
                
                df_water = fetch_water_consumption(
                    token=token,
                    controller_id=controller_id,
                    period=period_param
                )
                
                progress.progress(100)
                status.text("Processando resultados...")

            if not df_water.empty:
                ComponentLibrary.alert("Consulta de água realizada com sucesso!", "success")
                
                # Card informativo
                controller_info = f"**Controlador:** {controller_name}" if controller_id else "**Controlador:** Todos"
                period_info = f"**Agregação:** {period}" if period else "**Agregação:** Padrão"
                ComponentLibrary.card(
                    title="💧 Dados de Água Carregados",
                    content=f"""{controller_info}
- {period_info}
- **Registros:** {len(df_water)} medições""",
                    icon="💧",
                    color="success"
                )

                # Dados tabulares
                st.markdown("#### 📋 Dados Tabulares")
                display_columns = ["date_display", "consumption"] if "date_display" in df_water.columns else df_water.columns
                st.dataframe(df_water[display_columns], use_container_width=True, key="water_dataframe")

                # Gráficos
                display_water_graphs(df_water)
                
                # Análise
                display_consumption_analysis(df_water, "Água")
            else:
                ComponentLibrary.alert("Nenhum dado de água encontrado para os filtros selecionados.", "info")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def show():
    """Tela principal de consumos unificada."""
    st.title("📊 Consumos - Energia e Água")

    token = st.session_state.get("token")
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return

    # Metric cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ComponentLibrary.metric_card(
            title="Tipos de Consumo",
            value="2",
            icon="📊"
        )
    
    with col2:
        ComponentLibrary.metric_card(
            title="Período Máximo",
            value="90 dias",
            icon="📅"
        )
    
    with col3:
        ComponentLibrary.metric_card(
            title="Status do Sistema",
            value="Operacional",
            icon="✅"
        )
    
    st.markdown("---")

    # Aviso sobre disponibilidade dos endpoints
    ComponentLibrary.alert(
        "ℹ️ **Nota**: Os endpoints de consumo (/api/consumptions/energy e /api/consumptions/water) "
        "estão definidos no Swagger mas podem não estar implementados na API atual. "
        "Se você receber erro 404, significa que os endpoints ainda não foram desenvolvidos no backend.",
        "info"
    )

    # Tabs para energia e água
    tab1, tab2 = st.tabs(["⚡ Energia", "💧 Água"])
    
    with tab1:
        show_energy_tab()
    
    with tab2:
        show_water_tab()


if __name__ == "__main__":
    show()