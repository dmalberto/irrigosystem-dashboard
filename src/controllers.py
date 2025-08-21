import pandas as pd
import streamlit as st

from api import api_request
from src.utils import handle_api_response, safe_dataframe_display, validate_positive_number


def rename_controller_columns(df: pd.DataFrame):
    """Renomeia colunas do controller para português."""
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "pumpPower": "Potência (W)",
            "efficiency": "Eficiência (0-1)",
            "powerFactor": "Fator de Potência",
        }
        df.rename(columns=columns_mapping, inplace=True)


def get_controllers(token):
    """GET /api/controllers"""
    endpoint = "/api/controllers"
    resp = api_request("GET", endpoint, token=token, timeout=30)
    data = handle_api_response(resp, error_message="Falha ao obter lista de controladores")
    return data if data else []


def create_controller(token, pump_power, efficiency, power_factor):
    """POST /api/controllers"""
    if not (validate_positive_number(pump_power, "Potência") and 
            0 <= efficiency <= 1 and 0 <= power_factor <= 1):
        return None
        
    endpoint = "/api/controllers"
    body = {
        "pumpPower": pump_power,
        "efficiency": efficiency,
        "powerFactor": power_factor,
    }
    resp = api_request("POST", endpoint, token=token, json=body, timeout=30)
    return resp


def update_controller(token, controller_id, pump_power, efficiency, power_factor):
    """PUT /api/controllers/{id}"""
    endpoint = f"/api/controllers/{controller_id}"
    body = {
        "pumpPower": pump_power,
        "efficiency": efficiency,
        "powerFactor": power_factor,
    }
    resp = api_request("PUT", endpoint, token=token, json=body)
    return resp


def delete_controller(token, controller_id):
    """DELETE /api/controllers/{id}"""
    endpoint = f"/api/controllers/{controller_id}"
    resp = api_request("DELETE", endpoint, token=token)
    return resp


def show_list_controllers(token):
    st.subheader("Listar Controladores")
    data = get_controllers(token)
    if data:
        df = pd.DataFrame(data)
        rename_controller_columns(df)
        if "ID" in df.columns:
            df.set_index("ID", inplace=True)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum controlador cadastrado.")


def show_create_controller(token):
    st.subheader("Criar Controlador")
    with st.form("FormCriarControlador"):
        pump_power = st.number_input("Potência (W)", min_value=0.0, step=1.0)
        efficiency = st.number_input(
            "Eficiência (0–1)", min_value=0.0, max_value=1.0, step=0.01
        )
        power_factor = st.number_input(
            "Fator de Potência", min_value=0.0, max_value=1.0, step=0.01
        )

        submitted = st.form_submit_button("Criar Controlador")
        if submitted:
            resp = create_controller(token, pump_power, efficiency, power_factor)
            if resp and resp.status_code == 201:
                st.success("Controlador criado com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao criar controlador.")


def show_edit_controller(token):
    st.subheader("Editar Controlador")
    data = get_controllers(token)
    if not data:
        st.info("Nenhum controlador cadastrado para editar.")
        return

    df = pd.DataFrame(data)
    rename_controller_columns(df)

    if "ID" in df.columns:
        df.set_index("ID", inplace=True)

    # Precisamos de um selectbox para escolher qual "ID" editar
    if df.empty:
        st.warning("Nenhum controlador para editar.")
        return

    ids = list(df.index)
    selected_id = st.selectbox("Selecione o ID do Controlador para Editar", ids)
    controller_row = df.loc[selected_id]

    with st.form("FormEditarControlador"):
        new_pump_power = st.number_input(
            "Potência (W)", value=float(controller_row["Potência (W)"]), step=1.0
        )
        new_efficiency = st.number_input(
            "Eficiência (0–1)",
            value=float(controller_row["Eficiência (0-1)"]),
            min_value=0.0,
            max_value=1.0,
            step=0.01,
        )
        new_power_factor = st.number_input(
            "Fator de Potência",
            value=float(controller_row["Fator de Potência"]),
            min_value=0.0,
            max_value=1.0,
            step=0.01,
        )
        submitted = st.form_submit_button("Atualizar")
        if submitted:
            resp = update_controller(
                token, selected_id, new_pump_power, new_efficiency, new_power_factor
            )
            if resp and resp.status_code == 200:
                st.success("Controlador atualizado com sucesso!")
                st.rerun()
            else:
                st.error("Falha ao atualizar controlador.")


def show_delete_controller(token):
    st.subheader("Excluir Controlador")
    data = get_controllers(token)
    if not data:
        st.info("Nenhum controlador cadastrado para excluir.")
        return

    df = pd.DataFrame(data)
    rename_controller_columns(df)

    if "ID" in df.columns:
        df.set_index("ID", inplace=True)

    if df.empty:
        st.warning("Nenhum controlador para excluir.")
        return

    ids = list(df.index)
    selected_id = st.selectbox("Selecione o ID do Controlador para Excluir", ids)

    if st.button("Confirmar Exclusão"):
        resp = delete_controller(token, selected_id)
        if resp and resp.status_code == 204:
            st.success("Controlador excluído com sucesso!")
            st.rerun()
        else:
            st.error("Falha ao excluir controlador.")


def show():
    st.title("Gerenciamento de Controladores")

    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return

    menu_options = ["Listar", "Criar", "Editar", "Excluir"]
    choice = st.radio(
        "O que deseja fazer?", menu_options, horizontal=True, key="radio_controllers"
    )

    if choice == "Listar":
        show_list_controllers(token)
    elif choice == "Criar":
        show_create_controller(token)
    elif choice == "Editar":
        show_edit_controller(token)
    elif choice == "Excluir":
        show_delete_controller(token)
