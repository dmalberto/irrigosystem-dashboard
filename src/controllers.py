"""
Controladores - Modernizado com UI Foundations v3
Sistema completo de CRUD para controladores com FormBuilder,
ComponentLibrary e design tokens aplicados.
"""

import pandas as pd
import streamlit as st

from api import api_request
from src.design_tokens import DesignTokens
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    geographic_coordinates_input,
    handle_api_response_v2,
    power_input,
    validate_coordinates,
    cast_to_double,
    cast_to_int64,
)


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
    """Lista controladores com ComponentLibrary e loading states"""

    data = get_controllers(token)

    if data:
        # Cards informativos no topo
        col1, col2, col3 = st.columns(3)

        with col1:
            ComponentLibrary.metric_card(
                title="Total de Controladores", value=str(len(data)), icon="⚙️"
            )

        with col2:
            avg_power = sum(float(ctrl.get("pumpPower", 0)) for ctrl in data) / len(
                data
            )
            ComponentLibrary.metric_card(
                title="Potência Média", value=f"{avg_power:.0f}W", icon="⚡"
            )

        with col3:
            avg_efficiency = sum(
                float(ctrl.get("efficiency", 0)) for ctrl in data
            ) / len(data)
            ComponentLibrary.metric_card(
                title="Eficiência Média", value=f"{avg_efficiency:.1%}", icon="📊"
            )

        st.markdown("---")

        # Tabela com dados renomeados
        df = pd.DataFrame(data)
        rename_controller_columns(df)
        if "ID" in df.columns:
            df.set_index("ID", inplace=True)

        st.markdown("### 📋 Lista de Controladores")
        st.dataframe(df, use_container_width=True)

    else:
        enhanced_empty_state(
            title="Nenhum Controlador Cadastrado",
            description="Comece criando seu primeiro controlador para gerenciar o sistema de irrigação.",
            icon="⚙️",
            action_button={
                "label": "➕ Criar Primeiro Controlador",
                "callback": lambda: st.session_state.update({"show_create": True}),
            },
        )


def show_create_controller(token):
    """Formulário padronizado para criar controlador"""

    ComponentLibrary.card(
        title="Novo Controlador",
        content="Configure um novo controlador para gerenciar bombas e válvulas do sistema de irrigação.",
        icon="➕",
        color="primary",
    )

    with st.form("create_controller_form"):
        st.markdown("### ⚙️ Configurações Básicas")

        # Nome
        name = st.text_input(
            "Nome do Controlador *",
            placeholder="Ex: Controlador Setor Norte",
            help="Nome identificador para este controlador",
        )

        # Especificações técnicas
        col1, col2 = st.columns(2)

        with col1:
            pump_power = st.number_input(
                "Potência da Bomba (W) *",
                min_value=1.0,
                max_value=50000.0,
                value=1500.0,
                step=50.0,
                help="Potência nominal da bomba em watts",
            )

            efficiency = st.number_input(
                "Eficiência *",
                min_value=0.01,
                max_value=1.0,
                step=0.01,
                value=0.85,
                format="%.2f",
                help="Eficiência da bomba (0.01 = 1% até 1.00 = 100%)",
            )

        with col2:
            power_factor = st.number_input(
                "Fator de Potência *",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                value=0.9,
                format="%.2f",
                help="Fator de potência elétrica (0.0 a 1.0)",
            )

        # Localização geográfica
        st.markdown("### 📍 Localização")
        latitude, longitude = geographic_coordinates_input(
            lat_value=None, lon_value=None
        )

        # Botão de submit
        st.markdown("---")
        submitted = st.form_submit_button(
            "✅ Criar Controlador", type="primary", use_container_width=True
        )

        if submitted:
            errors = []

            # Validações
            if not name.strip():
                errors.append("Nome do controlador é obrigatório.")

            if pump_power <= 0:
                errors.append("Potência deve ser maior que 0W.")

            if not (0.01 <= efficiency <= 1.0):
                errors.append("Eficiência deve estar entre 0.01 e 1.0.")

            if not (0.0 <= power_factor <= 1.0):
                errors.append("Fator de potência deve estar entre 0.0 e 1.0.")

            # Validar coordenadas
            coords_valid, coords_msg = validate_coordinates(latitude, longitude)
            if not coords_valid:
                errors.append(coords_msg)

            # Exibir erros
            if errors:
                for error in errors:
                    ComponentLibrary.alert(error, alert_type="error")
                return

            # Criar controlador com casting correto
            with LoadingStates.spinner_with_cancel("Criando controlador..."):
                resp = create_controller(
                    token=token,
                    name=name.strip(),
                    pump_power=cast_to_double(pump_power),
                    efficiency=cast_to_double(efficiency),
                    power_factor=cast_to_double(power_factor),
                    latitude=cast_to_double(latitude),
                    longitude=cast_to_double(longitude),
                )

            if handle_api_response_v2(
                resp, f"✅ Controlador '{name}' criado com sucesso!"
            ):
                ComponentLibrary.alert(
                    f"O controlador **{name}** foi adicionado ao sistema com potência de {pump_power}W.",
                    alert_type="success",
                )
                st.rerun()


def show_edit_controller(token):
    st.markdown("### Editar Controlador")
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
        key="controller_edit_select",
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

            if handle_api_response_v2(resp, "Controlador atualizado com sucesso!"):
                st.rerun()


def show_delete_controller(token):
    st.markdown("### Excluir Controlador")
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
        key="controller_delete_select",
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

        if handle_api_response_v2(resp, "Controlador excluído com sucesso!"):
            st.rerun()


def show():
    st.title("⚙️ Controladores")

    token = st.session_state.get("token", None)
    if not token:
        ComponentLibrary.alert(
            "Usuário não autenticado. Faça login para acessar esta funcionalidade.",
            alert_type="error",
        )
        return

    # Tabs modernas em vez de radio buttons
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "➕ Criar", "✏️ Editar", "🗑️ Excluir"])

    with tab1:
        show_list_controllers(token)

    with tab2:
        show_create_controller(token)

    with tab3:
        show_edit_controller_modern(token)

    with tab4:
        show_delete_controller_modern(token)


def show_edit_controller_modern(token):
    """Versão modernizada da edição de controlador"""

    data = get_controllers(token)
    if not data:
        enhanced_empty_state(
            title="Nenhum Controlador para Editar",
            description="Você precisa criar pelo menos um controlador antes de poder editá-lo.",
            icon="⚙️",
            action_button={
                "label": "➕ Criar Primeiro Controlador",
                "callback": lambda: None,  # Callback será implementado com navegação
            },
        )
        return

    # Seletor de controlador com informações visuais
    st.markdown("### 🔍 Selecionar Controlador")

    controller_options = {f"{ctrl['name']} (ID: {ctrl['id']})": ctrl for ctrl in data}
    selected_option = st.selectbox(
        "Escolha o controlador para editar:",
        list(controller_options.keys()),
        help="Selecione pelo nome do controlador",
        key="controller_details_select",
    )
    selected_controller = controller_options[selected_option]

    # Card informativo do controlador selecionado
    ComponentLibrary.card(
        title=f"Editando: {selected_controller['name']}",
        content=f"""**ID:** {selected_controller['id']}  
**Potência Atual:** {selected_controller['pumpPower']}W  
**Eficiência:** {float(selected_controller['efficiency']):.1%}  
**Localização:** ({selected_controller['latitude']}, {selected_controller['longitude']})""",
        icon="✏️",
        color="warning",
    )

    # Formulário de edição similar ao de criação
    with st.form("edit_controller_form"):
        st.markdown("### ✏️ Novos Valores")

        # Campos pré-preenchidos
        new_name = st.text_input(
            "Nome do Controlador *",
            value=selected_controller["name"],
            help="Nome identificador para este controlador",
        )

        col1, col2 = st.columns(2)

        with col1:
            new_pump_power = st.number_input(
                "Potência da Bomba (W) *",
                value=float(selected_controller["pumpPower"]),
                min_value=1.0,
                max_value=50000.0,
                step=50.0,
                help="Potência nominal da bomba em watts",
            )

            new_efficiency = st.number_input(
                "Eficiência *",
                value=float(selected_controller["efficiency"]),
                min_value=0.01,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                help="Eficiência da bomba (0.01 a 1.0)",
            )

        with col2:
            new_power_factor = st.number_input(
                "Fator de Potência *",
                value=float(selected_controller["powerFactor"]),
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                help="Fator de potência elétrica (0.0 a 1.0)",
            )

        # Coordenadas atuais
        st.markdown("### 📍 Localização")
        new_latitude, new_longitude = geographic_coordinates_input(
            lat_value=float(selected_controller["latitude"]),
            lon_value=float(selected_controller["longitude"]),
        )

        st.markdown("---")
        submitted = st.form_submit_button(
            "✅ Atualizar Controlador", type="primary", use_container_width=True
        )

        if submitted:
            errors = []

            # Validações
            if not new_name.strip():
                errors.append("Nome do controlador é obrigatório.")

            if new_pump_power <= 0:
                errors.append("Potência deve ser maior que 0W.")

            # Validar coordenadas
            coords_valid, coords_msg = validate_coordinates(new_latitude, new_longitude)
            if not coords_valid:
                errors.append(coords_msg)

            if errors:
                for error in errors:
                    ComponentLibrary.alert(error, alert_type="error")
                return

            # Atualizar controlador
            with LoadingStates.spinner_with_cancel("Atualizando controlador..."):
                resp = update_controller(
                    token=token,
                    controller_id=cast_to_int64(selected_controller["id"]),
                    name=new_name.strip(),
                    pump_power=cast_to_double(new_pump_power),
                    efficiency=cast_to_double(new_efficiency),
                    power_factor=cast_to_double(new_power_factor),
                    latitude=cast_to_double(new_latitude),
                    longitude=cast_to_double(new_longitude),
                )

            if handle_api_response_v2(
                resp, f"✅ Controlador '{new_name}' atualizado com sucesso!"
            ):
                ComponentLibrary.alert(
                    f"As alterações no controlador **{new_name}** foram salvas.",
                    alert_type="success",
                )
                st.rerun()


def show_delete_controller_modern(token):
    """Versão modernizada da exclusão de controlador"""

    data = get_controllers(token)
    if not data:
        enhanced_empty_state(
            title="Nenhum Controlador para Excluir",
            description="Não há controladores cadastrados no sistema.",
            icon="⚙️",
        )
        return

    ComponentLibrary.alert(
        "⚠️ **ATENÇÃO**: A exclusão de um controlador é permanente e não pode ser desfeita. "
        "Certifique-se de que não há válvulas ou ativações dependentes.",
        alert_type="warning",
    )

    # Seletor de controlador
    controller_options = {f"{ctrl['name']} (ID: {ctrl['id']})": ctrl for ctrl in data}
    selected_option = st.selectbox(
        "Selecione o controlador para excluir:",
        list(controller_options.keys()),
        help="Escolha cuidadosamente o controlador a ser removido",
        key="controller_delete_confirm_select",
    )
    selected_controller = controller_options[selected_option]

    # Card de confirmação visual
    st.markdown(
        f"""
    <div style="
        background-color: {DesignTokens.COLORS['error']}20;
        border: 2px solid {DesignTokens.COLORS['error']};
        border-radius: {DesignTokens.RADIUS['lg']};
        padding: {DesignTokens.SPACING['6']};
        margin: {DesignTokens.SPACING['4']} 0;
    ">
        <h3 style="color: {DesignTokens.COLORS['error']}; margin: 0 0 {DesignTokens.SPACING['3']} 0;">
            🚨 CONTROLADOR A SER EXCLUÍDO
        </h3>
        <ul style="margin: 0;">
            <li><strong>Nome:</strong> {selected_controller['name']}</li>
            <li><strong>ID:</strong> {selected_controller['id']}</li>
            <li><strong>Potência:</strong> {selected_controller['pumpPower']} W</li>
            <li><strong>Localização:</strong> ({selected_controller['latitude']}, {selected_controller['longitude']})</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Confirmação dupla
    confirm_text = st.text_input(
        f"Para confirmar, digite o nome do controlador: **{selected_controller['name']}**",
        placeholder="Digite o nome exato aqui...",
        help="Esta confirmação é obrigatória para realizar a exclusão",
    )

    # Botão de exclusão
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🗑️ CONFIRMAR EXCLUSÃO PERMANENTE",
            type="primary",
            use_container_width=True,
            disabled=(confirm_text != selected_controller["name"]),
        ):
            with LoadingStates.spinner_with_cancel("Excluindo controlador..."):
                resp = delete_controller(
                    token, cast_to_int64(selected_controller["id"])
                )

            if handle_api_response_v2(
                resp,
                f"✅ Controlador '{selected_controller['name']}' excluído com sucesso!",
            ):
                ComponentLibrary.alert(
                    f"O controlador **{selected_controller['name']}** foi removido permanentemente do sistema.",
                    alert_type="success",
                )
                st.rerun()
