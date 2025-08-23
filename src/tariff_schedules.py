# src/tariff_schedules.py

from datetime import date, time

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (format_datetime_for_api, handle_api_response,
                               monetary_input, percentage_input)


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


def tariff_selector(token, label="Selecione a Tarifa *"):
    """Seletor padronizado de tarifas com formato 'Data (ID: X)'."""
    all_tariffs = get_all_tariffs(token)
    if not all_tariffs:
        st.warning("Nenhuma tarifa cadastrada.")
        return None, None

    tariff_options = {
        f"{tariff['date'][:10]} (ID: {tariff['id']})": tariff["id"]
        for tariff in all_tariffs
        if "id" in tariff and "date" in tariff
    }

    if not tariff_options:
        st.warning("Nenhuma tarifa disponível.")
        return None, None

    choice = st.selectbox(label, tariff_options.keys())
    selected_id = tariff_options[choice]

    # Retornar objeto completo da tarifa
    selected_tariff = next((t for t in all_tariffs if t["id"] == selected_id), None)
    return selected_id, selected_tariff


def validate_tariff_times(day_start, day_end, night_start, night_end):
    """Valida se os horários não se sobrepõem incorretamente."""
    # Converter time objects para minutos para facilitar comparação
    day_start_min = day_start.hour * 60 + day_start.minute
    day_end_min = day_end.hour * 60 + day_end.minute
    # night_start_min = night_start.hour * 60 + night_start.minute
    # night_end_min = night_end.hour * 60 + night_end.minute

    # Validação básica: período diurno deve ser consistente
    if day_start_min >= day_end_min:
        return False, "Horário de início diurno deve ser anterior ao fim diurno."

    # TODO: Implementar validação completa de sobreposição diurno/noturno
    # Por ora, apenas validação básica do período diurno
    return True, "Horários válidos."


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
        # Data usando date_input
        date_val = st.date_input(
            "Data da Tarifa *", value=date.today(), help="Data de vigência da tarifa"
        )

        # Horários usando time_input
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Período Diurno")
            daytime_start = st.time_input(
                "Início (Diurno) *",
                value=time(6, 0),
                help="Horário de início do período diurno",
            )
            daytime_end = st.time_input(
                "Fim (Diurno) *",
                value=time(18, 0),
                help="Horário de fim do período diurno",
            )

        with col2:
            st.markdown("#### Período Noturno")
            nighttime_start = st.time_input(
                "Início (Noturno) *",
                value=time(18, 0),
                help="Horário de início do período noturno",
            )
            nighttime_end = st.time_input(
                "Fim (Noturno) *",
                value=time(6, 0),
                help="Horário de fim do período noturno",
            )

        # Valores monetários
        daytime_tariff = monetary_input(
            "Tarifa Diurna (R$/kWh) *",
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período diurno",
        )

        nighttime_tariff = monetary_input(
            "Tarifa Noturna (R$/kWh) *",
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período noturno",
        )

        nighttime_discount = percentage_input(
            "Desconto Noturno (%)",
            help_text="Percentual de desconto aplicado no período noturno",
        )

        submitted_new = st.form_submit_button("Criar Tarifa")
        if submitted_new:
            # Validar horários
            times_valid, times_msg = validate_tariff_times(
                daytime_start, daytime_end, nighttime_start, nighttime_end
            )
            if not times_valid:
                st.error(times_msg)
                return

            # Preparar dados para API
            data = {
                "date": format_datetime_for_api(date_val),
                "daytimeStart": daytime_start.strftime("%H:%M:%S"),
                "daytimeEnd": daytime_end.strftime("%H:%M:%S"),
                "nighttimeStart": nighttime_start.strftime("%H:%M:%S"),
                "nighttimeEnd": nighttime_end.strftime("%H:%M:%S"),
                "daytimeTariff": daytime_tariff,
                "nighttimeTariff": nighttime_tariff,
                "nighttimeDiscount": nighttime_discount,
            }

            resp = create_tariff(token, data)
            handle_api_response(resp, "Tarifa criada com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()


def show_edit_tariff(token):
    """Formulário para editar uma tarifa existente."""
    st.subheader("Editar Tarifa Existente")

    # Usar seletor padronizado
    selected_id, tariff_obj = tariff_selector(token, "Selecione a Tarifa para Editar")
    if not tariff_obj:
        return

    with st.form("EditarTarifa"):
        # Converter data ISO para date object
        try:
            date_obj = pd.to_datetime(tariff_obj["date"]).date()
        except (ValueError, TypeError, KeyError):
            date_obj = date.today()

        date_val = st.date_input(
            "Data da Tarifa *", value=date_obj, help="Data de vigência da tarifa"
        )

        # Converter strings de horário para time objects
        def parse_time_string(time_str):
            try:
                return time.fromisoformat(time_str)
            except (ValueError, TypeError):
                # Fallback para formato HH:MM:SS
                try:
                    parts = time_str.split(":")
                    return time(
                        int(parts[0]),
                        int(parts[1]),
                        int(parts[2]) if len(parts) > 2 else 0,
                    )
                except (ValueError, TypeError, IndexError):
                    return time(0, 0)

        # Horários usando time_input
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Período Diurno")
            daytime_start = st.time_input(
                "Início (Diurno) *",
                value=parse_time_string(tariff_obj["daytimeStart"]),
                help="Horário de início do período diurno",
            )
            daytime_end = st.time_input(
                "Fim (Diurno) *",
                value=parse_time_string(tariff_obj["daytimeEnd"]),
                help="Horário de fim do período diurno",
            )

        with col2:
            st.markdown("#### Período Noturno")
            nighttime_start = st.time_input(
                "Início (Noturno) *",
                value=parse_time_string(tariff_obj["nighttimeStart"]),
                help="Horário de início do período noturno",
            )
            nighttime_end = st.time_input(
                "Fim (Noturno) *",
                value=parse_time_string(tariff_obj["nighttimeEnd"]),
                help="Horário de fim do período noturno",
            )

        # Valores monetários
        daytime_tariff = monetary_input(
            "Tarifa Diurna (R$/kWh) *",
            value=float(tariff_obj["daytimeTariff"]),
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período diurno",
        )

        nighttime_tariff = monetary_input(
            "Tarifa Noturna (R$/kWh) *",
            value=float(tariff_obj["nighttimeTariff"]),
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período noturno",
        )

        nighttime_discount = percentage_input(
            "Desconto Noturno (%)",
            value=float(tariff_obj["nighttimeDiscount"]),
            help_text="Percentual de desconto aplicado no período noturno",
        )

        submitted_edit = st.form_submit_button("Atualizar Tarifa")
        if submitted_edit:
            # Validar horários
            times_valid, times_msg = validate_tariff_times(
                daytime_start, daytime_end, nighttime_start, nighttime_end
            )
            if not times_valid:
                st.error(times_msg)
                return

            data_edit = {
                "id": selected_id,
                "date": format_datetime_for_api(date_val),
                "daytimeStart": daytime_start.strftime("%H:%M:%S"),
                "daytimeEnd": daytime_end.strftime("%H:%M:%S"),
                "nighttimeStart": nighttime_start.strftime("%H:%M:%S"),
                "nighttimeEnd": nighttime_end.strftime("%H:%M:%S"),
                "daytimeTariff": daytime_tariff,
                "nighttimeTariff": nighttime_tariff,
                "nighttimeDiscount": nighttime_discount,
            }

            resp = update_tariff(token, selected_id, data_edit)
            handle_api_response(resp, "Tarifa atualizada com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()


def show_delete_tariff(token):
    """Formulário para excluir uma tarifa."""
    st.subheader("Excluir Tarifa Existente")

    # Usar seletor padronizado
    selected_id, tariff_obj = tariff_selector(token, "Selecione a Tarifa para Excluir")
    if not tariff_obj:
        return

    # Mostrar informações da tarifa selecionada
    st.warning("⚠️ **ATENÇÃO**: Você está prestes a excluir a tarifa:")
    st.info(
        f"""
    - **Data**: {tariff_obj['date'][:10]}
    - **ID**: {tariff_obj['id']}
    - **Tarifa Diurna**: R$ {tariff_obj['daytimeTariff']:.4f}/kWh
    - **Tarifa Noturna**: R$ {tariff_obj['nighttimeTariff']:.4f}/kWh
    - **Desconto Noturno**: {tariff_obj['nighttimeDiscount']:.1f}%
    """
    )

    if st.button("🗑️ Confirmar Exclusão", type="primary"):
        resp = delete_tariff(token, selected_id)
        handle_api_response(resp, "Tarifa excluída com sucesso!")
        if resp and 200 <= resp.status_code < 300:
            st.rerun()


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
