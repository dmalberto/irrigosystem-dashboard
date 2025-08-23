import pandas as pd
import streamlit as st

from api import api_request
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
    st.subheader("Listar Válvulas")

    # Buscar controladores existentes
    controllers_data = get_controllers(token)
    if not controllers_data:
        st.warning("Nenhum controlador disponível para selecionar.")
        return

    # Criar opções com nome + ID visível
    controller_options = {
        f"{controller['name']} (ID: {controller['id']})": controller["id"]
        for controller in controllers_data
    }

    if not controller_options:
        st.warning("Nenhum controlador encontrado.")
        return

    controller_choice = st.selectbox(
        "Selecione o Controlador", controller_options.keys()
    )
    controller_id = controller_options[controller_choice]

    if st.button("Carregar Válvulas"):
        data = get_valves(token, controller_id)
        if data:
            df = pd.DataFrame(data)
            rename_valve_columns(df)
            if "ID" in df.columns:
                df.set_index("ID", inplace=True)
            # Tabela sem rolagem (ou mínima) -> use_container_width
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhuma válvula cadastrada ou falha ao obter.")


def show_create_valve(token):
    st.subheader("Criar Válvula")

    # Buscar controladores
    controllers_data = get_controllers(token)
    if not controllers_data:
        st.warning("Não há controladores para associar a uma válvula.")
        return

    # Criar opções com nome + ID visível
    controller_options = {
        f"{controller['name']} (ID: {controller['id']})": controller["id"]
        for controller in controllers_data
    }

    with st.form("FormCriarValvula"):
        controller_choice = st.selectbox(
            "Selecione o Controlador", controller_options.keys()
        )
        selected_controller = controller_options[controller_choice]
        valve_id = st.number_input(
            "ID da Válvula", min_value=1, step=1, help="ID único da válvula (int32)"
        )
        flow_rate = st.number_input("Taxa de Fluxo (L/min)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Criar Válvula")
        if submitted:
            resp = create_valve(token, selected_controller, valve_id, flow_rate)
            if resp and resp.status_code == 200:
                st.success("Válvula criada com sucesso!")
                st.rerun()
            elif resp and resp.status_code == 400:
                st.error("Requisição inválida - verifique os dados informados.")
            elif resp and resp.status_code == 409:
                st.error("Conflito - válvula com este ID já existe.")
            elif resp and resp.status_code == 500:
                st.error("Erro interno do servidor.")
            else:
                st.error("Falha ao criar válvula.")


def show_edit_valve(token):
    st.subheader("Editar Válvula Existente")

    controllers_data = get_controllers(token)
    if not controllers_data:
        st.warning("Não há controladores para associar a válvulas.")
        return

    # Criar opções com nome + ID visível
    controller_options = {
        f"{controller['name']} (ID: {controller['id']})": controller["id"]
        for controller in controllers_data
    }

    controller_choice = st.selectbox(
        "Selecione o Controlador", controller_options.keys()
    )
    selected_controller = controller_options[controller_choice]
    if st.button("Carregar Válvulas"):
        data = get_valves(token, selected_controller)
        if not data:
            st.info("Nenhuma válvula para editar.")
            return
        df = pd.DataFrame(data)
        rename_valve_columns(df)
        if "ID" in df.columns:
            df.set_index("ID", inplace=True)
        ids = list(df.index)
        selected_valve = st.selectbox("Selecione o ID da Válvula", ids)
        current_valve = df.loc[selected_valve]

        new_flow = st.number_input(
            "Nova Taxa de Fluxo (L/min)",
            value=float(current_valve["Taxa de Fluxo (L/min)"]),
            min_value=0.0,
            step=1.0,
        )
        if st.button("Atualizar Válvula"):
            resp = update_valve(token, selected_controller, selected_valve, new_flow)
            if resp and resp.status_code == 200:
                st.success("Válvula atualizada com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao atualizar válvula.")


def show_delete_valve(token):
    st.subheader("Excluir Válvula")

    # Usar seletor padronizado de controlador
    controller_id, controller_name = controller_selector(
        token, "Selecione o Controlador *"
    )

    if not controller_id:
        return

    # Usar seletor dependente de válvulas
    valve_id, valve_name = valve_selector(
        token, controller_id, "Selecione a Válvula para Excluir *"
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
            f"""
        - **Controlador**: {controller_name}
        - **ID da Válvula**: {valve_id}
        - **Vazão**: {valve_info.get('flowRate', 0):.1f} L/min
        """
        )

        if st.button("🗑️ Confirmar Exclusão", type="primary"):
            resp = delete_valve(token, controller_id, valve_id)
            if handle_api_response_v2(resp, "Válvula excluída com sucesso!"):
                invalidate_caches_after_mutation("valves")
                st.rerun()


def show():
    st.title("Gerenciamento de Válvulas")

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return

    menu_options = ["Listar", "Criar", "Editar", "Excluir"]
    choice = st.radio(
        "O que deseja fazer?", menu_options, horizontal=True, key="radio_valves"
    )

    if choice == "Listar":
        show_list_valves(token)
    elif choice == "Criar":
        show_create_valve(token)
    elif choice == "Editar":
        show_edit_valve(token)
    elif choice == "Excluir":
        show_delete_valve(token)
