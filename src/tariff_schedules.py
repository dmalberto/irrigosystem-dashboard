# src/tariff_schedules.py
"""
Gerenciamento de Tarifas - Modernizado com UI Foundations v3
FormBuilder, ComponentLibrary e design tokens aplicados.
"""

from datetime import date, time

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state,
    format_datetime_for_api,
    handle_api_response_v2,
    monetary_input,
    percentage_input
)


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

    choice = st.selectbox(label, tariff_options.keys(), key=f"tariff_selector_{label.replace(' ', '_').lower()}")
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
    """Exibe a tarifa atual de forma amigável com ComponentLibrary."""
    st.markdown("### 🏷️ Tarifa Vigente")

    with LoadingStates.spinner_with_cancel("Carregando tarifa atual..."):
        current_data = get_current_tariff(token)

    if current_data and "id" in current_data:
        # Cards de métricas com ComponentLibrary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ComponentLibrary.metric_card(
                title="Tarifa Diurna",
                value=f"R$ {current_data['daytimeTariff']:.4f}/kWh",
                icon="☀️"
            )
        
        with col2:
            ComponentLibrary.metric_card(
                title="Tarifa Noturna",
                value=f"R$ {current_data['nighttimeTariff']:.4f}/kWh",
                icon="🌙"
            )
        
        with col3:
            ComponentLibrary.metric_card(
                title="Desconto Noturno",
                value=f"{current_data['nighttimeDiscount']:.1f}%",
                delta="Economia",
                icon="💸"
            )
        
        # Card com informações dos horários
        ComponentLibrary.card(
            title="🕐 Horários de Vigência",
            content=f"""**Período Diurno:**  
• Início: {current_data['daytimeStart']}  
• Fim: {current_data['daytimeEnd']}

**Período Noturno:**  
• Início: {current_data['nighttimeStart']}  
• Fim: {current_data['nighttimeEnd']}""",
            color="info"
        )

    else:
        enhanced_empty_state(
            title="Nenhuma Tarifa Vigente",
            description="Não há tarifas configuradas como vigentes no sistema. Crie uma nova tarifa para começar.",
            icon="💰",
            action_button={
                "label": "➕ Criar Primeira Tarifa",
                "key": "create_first_tariff"
            }
        )


def show_list_tariffs(token):
    """Lista todas as tarifas em formato de tabela com ComponentLibrary."""
    st.markdown("### 📋 Tarifas Cadastradas")
    
    all_tariffs = get_all_tariffs(token)
    
    if all_tariffs:
        # Card informativo
        ComponentLibrary.card(
            title="📋 Resumo das Tarifas",
            content=f"Total de {len(all_tariffs)} tarifa(s) cadastrada(s) no sistema.",
            color="info"
        )
        
        df = pd.DataFrame(all_tariffs)
        rename_tariff_columns(df)
        st.dataframe(df.set_index("ID"), use_container_width=True)
    else:
        enhanced_empty_state(
            title="Nenhuma Tarifa Cadastrada",
            description="O sistema ainda não possui tarifas cadastradas. Crie uma nova tarifa para definir os valores de consumo de energia.",
            icon="💰",
            action_button={
                "label": "➕ Cadastrar Primeira Tarifa",
                "key": "create_first_tariff_from_list"
            }
        )


def show_create_tariff(token):
    """Formulário para criar nova tarifa usando FormBuilder."""
    st.markdown("### ➕ Cadastrar Nova Tarifa")
    
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

        submitted_new = st.form_submit_button("✅ Cadastrar Tarifa")
        if submitted_new:
            # Validar horários
            times_valid, times_msg = validate_tariff_times(
                daytime_start, daytime_end, nighttime_start, nighttime_end
            )
            if not times_valid:
                ComponentLibrary.alert(times_msg, "error")
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
            if handle_api_response_v2(resp, "Tarifa criada com sucesso!"):
                st.rerun()


def show_edit_tariff(token):
    """Formulário para editar uma tarifa existente."""
    st.markdown("### ✏️ Editar Tarifa Existente")

    # Usar seletor padronizado
    selected_id, tariff_obj = tariff_selector(token, "Selecione a Tarifa para Editar *")
    if not tariff_obj:
        enhanced_empty_state(
            title="Selecione uma Tarifa",
            description="Escolha uma tarifa cadastrada acima para editar suas informações.",
            icon="✏️"
        )
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

        # Função helper para parsing seguro de valores
        def safe_float_parse(value, default=0.01):
            try:
                parsed_value = float(value)
                return parsed_value if parsed_value >= 0 else default
            except (ValueError, TypeError):
                return default

        # Valores monetários com parsing seguro
        daytime_tariff = monetary_input(
            "Tarifa Diurna (R$/kWh) *",
            value=safe_float_parse(tariff_obj["daytimeTariff"], 0.01),
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período diurno",
        )

        nighttime_tariff = monetary_input(
            "Tarifa Noturna (R$/kWh) *",
            value=safe_float_parse(tariff_obj["nighttimeTariff"], 0.01),
            min_value=0.01,
            max_value=5.0,
            help_text="Valor da tarifa no período noturno",
        )

        nighttime_discount = percentage_input(
            "Desconto Noturno (%)",
            value=safe_float_parse(tariff_obj["nighttimeDiscount"], 0.0),
            help_text="Percentual de desconto aplicado no período noturno",
        )

        submitted_edit = st.form_submit_button("💾 Atualizar Tarifa")
        if submitted_edit:
            # Validar horários
            times_valid, times_msg = validate_tariff_times(
                daytime_start, daytime_end, nighttime_start, nighttime_end
            )
            if not times_valid:
                ComponentLibrary.alert(times_msg, "error")
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
            if handle_api_response_v2(resp, "Tarifa atualizada com sucesso!"):
                st.rerun()


def show_delete_tariff(token):
    """Formulário para excluir uma tarifa."""
    st.markdown("### 🗑️ Excluir Tarifa Existente")

    # Usar seletor padronizado
    selected_id, tariff_obj = tariff_selector(token, "Selecione a Tarifa para Excluir *")
    if not tariff_obj:
        enhanced_empty_state(
            title="Selecione uma Tarifa",
            description="Escolha uma tarifa cadastrada acima para excluir do sistema.",
            icon="🗑️"
        )
        return

    # Mostrar informações da tarifa selecionada com ComponentLibrary
    ComponentLibrary.alert(
        "⚠️ **ATENÇÃO**: Você está prestes a excluir permanentemente esta tarifa do sistema.",
        "warning"
    )
    
    ComponentLibrary.card(
        title="🗑️ Tarifa a ser Excluída",
        content=f"""- **Data de Vigência**: {tariff_obj['date'][:10]}
- **ID**: {tariff_obj['id']}
- **Tarifa Diurna**: R$ {tariff_obj['daytimeTariff']:.4f}/kWh
- **Tarifa Noturna**: R$ {tariff_obj['nighttimeTariff']:.4f}/kWh
- **Desconto Noturno**: {tariff_obj['nighttimeDiscount']:.1f}%""",
        color="error"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:  # Centralizar o botão
        if st.button("🗑️ Confirmar Exclusão", type="primary"):
            with LoadingStates.spinner_with_cancel("Excluindo tarifa..."):
                resp = delete_tariff(token, selected_id)
                
            if handle_api_response_v2(resp, "Tarifa excluída com sucesso!"):
                st.rerun()


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
            delta=f"{projected_consumption_diurno + projected_consumption_noturno} kWh total",
            icon="💰"
        )
    
    # Detalhes da simulação
    ComponentLibrary.card(
        title="💡 Detalhes da Simulação",
        content=f"""
        **Tarifa Diurna:** R$ {diurna:.4f} por kWh
        **Tarifa Noturna:** R$ {noturna:.4f} por kWh
        {f'**Desconto Noturno:** {desconto:.1f}%' if desconto > 0 else ''}
        {f'**Tarifa Noturna com Desconto:** R$ {tarifa_noturna_com_desconto:.4f} por kWh' if desconto > 0 else ''}
        
        **Economia Noturna:** R$ {(projected_consumption_noturno * noturna) - custo_noturno:.2f}
        **% Economia:** {((projected_consumption_noturno * noturna) - custo_noturno) / (custo_total + ((projected_consumption_noturno * noturna) - custo_noturno)) * 100:.1f}%
        """,
        color="info"
    )


def show_simulation(token):
    """Simulação de custos de energia baseada nas tarifas cadastradas."""
    st.markdown("### 🔮 Simulação de Custos de Energia")
    
    ComponentLibrary.card(
        title="ℹ️ Como Funciona a Simulação",
        content="""
        Informe o consumo projetado de energia nos períodos diurno e noturno para calcular 
        o custo estimado baseado na tarifa vigente atual. A simulação considera descontos
        noturnos quando aplicáveis.
        """,
        color="info"
    )

    with st.form("SimulacaoTarifas"):
        st.markdown("### Parâmetros da Simulação")
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ☀️ Período Diurno")
            projected_consumption_diurno = st.number_input(
                "Consumo Projetado Diurno (kWh)",
                min_value=0.0,
                step=1.0,
                value=100.0,
                help="Consumo esperado durante o período diurno",
            )

        with col2:
            st.markdown("#### 🌙 Período Noturno")
            projected_consumption_noturno = st.number_input(
                "Consumo Projetado Noturno (kWh)",
                min_value=0.0,
                step=1.0,
                value=50.0,
                help="Consumo esperado durante o período noturno",
            )

        submitted = st.form_submit_button("🧮 Calcular Simulação", type="primary")

        if submitted:
            with LoadingStates.spinner_with_cancel("Calculando simulação..."):
                tariffs = get_current_tariff(token)

            if tariffs and "daytimeTariff" in tariffs:
                simulate_future_costs(
                    tariffs,
                    projected_consumption_diurno,
                    projected_consumption_noturno,
                )
            else:
                ComponentLibrary.alert(
                    "Não é possível simular custos sem tarifas vigentes. Configure uma tarifa atual na aba 'Tarifa Atual' primeiro.",
                    "error",
                )


def show():
    st.title("💰 Gerenciamento de Tarifas")

    token = st.session_state.get("token")
    if not token:
        ComponentLibrary.alert("Usuário não autenticado.", "error")
        return

    # Tabs modernizadas
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏷️ Tarifa Atual",
        "📋 Listar Tarifas", 
        "🔮 Simulação",
        "➕ Criar Tarifa",
        "✏️ Editar Tarifa",
        "🗑️ Excluir Tarifa"
    ])
    
    with tab1:
        show_current_tariff(token)
    with tab2:
        show_list_tariffs(token)
    with tab3:
        show_simulation(token)
    with tab4:
        show_create_tariff(token)
    with tab5:
        show_edit_tariff(token)
    with tab6:
        show_delete_tariff(token)

    pass  # O código tabs já executa as funções diretamente


if __name__ == "__main__":
    show()
