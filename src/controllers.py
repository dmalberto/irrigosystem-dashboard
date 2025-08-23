import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (geographic_coordinates_input,
                               handle_api_response, power_input,
                               validate_coordinates)


def rename_controller_columns(df: pd.DataFrame):
    """Renomeia colunas do controller para português."""
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "name": "Nome",
            "pumpPower": "Potência (W)",
            "efficiency": "Eficiência (%)",
            "powerFactor": "Fator de Potência",
            "latitude": "Latitude",
            "longitude": "Longitude",
        }
        df.rename(columns=columns_mapping, inplace=True)


def get_controllers(token):
    """GET /api/controllers

    Retorna: array de Controller ou ErrorResponse conforme Swagger
    Status codes: 200 (Success), 500 (Server Error)
    """
    endpoint = "/api/controllers"
    resp = api_request("GET", endpoint, token=token)
    if not resp:
        st.error("Erro ao conectar com a API de controladores.")
        return []

    if resp.status_code == 200:
        try:
            data = resp.json()
            if isinstance(data, list):
                return data
            else:
                st.error("Formato de resposta inesperado da API.")
                return []
        except ValueError:
            st.error("Erro ao processar resposta JSON da API.")
            return []
    elif resp.status_code == 500:
        st.error("Erro interno do servidor ao buscar controladores.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar controladores: {resp.status_code}")
        return []


def create_controller(
    token, name, pump_power, efficiency, power_factor, latitude, longitude
):
    """POST /api/controllers

    Campos obrigatórios conforme Swagger: name, pumpPower, efficiency, powerFactor, latitude, longitude, id
    Note: id é gerado pelo servidor
    """
    endpoint = "/api/controllers"
    body = {
        "name": name,
        "pumpPower": pump_power,
        "efficiency": efficiency,
        "powerFactor": power_factor,
        "latitude": latitude,
        "longitude": longitude,
    }
    resp = api_request("POST", endpoint, token=token, json=body)
    return resp


def update_controller(
    token,
    controller_id,
    name,
    pump_power,
    efficiency,
    power_factor,
    latitude,
    longitude,
):
    """PUT /api/controllers/{id}

    Parâmetro: id (int64) no path
    Campos obrigatórios no body: name, pumpPower, efficiency, powerFactor, latitude, longitude, id
    """
    endpoint = f"/api/controllers/{controller_id}"
    body = {
        "id": controller_id,  # Swagger requer id no body também
        "name": name,
        "pumpPower": pump_power,
        "efficiency": efficiency,
        "powerFactor": power_factor,
        "latitude": latitude,
        "longitude": longitude,
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
        # Campos obrigatórios conforme Swagger
        name = st.text_input(
            "Nome *",
            placeholder="Ex: Bomba Setor A",
            help="Nome do controlador (obrigatório)",
        )
        pump_power = power_input(
            "Potência da Bomba (W) *", help_text="Potência nominal da bomba em watts"
        )
        efficiency = st.number_input(
            "Eficiência *",
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            value=0.85,
            format="%.2f",
            help="Eficiência da bomba (0.01-1.00)",
        )
        power_factor = st.number_input(
            "Fator de Potência *",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=0.9,
            format="%.2f",
            help="Fator de potência (0.0-1.0)",
        )
        latitude, longitude = geographic_coordinates_input()

        submitted = st.form_submit_button("Criar Controlador")
        if submitted:
            # Validar campos obrigatórios
            if not name.strip():
                st.error("Nome é obrigatório.")
                return

            # Validar coordenadas
            coords_valid, coords_msg = validate_coordinates(latitude, longitude)
            if not coords_valid:
                st.error(coords_msg)
                return

            resp = create_controller(
                token, name, pump_power, efficiency, power_factor, latitude, longitude
            )

            handle_api_response(resp, "Controlador criado com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()


def show_edit_controller(token):
    st.subheader("Editar Controlador")
    data = get_controllers(token)
    if not data:
        st.info("Nenhum controlador cadastrado para editar.")
        return

    # Melhorar UX: seletor por nome em vez de ID
    controller_options = {f"{ctrl['name']} (ID: {ctrl['id']})": ctrl for ctrl in data}

    if not controller_options:
        st.warning("Nenhum controlador para editar.")
        return

    selected_option = st.selectbox(
        "Selecione o Controlador para Editar",
        list(controller_options.keys()),
        help="Escolha o controlador pelo nome",
    )
    selected_controller = controller_options[selected_option]

    with st.form("FormEditarControlador"):
        # Pré-preencher com dados atuais
        new_name = st.text_input(
            "Nome *",
            value=selected_controller["name"],
            help="Nome do controlador (obrigatório)",
        )
        new_pump_power = power_input(
            "Potência da Bomba (W) *",
            value=float(selected_controller["pumpPower"]),
            help_text="Potência nominal da bomba em watts",
        )
        new_efficiency = st.number_input(
            "Eficiência *",
            value=float(selected_controller["efficiency"]),
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            format="%.2f",
            help="Eficiência da bomba (0.01-1.00)",
        )
        new_power_factor = st.number_input(
            "Fator de Potência *",
            value=float(selected_controller["powerFactor"]),
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            format="%.2f",
            help="Fator de potência (0.0-1.0)",
        )
        new_latitude, new_longitude = geographic_coordinates_input(
            lat_value=float(selected_controller["latitude"]),
            lon_value=float(selected_controller["longitude"]),
        )

        submitted = st.form_submit_button("Atualizar")
        if submitted:
            if not new_name.strip():
                st.error("Nome é obrigatório.")
                return

            # Validar coordenadas
            coords_valid, coords_msg = validate_coordinates(new_latitude, new_longitude)
            if not coords_valid:
                st.error(coords_msg)
                return

            resp = update_controller(
                token,
                selected_controller["id"],
                new_name,
                new_pump_power,
                new_efficiency,
                new_power_factor,
                new_latitude,
                new_longitude,
            )

            handle_api_response(resp, "Controlador atualizado com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()


def show_delete_controller(token):
    st.subheader("Excluir Controlador")
    data = get_controllers(token)
    if not data:
        st.info("Nenhum controlador cadastrado para excluir.")
        return

    # Melhorar UX: seletor por nome em vez de ID
    controller_options = {f"{ctrl['name']} (ID: {ctrl['id']})": ctrl for ctrl in data}

    if not controller_options:
        st.warning("Nenhum controlador para excluir.")
        return

    selected_option = st.selectbox(
        "Selecione o Controlador para Excluir",
        list(controller_options.keys()),
        help="Escolha o controlador pelo nome",
    )
    selected_controller = controller_options[selected_option]

    # Mostrar informações do controlador selecionado
    st.warning("⚠️ **ATENÇÃO**: Você está prestes a excluir o controlador:")
    st.info(
        f"""
    - **Nome**: {selected_controller['name']}
    - **ID**: {selected_controller['id']}
    - **Potência**: {selected_controller['pumpPower']} W
    - **Coordenadas**: ({selected_controller['latitude']}, {selected_controller['longitude']})
    """
    )

    if st.button("🗑️ Confirmar Exclusão", type="primary"):
        resp = delete_controller(token, selected_controller["id"])

        handle_api_response(resp, "Controlador excluído com sucesso!")
        if resp and 200 <= resp.status_code < 300:
            st.rerun()


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
