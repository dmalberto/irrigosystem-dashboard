from datetime import date, datetime, time, timedelta

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    controller_selector,
    format_datetime_for_api
)


def format_datetime(date_value, time_value):
    """Converte (date, time) do Streamlit em string ISO8601, ex: '2025-01-08T07:31:20'."""
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.isoformat()
    return None


def display_datetime(date_value, time_value):
    """Formata data e hora para exibição (DD/MM/YYYY HH:MM:SS)."""
    if date_value:
        if time_value:
            return datetime.combine(date_value, time_value).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        return datetime.combine(date_value, time.min).strftime("%d/%m/%Y %H:%M:%S")
    return "Não especificado"


def fetch_controllers(token):
    """
    GET /api/controllers: retorna lista de controladores
    Ex.: [{"id":2, "pumpPower":..., ...}, ...]
    """
    endpoint = "/api/controllers"
    response = api_request("GET", endpoint, token=token)
    if not response or response.status_code != 200:
        st.error("Falha ao obter lista de controladores.")
        return []
    return response.json() if isinstance(response.json(), list) else []


def fetch_statuses(token, controller_id, page=1, start_date=None, end_date=None):
    """
    GET /api/controllers/{controllerId}/statuses
    Parametros fixos de paginação: pageSize=15, sort=desc
    Recebe 'page' e datas para filtrar
    """
    endpoint = f"/api/controllers/{controller_id}/statuses"
    params = {"page": page, "pageSize": 15, "sort": "desc"}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    response = api_request("GET", endpoint, token=token, params=params)
    return response


def fetch_activations(token, controller_id, period=None):
    """
    GET /api/controllers/{controllerId}/activations
    Parâmetros conforme Swagger:
    - controllerId (int64): ID do controlador
    - period (string, opcional): Período de agregação
    
    Retorna: Array de PumpStatus
    """
    endpoint = f"/api/controllers/{controller_id}/activations"
    params = {}
    if period:
        params["period"] = period

    response = api_request("GET", endpoint, token=token, params=params)
    return response


def load_more_statuses():
    """
    Incrementa a página e faz nova requisição, concatenando
    os dados em st.session_state.act_data
    """
    st.session_state.act_page += 1

    resp = fetch_statuses(
        token=st.session_state["token"],
        controller_id=st.session_state["act_controller_id"],
        page=st.session_state["act_page"],
        start_date=st.session_state.get("act_start_date_str"),
        end_date=st.session_state.get("act_end_date_str"),
    )
    if resp and resp.status_code == 200:
        df_new = pd.DataFrame(resp.json())
        if not df_new.empty:
            st.session_state.act_data = pd.concat(
                [st.session_state.act_data, df_new], ignore_index=True
            )
            ComponentLibrary.alert(f"Carregados mais {len(df_new)} registros!", "success")
        else:
            ComponentLibrary.alert("Não há mais dados para carregar.", "info")
    else:
        ComponentLibrary.alert("Não foi possível carregar mais dados. Tente novamente.", "error")


def show():
    st.title("🔋 Ativações de Bomba")
    
    # Tabs para separar Statuses e Activations conforme Swagger
    tab1, tab2 = st.tabs(["📊 Status Histórico", "⚡ Ativações"])
    
    with tab1:
        show_statuses_tab()
        
    with tab2:
        show_activations_tab()


def show_statuses_tab():

    token = st.session_state.get("token", None)
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return

    # Carregar informações dos controladores
    controllers_data = fetch_controllers(token)
    
    # Exibir cards de resumo se há controladores
    if controllers_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ComponentLibrary.metric_card(
                title="Controladores Disponíveis",
                value=str(len(controllers_data)),
                icon="⚙️"
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

    # -----------------------------------------------------------------
    # Inicializa variáveis de estado, caso não existam
    # -----------------------------------------------------------------
    if "act_page" not in st.session_state:
        st.session_state.act_page = 1

    if "act_data" not in st.session_state:
        st.session_state.act_data = pd.DataFrame()

    if "act_controller_id" not in st.session_state:
        st.session_state.act_controller_id = None

    if "act_previous_controller_id" not in st.session_state:
        st.session_state.act_previous_controller_id = None

    if "act_start_date_str" not in st.session_state:
        st.session_state.act_start_date_str = None

    if "act_end_date_str" not in st.session_state:
        st.session_state.act_end_date_str = None

    # -----------------------------------------------------------------
    # Seleção de controlador e filtros em seções organizadas
    # -----------------------------------------------------------------
    st.markdown("### 🔍 Consulta de Ativações")
    
    # Seletor padronizado de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *", context="controller_activations"
    )
    if not controller_id:
        enhanced_empty_state(
            title="Selecione um Controlador",
            description="Escolha um controlador acima para visualizar suas ativações de bomba.",
            icon="⚙️"
        )
        return

    # Se o controlador mudou, resetar paginação/dados
    if controller_id != st.session_state.act_previous_controller_id:
        st.session_state.act_page = 1
        st.session_state.act_data = pd.DataFrame()
        st.session_state.act_controller_id = controller_id
        st.session_state.act_previous_controller_id = controller_id

    # Card informativo do controlador selecionado
    ComponentLibrary.card(
        title="Controlador Selecionado",
        content=f"Consultando ativações de bomba para: **{controller_name}**",
        icon="⚙️",
        color="info"
    )

    # -----------------------------------------------------------------
    # Filtros organizados em expander
    # -----------------------------------------------------------------
    with st.expander("📅 Filtros de Período", expanded=True):
        st.markdown("**Configure o período para consulta das ativações (máximo 90 dias)**")
        
        end_date_default = date.today()
        start_date_default = end_date_default - timedelta(days=7)  # Default 7 dias

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data de Início *",
                value=start_date_default,
                help="Data inicial do período (máx 90 dias)",
            )
        with col2:
            end_date = st.date_input(
                "Data de Fim *", value=end_date_default, help="Data final do período"
            )

        # Checkbox para filtrar horário
        filtrar_por_horario = st.checkbox("🕐 Filtrar por horário específico", value=False)

        if filtrar_por_horario:
            col3, col4 = st.columns(2)
            with col3:
                start_time = st.time_input("Hora de Início", value=time(0, 0, 0))
            with col4:
                end_time = st.time_input("Hora de Fim", value=time(23, 59, 59))
        else:
            start_time = time(0, 0, 0)
            end_time = time(23, 59, 59)

    # Botão de consulta centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Buscar Ativações", type="primary", use_container_width=True):
            # Validações
            if start_date > end_date:
                ComponentLibrary.alert("Data de início deve ser anterior à data de fim.", "error")
                return

            # Validar período máximo de 90 dias
            if (end_date - start_date).days > 90:
                ComponentLibrary.alert("Período máximo permitido é de 90 dias.", "error")
                return

            start_date_str = format_datetime_for_api(start_date, start_time)
            end_date_str = format_datetime_for_api(end_date, end_time)

            # Salva no session_state
            st.session_state.act_start_date_str = start_date_str
            st.session_state.act_end_date_str = end_date_str

            # Resetar paginação e dados
            st.session_state.act_page = 1
            st.session_state.act_data = pd.DataFrame()

            # Faz a primeira busca com loading melhorado
            with LoadingStates.progress_with_status("Buscando ativações...", 100) as (progress, status, container):
                progress.progress(30)
                status.text("Preparando consulta...")
                
                progress.progress(70)
                status.text("Consultando base de dados...")
                
                resp = fetch_statuses(
                    token,
                    controller_id,
                    st.session_state.act_page,
                    start_date_str,
                    end_date_str,
                )
                
                progress.progress(100)
                status.text("Processando resultados...")

            if resp and resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                st.session_state.act_data = df
                ComponentLibrary.alert("Consulta realizada com sucesso!", "success")
            else:
                ComponentLibrary.alert(
                    "Nenhum resultado encontrado para os filtros informados.",
                    "info"
                )

    # -----------------------------------------------------------------
    # Se temos act_data vazio e nenhuma requisição feita, busca inicial
    # -----------------------------------------------------------------
    if st.session_state.act_page == 1 and st.session_state.act_data.empty:
        # Carregamos sem filtros customizados, usando start_date/end_date default
        if start_date > end_date:
            ComponentLibrary.alert("Data de início deve ser anterior à data de fim.", "error")
            return
            
        st.session_state.act_start_date_str = format_datetime(start_date, start_time)
        st.session_state.act_end_date_str = format_datetime(end_date, end_time)

        with LoadingStates.spinner_with_cancel("Carregando dados iniciais..."):
            resp = fetch_statuses(
                token,
                controller_id,
                st.session_state.act_page,
                st.session_state.act_start_date_str,
                st.session_state.act_end_date_str,
            )
            
        if resp and resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            st.session_state.act_data = df
        else:
            ComponentLibrary.alert("Nenhum dado disponível ou falha na requisição.", "warning")

    # -----------------------------------------------------------------
    # Exibição da tabela e botão "Carregar mais"
    # -----------------------------------------------------------------
    if not st.session_state.act_data.empty:
        st.markdown("### 📊 Resultados da Consulta")
        
        # Card com informações do período
        start_disp = display_datetime(start_date, start_time)
        end_disp = display_datetime(end_date, end_time)
        
        ComponentLibrary.card(
            title="Dados Carregados",
            content=f"""- **Controlador**: {controller_name}
- **Período**: {start_disp} até {end_disp}
- **Registros**: {len(st.session_state.act_data)} ativações""",
            icon="📊",
            color="success"
        )

        # Tabela com dados
        st.dataframe(st.session_state.act_data, use_container_width=True)

        # Botão carregar mais com estilo moderno
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Carregar Mais Dados", type="secondary", use_container_width=True):
                with LoadingStates.spinner_with_cancel("Carregando mais ativações..."):
                    load_more_statuses()
                st.rerun()

    else:
        enhanced_empty_state(
            title="Nenhuma Ativação Encontrada",
            description="Não há ativações de bomba para o período e controlador selecionados. Tente ajustar os filtros ou selecionar outro controlador.",
            icon="🔋",
            action_button={
                "label": "🔄 Recarregar Dados",
                "key": "reload_activations"
            }
        )


def show_activations_tab():
    """Tab para mostrar ativações de bomba conforme endpoint /api/controllers/{controllerId}/activations"""
    
    token = st.session_state.get("token", None)
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return

    st.markdown("#### ⚡ Ativações de Bomba")
    st.markdown("Consulte as ativações de bomba por controlador usando diferentes períodos de agregação.")

    # Seletor de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *", context="activations"
    )

    if not controller_id:
        ComponentLibrary.alert("Selecione um controlador para consultar as ativações.", "info")
        return

    # Filtros conforme Swagger
    with st.expander("🔍 Filtros de Consulta", expanded=True):
        st.markdown("**Configure os parâmetros para consulta das ativações**")
        
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Período de Agregação (Opcional)",
                ["", "daily", "weekly", "monthly", "yearly"],
                help="Período de agregação das ativações conforme API",
                key="activations_period_selector"
            )
        with col2:
            st.write(" ")  # Espaçamento

    # Botão de consulta
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚡ Buscar Ativações", type="primary", use_container_width=True, key="activations_search_button"):
            # Preparar parâmetros conforme Swagger
            period_param = period if period else None

            # Buscar dados
            with LoadingStates.spinner_with_cancel("Buscando ativações de bomba..."):
                response = fetch_activations(
                    token=token,
                    controller_id=controller_id,
                    period=period_param
                )

            if response and response.status_code == 200:
                activations_data = response.json()
                
                if activations_data:
                    ComponentLibrary.alert("Consulta de ativações realizada com sucesso!", "success")
                    
                    # Card informativo
                    period_info = f"**Período:** {period}" if period else "**Período:** Todos os dados"
                    ComponentLibrary.card(
                        title="⚡ Dados de Ativações Carregados",
                        content=f"""- **Controlador:** {controller_name}
- {period_info}
- **Registros:** {len(activations_data)} ativações""",
                        icon="⚡",
                        color="success"
                    )

                    # Processar dados para DataFrame
                    df_activations = pd.DataFrame(activations_data)
                    
                    # Formatear datas para exibição se existirem
                    if "startDate" in df_activations.columns:
                        df_activations["startDate_display"] = pd.to_datetime(df_activations["startDate"]).dt.strftime("%d/%m/%Y %H:%M:%S")
                    if "endDate" in df_activations.columns:
                        df_activations["endDate_display"] = pd.to_datetime(df_activations["endDate"]).dt.strftime("%d/%m/%Y %H:%M:%S")

                    # Métricas de resumo
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_activations = len(df_activations)
                        ComponentLibrary.metric_card(
                            title="Total de Ativações",
                            value=str(total_activations),
                            icon="🔢"
                        )
                    
                    with col2:
                        if "duration" in df_activations.columns:
                            avg_duration = df_activations["duration"].mean()
                            ComponentLibrary.metric_card(
                                title="Duração Média",
                                value=f"{avg_duration:.1f}h",
                                icon="⏱️"
                            )
                        else:
                            ComponentLibrary.metric_card(
                                title="Duração",
                                value="N/A",
                                icon="⏱️"
                            )
                    
                    with col3:
                        active_pumps = len(df_activations[df_activations.get("status", 0) == 1]) if "status" in df_activations.columns else 0
                        ComponentLibrary.metric_card(
                            title="Bombas Ativas",
                            value=str(active_pumps),
                            icon="🟢"
                        )
                    
                    with col4:
                        if "duration" in df_activations.columns:
                            total_hours = df_activations["duration"].sum()
                            ComponentLibrary.metric_card(
                                title="Total de Horas",
                                value=f"{total_hours:.1f}h",
                                icon="🕐"
                            )
                        else:
                            ComponentLibrary.metric_card(
                                title="Total Horas",
                                value="N/A",
                                icon="🕐"
                            )

                    # Dados tabulares
                    st.markdown("---")
                    st.markdown("#### 📋 Dados Tabulares")
                    
                    # Mostrar colunas relevantes para ativações conforme schema PumpStatus
                    display_columns = []
                    if "startDate_display" in df_activations.columns:
                        display_columns.append("startDate_display")
                    if "endDate_display" in df_activations.columns:
                        display_columns.append("endDate_display")
                    if "status" in df_activations.columns:
                        display_columns.append("status")
                    if "duration" in df_activations.columns:
                        display_columns.append("duration")
                    
                    if display_columns:
                        st.dataframe(df_activations[display_columns], use_container_width=True, key="activations_dataframe")
                    else:
                        st.dataframe(df_activations, use_container_width=True, key="activations_dataframe")

                else:
                    enhanced_empty_state(
                        title="Nenhuma Ativação Encontrada",
                        description="Não há ativações de bomba para o controlador e período selecionados.",
                        icon="⚡"
                    )
                    
            elif response and response.status_code == 404:
                ComponentLibrary.alert("Controlador não encontrado ou sem dados de ativações.", "warning")
            else:
                error_msg = "Erro ao buscar ativações de bomba."
                if response:
                    error_msg += f" Status: {response.status_code}"
                ComponentLibrary.alert(error_msg, "error")


if __name__ == "__main__":
    show()
