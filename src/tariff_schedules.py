# src/tariff_schedules.py

import pandas as pd
import streamlit as st

from api import api_request


def rename_tariff_columns(df: pd.DataFrame):
    """Renomeia colunas para português e formata datas."""
    if not df.empty:
        # Formatar datas para o padrão brasileiro
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m/%Y")

        columns_mapping = {
            "id": "ID",
            "date": "Data",
            "daytimeStart": "Início (Diurno)",
            "daytimeEnd": "Fim (Diurno)",
            "nighttimeStart": "Início (Noturno)",
            "nighttimeEnd": "Fim (Noturno)",
            "daytimeTariff": "Tarifa Diurna",
            "nighttimeTariff": "Tarifa Noturna",
            "nighttimeDiscount": "Desconto Noturno",
        }
        df.rename(columns=columns_mapping, inplace=True)


def get_all_tariffs(token):
    """GET /api/tariff-schedules
    
    Conforme OpenAPI, retorna TariffSchedule singular (não array).
    Normaliza para array para compatibilidade com UI existente.
    """
    endpoint = "/api/tariff-schedules"
    response = api_request("GET", endpoint, token=token)
    if not response:
        return []
    if response.status_code == 200:
        try:
            data = response.json()
            # OpenAPI define retorno como TariffSchedule singular
            if isinstance(data, dict) and data:
                # Se é um objeto válido, encapsula em array
                return [data]
            elif isinstance(data, list):
                # Caso API retorne array (diverge do Swagger)
                return data
            else:
                return []
        except ValueError:
            st.error("Erro ao processar resposta JSON das tarifas.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar tarifas.")
        return []
    else:
        st.error(f"Falha ao obter as tarifas. Status: {response.status_code}")
        return []


def get_current_tariff(token):
    """GET /api/tariff-schedules/current
    
    Retorna objeto TariffSchedule ou erro conforme OpenAPI.
    """
    endpoint = "/api/tariff-schedules/current"
    response = api_request("GET", endpoint, token=token)
    
    if not response:
        return {}
    
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON da tarifa atual.")
            return {}
    elif response.status_code == 404:
        st.info("Nenhuma tarifa atual encontrada.")
        return {}
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar tarifa atual.")
        return {}
    else:
        st.error(f"Falha ao obter tarifa atual. Status: {response.status_code}")
        return {}


def create_tariff(token, data):
    """POST /api/tariff-schedules
    
    Retorna TariffSchedule criado ou ErrorResponse conforme OpenAPI.
    """
    endpoint = "/api/tariff-schedules"
    resp = api_request("POST", endpoint, token=token, json=data)
    return resp


def update_tariff(token, tariff_id, data):
    """PUT /api/tariff-schedules/{id}
    
    Retorna TariffSchedule atualizado ou ErrorResponse conforme OpenAPI.
    """
    endpoint = f"/api/tariff-schedules/{tariff_id}"
    resp = api_request("PUT", endpoint, token=token, json=data)
    return resp


def delete_tariff(token, tariff_id):
    """DELETE /api/tariff-schedules/{id}
    
    Conforme OpenAPI, não retorna corpo na resposta de sucesso (204).
    Possíveis códigos: 404 (Not Found), 500 (Server Error).
    """
    endpoint = f"/api/tariff-schedules/{tariff_id}"
    resp = api_request("DELETE", endpoint, token=token)
    return resp


def show_current_tariff(token):
    """Exibe a tarifa atual de forma amigável."""
    st.subheader("Tarifa Atual")

    current_data = get_current_tariff(token)

    if current_data and "id" in current_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            # st.metric(label, value, delta=None, delta_color="normal", help=None, label_visibility="visible", border=False)
            st.metric(
                label="Tarifa Diurna (R$)",
                value=current_data["daytimeTariff"],
                help="Valor aplicado no período diurno.",
            )
        with col2:
            st.metric(
                label="Tarifa Noturna (R$)",
                value=current_data["nighttimeTariff"],
                help="Valor aplicado no período noturno.",
            )
        with col3:
            st.metric(
                label="Desconto Noturno",
                value=current_data["nighttimeDiscount"],
                help="Porcentagem de desconto aplicada no período noturno.",
            )
        st.write(f"**Início (Diurno)**: {current_data['daytimeStart']}")
        st.write(f"**Fim (Diurno)**: {current_data['daytimeEnd']}")
        st.write(f"**Início (Noturno)**: {current_data['nighttimeStart']}")
        st.write(f"**Fim (Noturno)**: {current_data['nighttimeEnd']}")

    else:
        st.info("Nenhuma tarifa atual encontrada.")


def show_list_tariffs(token):
    """Lista todas as tarifas em formato de tabela."""
    st.subheader("Listagem de Tarifas")
    all_tariffs = get_all_tariffs(token)
    if all_tariffs:
        df = pd.DataFrame(all_tariffs)
        rename_tariff_columns(df)
        st.dataframe(df.set_index("ID"))
    else:
        st.info("Nenhuma tarifa cadastrada.")


def show_create_tariff(token):
    """Formulário para criar nova tarifa."""
    st.subheader("Criar Nova Tarifa")
    with st.form("CriarTarifa"):
        date_val = st.text_input("Data (Formato: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)")
        daytime_start = st.text_input("Início (Diurno)", value="06:00:00")
        daytime_end = st.text_input("Fim (Diurno)", value="18:00:00")
        nighttime_start = st.text_input("Início (Noturno)", value="18:00:00")
        nighttime_end = st.text_input("Fim (Noturno)", value="06:00:00")
        daytime_tariff = st.number_input("Tarifa Diurna", min_value=0.0, step=0.1)
        nighttime_tariff = st.number_input("Tarifa Noturna", min_value=0.0, step=0.1)
        nighttime_discount = st.number_input(
            "Desconto Noturno", min_value=0.0, step=0.1
        )

        submitted_new = st.form_submit_button("Criar Tarifa")
        if submitted_new:
            data = {
                "date": date_val,
                "daytimeStart": daytime_start,
                "daytimeEnd": daytime_end,
                "nighttimeStart": nighttime_start,
                "nighttimeEnd": nighttime_end,
                "daytimeTariff": daytime_tariff,
                "nighttimeTariff": nighttime_tariff,
                "nighttimeDiscount": nighttime_discount,
            }
            resp = create_tariff(token, data)
            if resp and resp.status_code == 200:
                st.success("Tarifa criada com sucesso!")
                st.rerun()
            elif resp and resp.status_code == 400:
                st.error("Dados inválidos. Verifique os campos obrigatórios.")
            elif resp and resp.status_code == 409:
                st.error("Conflito: tarifa já existe para esta data.")
            elif resp and resp.status_code == 500:
                st.error("Erro interno do servidor ao criar tarifa.")
            else:
                st.error("Falha ao criar tarifa.")


def show_edit_tariff(token):
    """Formulário para editar uma tarifa existente."""
    st.subheader("Editar Tarifa Existente")
    # Precisamos listar as tarifas para o usuário escolher qual editar
    all_tariffs = get_all_tariffs(token)
    if not all_tariffs:
        st.info("Nenhuma tarifa cadastrada para editar.")
        return

    # Selecionar ID da tarifa
    tariff_ids = [t["id"] for t in all_tariffs if "id" in t]
    selected_id = st.selectbox("Selecione o ID da Tarifa para Editar", tariff_ids)
    # Encontrar objeto da tarifa
    tariff_obj = next((t for t in all_tariffs if t["id"] == selected_id), None)
    if not tariff_obj:
        st.error("Tarifa não encontrada.")
        return

    with st.form("EditarTarifa"):
        # Formatar data para exibição no formato brasileiro
        try:
            formatted_date = pd.to_datetime(tariff_obj["date"]).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        except:
            formatted_date = tariff_obj["date"]
        date_val = st.text_input("Data", value=formatted_date)
        daytime_start = st.text_input(
            "Início (Diurno)", value=tariff_obj["daytimeStart"]
        )
        daytime_end = st.text_input("Fim (Diurno)", value=tariff_obj["daytimeEnd"])
        nighttime_start = st.text_input(
            "Início (Noturno)", value=tariff_obj["nighttimeStart"]
        )
        nighttime_end = st.text_input("Fim (Noturno)", value=tariff_obj["nighttimeEnd"])
        daytime_tariff = st.number_input(
            "Tarifa Diurna",
            value=float(tariff_obj["daytimeTariff"]),
            step=0.1,
        )
        nighttime_tariff = st.number_input(
            "Tarifa Noturna",
            value=float(tariff_obj["nighttimeTariff"]),
            step=0.1,
        )
        nighttime_discount = st.number_input(
            "Desconto Noturno",
            value=float(tariff_obj["nighttimeDiscount"]),
            step=0.1,
        )
        submitted_edit = st.form_submit_button("Atualizar Tarifa")
        if submitted_edit:
            data_edit = {
                "id": selected_id,
                "date": date_val,
                "daytimeStart": daytime_start,
                "daytimeEnd": daytime_end,
                "nighttimeStart": nighttime_start,
                "nighttimeEnd": nighttime_end,
                "daytimeTariff": daytime_tariff,
                "nighttimeTariff": nighttime_tariff,
                "nighttimeDiscount": nighttime_discount,
            }
            resp = update_tariff(token, selected_id, data_edit)
            if resp and resp.status_code == 200:
                st.success("Tarifa atualizada com sucesso!")
                st.rerun()
            elif resp and resp.status_code == 400:
                st.error("Dados inválidos. Verifique os campos obrigatórios.")
            elif resp and resp.status_code == 404:
                st.error("Tarifa não encontrada.")
            elif resp and resp.status_code == 409:
                st.error("Conflito: tarifa já existe para esta data.")
            elif resp and resp.status_code == 500:
                st.error("Erro interno do servidor ao atualizar tarifa.")
            else:
                st.error("Falha ao atualizar tarifa.")


def show_delete_tariff(token):
    """Formulário para excluir uma tarifa."""
    st.subheader("Excluir Tarifa Existente")
    all_tariffs = get_all_tariffs(token)
    if not all_tariffs:
        st.info("Nenhuma tarifa cadastrada para excluir.")
        return

    # Selecionar ID para excluir
    tariff_ids = [t["id"] for t in all_tariffs if "id" in t]
    selected_id = st.selectbox("Selecione o ID da Tarifa para Excluir", tariff_ids)

    if st.button("Confirmar Exclusão"):
        resp = delete_tariff(token, selected_id)
        # OpenAPI define DELETE sem retorno de corpo (status 204)
        # Mas algumas implementações podem retornar 200
        if resp and resp.status_code in [200, 204]:
            st.success("Tarifa excluída com sucesso!")
            st.rerun()
        elif resp and resp.status_code == 404:
            st.error("Tarifa não encontrada para exclusão.")
        elif resp and resp.status_code == 500:
            st.error("Erro interno do servidor ao excluir tarifa.")
        else:
            st.error("Falha ao excluir tarifa.")


def show():
    st.title("Gerenciamento de Tarifas")

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return

    # Escolha da "subpágina"
    # Opções em português e mais amigáveis
    menu_options = [
        "Tarifa Atual",
        "Listar Tarifas",
        "Criar Tarifa",
        "Editar Tarifa",
        "Excluir Tarifa",
    ]
    choice = st.radio("O que deseja fazer?", menu_options, horizontal=True)

    if choice == "Tarifa Atual":
        show_current_tariff(token)

    elif choice == "Listar Tarifas":
        show_list_tariffs(token)

    elif choice == "Criar Tarifa":
        show_create_tariff(token)

    elif choice == "Editar Tarifa":
        show_edit_tariff(token)

    elif choice == "Excluir Tarifa":
        show_delete_tariff(token)


if __name__ == "__main__":
    show()
