import pandas as pd
import streamlit as st

from api import api_request
from src.controllers import (  # para reusar a lógica
    get_controllers,
    rename_controller_columns,
)


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


def create_valve(token, controller_id, flow_rate):
    """POST /api/controllers/{id}/valves"""
    endpoint = f"/api/controllers/{controller_id}/valves"
    body = {"flowRate": flow_rate}
    resp = api_request("POST", endpoint, token=token, json=body)
    return resp


def update_valve(token, controller_id, valve_id, flow_rate):
    """PUT /api/controllers/{controllerId}/valves/{valveId}"""
    endpoint = f"/api/controllers/{controller_id}/valves/{valve_id}"
    body = {"flowRate": flow_rate}
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

    # Montamos um selectbox com IDs dos controladores
    df_controllers = pd.DataFrame(controllers_data)
    if not df_controllers.empty:
        if "id" in df_controllers.columns:
            df_controllers.rename(columns={"id": "ID"}, inplace=True)
        controller_ids = df_controllers["ID"].tolist()
    else:
        st.warning("Nenhum controlador encontrado.")
        return

    controller_id = st.selectbox("Selecione o Controlador", controller_ids)

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

    df_ctrl = pd.DataFrame(controllers_data)
    if "id" in df_ctrl.columns:
        df_ctrl.rename(columns={"id": "ID"}, inplace=True)
    controller_ids = df_ctrl["ID"].tolist()

    with st.form("FormCriarValvula"):
        selected_controller = st.selectbox("Selecione o Controlador", controller_ids)
        flow_rate = st.number_input("Taxa de Fluxo (L/min)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Criar Válvula")
        if submitted:
            resp = create_valve(token, selected_controller, flow_rate)
            if resp and resp.status_code == 201:
                st.success("Válvula criada com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao criar válvula.")


def show_edit_valve(token):
    st.subheader("Editar Válvula Existente")

    controllers_data = get_controllers(token)
    if not controllers_data:
        st.warning("Não há controladores para associar a válvulas.")
        return

    df_ctrl = pd.DataFrame(controllers_data)
    if "id" in df_ctrl.columns:
        df_ctrl.rename(columns={"id": "ID"}, inplace=True)
    controller_ids = df_ctrl["ID"].tolist()

    selected_controller = st.selectbox("Selecione o Controlador", controller_ids)
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

    controllers_data = get_controllers(token)
    if not controllers_data:
        st.warning("Não há controladores para associar a válvulas.")
        return

    df_ctrl = pd.DataFrame(controllers_data)
    if "id" in df_ctrl.columns:
        df_ctrl.rename(columns={"id": "ID"}, inplace=True)
    controller_ids = df_ctrl["ID"].tolist()

    selected_controller = st.selectbox("Selecione o Controlador", controller_ids)
    if st.button("Carregar Válvulas para Excluir"):
        data = get_valves(token, selected_controller)
        if not data:
            st.info("Nenhuma válvula para excluir.")
            return
        df = pd.DataFrame(data)
        rename_valve_columns(df)
        if "ID" in df.columns:
            df.set_index("ID", inplace=True)
        ids = list(df.index)
        selected_valve = st.selectbox("Selecione o ID da Válvula", ids)
        if st.button("Confirmar Exclusão"):
            resp = delete_valve(token, selected_controller, selected_valve)
            if resp and resp.status_code == 204:
                st.success("Válvula excluída com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao excluir válvula.")


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
