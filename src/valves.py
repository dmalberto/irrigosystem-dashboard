import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    cast_to_int32,
    cast_to_int64,
    controller_selector,
    handle_api_response_v2,
    invalidate_caches_after_mutation,
    valve_selector,
)
from src.controllers import get_controllers  # para reusar a lógica


def rename_valve_columns(df: pd.DataFrame):
    """Renomeia colunas de Válvulas para português."""
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "controllerId": "ID do Controlador",
            "flowRate": "Taxa de Fluxo (L/min)",
        }
        df.rename(columns=columns_mapping, inplace=True)


def get_valves(token, controller_id):
    """GET /api/controllers/{controllerId}/valves"""
    endpoint = f"/api/controllers/{controller_id}/valves"
    resp = api_request("GET", endpoint, token=token)
    if resp and resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            return data
    st.error("Falha ao obter válvulas do controlador.")
    return []


def create_valve(token, controller_id, valve_id, flow_rate):
    """POST /api/controllers/{controllerId}/valves

    Campos obrigatórios conforme Swagger: id (int32), flowRate (double)
    controllerId é int64 no path
    """
    endpoint = f"/api/controllers/{controller_id}/valves"
    body = {
        "id": valve_id,  # required field conforme Swagger
        "flowRate": flow_rate,
        "controllerId": controller_id,  # incluir por consistência
    }
    resp = api_request("POST", endpoint, token=token, json=body)
    return resp


def update_valve(token, controller_id, valve_id, flow_rate):
    """PUT /api/controllers/{controllerId}/valves/{id}

    Campos obrigatórios conforme Swagger: id (int32), flowRate (double)
    Path params: controllerId (int64), id (int32)
    """
    endpoint = f"/api/controllers/{controller_id}/valves/{valve_id}"
    body = {
        "id": valve_id,  # required field conforme Swagger
        "flowRate": flow_rate,
        "controllerId": controller_id,  # incluir por consistência
    }
    resp = api_request("PUT", endpoint, token=token, json=body)
    return resp


def delete_valve(token, controller_id, valve_id):
    endpoint = f"/api/controllers/{controller_id}/valves/{valve_id}"
    resp = api_request("DELETE", endpoint, token=token)
    return resp


def show_list_valves(token):
    """Listar válvulas de um controlador escolhido."""
    st.markdown("### 📋 Válvulas por Controlador")

    # Usar seletor padronizado
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *", context="list_valves"
    )

    if not controller_id:
        enhanced_empty_state(
            title="Selecione um Controlador",
            description="Escolha um controlador acima para visualizar suas válvulas.",
            icon="⚙️",
        )
        return

    if st.button("🔄 Carregar Válvulas", type="primary"):
        with LoadingStates.spinner_with_cancel("Buscando válvulas..."):
            data = get_valves(token, controller_id)

        if data:
            df = pd.DataFrame(data)
            rename_valve_columns(df)

            # Card informativo
            ComponentLibrary.card(
                title=f"Válvulas do Controlador: {controller_name}",
                content=f"Encontradas {len(data)} válvulas neste controlador.",
                color="info",
            )

            if "ID" in df.columns:
                df.set_index("ID", inplace=True)

            st.dataframe(df, use_container_width=True)
        else:
            enhanced_empty_state(
                title="Nenhuma Válvula Encontrada",
                description=f"O controlador {controller_name} não possui válvulas cadastradas.",
                icon="💧",
                action_button={
                    "label": "➕ Cadastrar Primeira Válvula",
                    "key": "create_first_valve",
                },
            )


def show_create_valve(token):
    st.markdown("### ➕ Cadastrar Nova Válvula")

    # Usar seletor padronizado
    controller_id, controller_name = controller_selector(
        token, "Controlador de Destino *", context="create_valve"
    )

    if not controller_id:
        ComponentLibrary.alert(
            "Selecione um controlador para associar a nova válvula.", "warning"
        )
        return

    with st.form("FormCriarValvula"):
        st.info(f"**Controlador selecionado:** {controller_name}")

        valve_id = st.number_input(
            "ID da Válvula *",
            min_value=1,
            step=1,
            value=1,
            help="ID único da válvula (int32 conforme swagger)",
        )

        flow_rate = st.number_input(
            "Taxa de Fluxo (L/min) *",
            min_value=0.0,
            step=0.1,
            value=10.0,
            help="Taxa de fluxo em litros por minuto (double conforme swagger)",
        )

        submitted = st.form_submit_button("✅ Cadastrar Válvula")

        if submitted:
            # Validações
            if valve_id <= 0:
                ComponentLibrary.alert(
                    "ID da válvula deve ser maior que zero.", "error"
                )
                return

            if flow_rate < 0:
                ComponentLibrary.alert(
                    "Taxa de fluxo deve ser um valor positivo.", "error"
                )
                return

            # Casting conforme swagger
            controller_id_cast = cast_to_int64(controller_id)
            valve_id_cast = cast_to_int32(valve_id)

            resp = create_valve(token, controller_id_cast, valve_id_cast, flow_rate)
            if handle_api_response_v2(resp, "Válvula criada com sucesso!"):
                invalidate_caches_after_mutation("valves")
                st.rerun()


def show_edit_valve(token):
    st.markdown("### ✏️ Editar Válvula Existente")

    # Usar seletor padronizado de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *", context="edit_valve"
    )

    if not controller_id:
        return

    # Usar seletor dependente de válvulas
    valve_id, valve_name = valve_selector(
        token, controller_id, "Selecione a Válvula para Editar *", context="edit"
    )

    if not valve_id:
        return

    # Buscar dados atuais da válvula
    with LoadingStates.spinner_with_cancel("Carregando dados da válvula..."):
        valves_data = get_valves(token, controller_id)

    valve_info = next(
        (v for v in valves_data if cast_to_int32(v["id"]) == valve_id), None
    )

    if not valve_info:
        ComponentLibrary.alert("Válvula não encontrada.", "error")
        return

    # Card com informações atuais
    ComponentLibrary.card(
        title="Válvula Selecionada",
        content=f"""- **Controlador**: {controller_name}
- **ID da Válvula**: {valve_id}
- **Vazão Atual**: {valve_info.get('flowRate', 0):.1f} L/min
""",
        color="info",
    )

    with st.form("FormEditarValvula"):
        new_flow = st.number_input(
            "Nova Taxa de Fluxo (L/min) *",
            value=float(valve_info.get("flowRate", 0)),
            min_value=0.0,
            step=0.1,
            help="Nova taxa de fluxo em litros por minuto",
        )

        submitted = st.form_submit_button("💾 Atualizar Válvula")

        if submitted:
            if new_flow < 0:
                ComponentLibrary.alert(
                    "Taxa de fluxo deve ser um valor positivo.", "error"
                )
                return

            # Casting conforme swagger
            controller_id_cast = cast_to_int64(controller_id)
            valve_id_cast = cast_to_int32(valve_id)

            resp = update_valve(token, controller_id_cast, valve_id_cast, new_flow)
            if handle_api_response_v2(resp, "Válvula atualizada com sucesso!"):
                invalidate_caches_after_mutation("valves")
                st.rerun()


def show_delete_valve(token):
    st.markdown("### Excluir Válvula")

    # Usar seletor padronizado de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *", context="delete_valve"
    )

    if not controller_id:
        return

    # Usar seletor dependente de válvulas
    valve_id, valve_name = valve_selector(
        token, controller_id, "Selecione a Válvula para Excluir *", context="delete"
    )

    if not valve_id:
        return

    # Mostrar informações da válvula
    valves_data = get_valves(token, controller_id)
    valve_info = next(
        (v for v in valves_data if cast_to_int32(v["id"]) == valve_id), None
    )

    if valve_info:
        st.warning("⚠️ **ATENÇÃO**: Você está prestes a excluir a válvula:")
        st.info(
            f"""- **Controlador**: {controller_name}
- **ID da Válvula**: {valve_id}
- **Vazão**: {valve_info.get('flowRate', 0):.1f} L/min"""
        )

        if st.button("🗑️ Confirmar Exclusão", type="primary"):
            resp = delete_valve(token, controller_id, valve_id)
            if handle_api_response_v2(resp, "Válvula excluída com sucesso!"):
                invalidate_caches_after_mutation("valves")
                st.rerun()


def show():
    st.title("💧 Gerenciamento de Válvulas")

    token = st.session_state.get("token")
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return

    # Cards de informações com layout moderno
    controllers_data = get_controllers(token)

    # Exibir resumo se há controladores
    if controllers_data:
        col1, col2, col3 = st.columns(3)

        with col1:
            ComponentLibrary.metric_card(
                title="Controladores", value=str(len(controllers_data)), icon="⚙️"
            )

        with col2:
            # Contar total de válvulas (simulado)
            total_valves = len(controllers_data) * 2  # Estimativa
            ComponentLibrary.metric_card(
                title="Válvulas Estimadas", value=str(total_valves), icon="💧"
            )

        with col3:
            ComponentLibrary.metric_card(title="Status", value="Operacional", icon="✅")

        st.markdown("---")

    # Tabs modernizadas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "➕ Criar", "✏️ Editar", "🗑️ Excluir"])

    with tab1:
        show_list_valves(token)
    with tab2:
        show_create_valve(token)
    with tab3:
        show_edit_valve(token)
    with tab4:
        show_delete_valve(token)
