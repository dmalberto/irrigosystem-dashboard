# src/measurements.py
"""
Medições dos Sensores - Modernizado com UI Foundations v3
Enhanced empty states, ComponentLibrary e design tokens aplicados.
"""

import io
from datetime import datetime, time

import pandas as pd
import streamlit as st

from api import api_request
from src.ui_components import (
    ComponentLibrary,
    LoadingStates,
    enhanced_empty_state
)


def format_datetime(date_value, time_value):
    """Formata data e hora em ISO8601 UTC Z"""
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def export_measurements_csv(token, start_date=None, end_date=None, station_id=None, sensor_id=None, sort="desc"):
    """
    GET /api/measurements/export
    Parâmetros conforme Swagger:
    - startDate (date-time, opcional): Data de início
    - endDate (date-time, opcional): Data de fim  
    - stationId (int32, opcional): ID da estação
    - sensorId (int32, opcional): ID do sensor
    - sort (string, opcional): Ordenação (default: desc)
    
    Retorna: Conteúdo CSV para download
    """
    endpoint = "/api/measurements/export"
    params = {"sort": sort}
    
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    if station_id:
        params["stationId"] = station_id
    if sensor_id:
        params["sensorId"] = sensor_id
    
    response = api_request("GET", endpoint, token=token, params=params)
    return response


def display_datetime(date_value, time_value):
    """Mostra data e hora em formato DD/MM/YYYY HH:MM:SS (ou 'Não especificado')."""
    if date_value:
        if time_value:
            return datetime.combine(date_value, time_value).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        return datetime.combine(date_value, time.min).strftime("%d/%m/%Y %H:%M:%S")
    return "Não especificado"


def rename_columns(df):
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "date": "Data",
            "sensorId": "ID do Sensor",
            "batteryVoltage": "Tensão da Bateria (V)",
            "boardTemperature": "Temperatura da Placa (°C)",
            "sensorTemperature": "Temperatura do Sensor (°C)",
            "sampleTemperature": "Temperatura da Amostra (°C)",
            "moisture": "Umidade",
            "salinity": "Salinidade (uS/cm)",
            "conductivity": "Condutividade",
        }
        df.rename(columns=columns_mapping, inplace=True)


def listar_estacoes():
    """GET /api/monitoring-stations

    Responses: 200 (Success), 500 (Server Error)
    Retorna lista de estações para alimentar seletor
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)

    if not response:
        st.error("Erro ao conectar com a API de estações.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON das estações.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar estações.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar estações: {response.status_code}")
        return []


def listar_sensores_por_estacao(station_id):
    """GET /api/monitoring-stations/{stationId}/sensors

    Parâmetro: stationId (int64) no path
    Responses: 200 (Success), 500 (Server Error)
    Retorna lista de sensores para alimentar seletor
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)

    if not response:
        st.error("Erro ao conectar com a API de sensores.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON dos sensores.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar sensores.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar sensores: {response.status_code}")
        return []


def selecionar_estacao():
    """Componente de seleção de estação usando seletor padronizado

    Retorna: (estacao_id, estacao_nome) ou (None, None) se nenhuma selecionada
    """
    estacoes = listar_estacoes()
    if not estacoes:
        ComponentLibrary.alert("Nenhuma estação cadastrada.", "warning")
        return None, None

    # Criar opções com nome + ID visível
    estacao_options = {
        f"{estacao['name']} (ID: {estacao['id']})": estacao["id"]
        for estacao in estacoes
    }
    estacao_nome = st.selectbox("Selecione a Estação *", estacao_options.keys(), key="measurements_station_select")
    estacao_id = estacao_options[estacao_nome]

    return estacao_id, estacao_nome


def selecionar_sensor(estacao_id):
    """Componente de seleção de sensor usando seletor padronizado

    Args:
        estacao_id: ID da estação selecionada

    Retorna: sensor_id ou None se nenhum selecionado
    """
    if not estacao_id:
        ComponentLibrary.alert(
            "Selecione uma estação primeiro para carregar os sensores.",
            "info"
        )
        return None

    sensores = listar_sensores_por_estacao(estacao_id)
    if not sensores:
        ComponentLibrary.alert("Nenhum sensor encontrado para esta estação.", "warning")
        return None

    # Criar opções com ID visível
    sensor_options = {"Todos os Sensores": None}
    sensor_options.update(
        {f"Sensor ID: {sensor['id']}": sensor["id"] for sensor in sensores}
    )

    sensor_choice = st.selectbox("Filtrar por Sensor (Opcional)", sensor_options.keys(), key="measurements_sensor_select")
    sensor_id = sensor_options[sensor_choice]

    return sensor_id


def obter_estacoes_cadastradas():
    """GET /api/monitoring-stations

    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    response = api_request("GET", "/api/monitoring-stations", token=token)

    if not response:
        st.error("Erro ao conectar com a API de estações.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON das estações.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar estações.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar estações: {response.status_code}")
        return []


def obter_sensores_por_estacao(station_id):
    """GET /api/monitoring-stations/{stationId}/sensors

    Parâmetro: stationId (int64) no path
    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return []

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)

    if not response:
        st.error("Erro ao conectar com a API de sensores.")
        return []

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta JSON dos sensores.")
            return []
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar sensores.")
        return []
    else:
        st.error(f"Erro inesperado ao buscar sensores: {response.status_code}")
        return []


def fetch_data(
    start_date=None,
    end_date=None,
    station_id=None,
    sensor_id=None,
    page=1,
    page_size=15,
    sort="desc",
):
    """
    GET /api/measurements

    Parâmetros conforme Swagger:
    - startDate (string, date-time)
    - endDate (string, date-time)
    - stationId (integer, int32)
    - sensorId (integer, int32)
    - page (integer, int32, default: 1)
    - pageSize (integer, int32, default: 15)
    - sort (string, default: desc)

    Responses: 200 (Success), 500 (Server Error)
    """
    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    endpoint = "/api/measurements"
    params = {}

    # Parâmetros conforme nomes exatos do Swagger
    if page is not None:
        params["page"] = page
        params["pageSize"] = page_size

    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    # stationId como int32 conforme Swagger
    if station_id:
        params["stationId"] = int(station_id)

    # sensorId como int32 conforme Swagger
    if sensor_id:
        params["sensorId"] = int(sensor_id)

    # sort parameter conforme Swagger
    if sort:
        params["sort"] = sort

    with st.spinner("Carregando dados..."):
        response = api_request("GET", endpoint, token=token, params=params)

    if not response:
        st.error("Erro ao conectar com a API de medições.")
        return pd.DataFrame()

    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data)
            if not df.empty and "date" in df.columns:
                df["date"] = (
                    pd.to_datetime(df["date"])
                    .dt.tz_localize("UTC")
                    .dt.tz_convert("America/Sao_Paulo")
                    .dt.strftime("%d/%m/%Y %H:%M:%S")
                )
            rename_columns(df)
            return df
        except ValueError:
            st.error("Erro ao processar resposta JSON da API.")
            return pd.DataFrame()
    elif response.status_code == 500:
        st.error("Erro interno do servidor ao buscar medições.")
        return pd.DataFrame()
    else:
        st.error(f"Erro inesperado ao buscar dados: {response.status_code}")
        return pd.DataFrame()


def load_more():
    """
    Carrega próxima página de dados de medições de sensores.

    Implementa paginação incremental concatenando novos dados aos existentes.

    Side Effects:
        - Incrementa st.session_state.page em 1
        - Modifica st.session_state.data via pd.concat() com ignore_index=True
        - Utiliza st.session_state.estacao_id para filtrar dados por estação
        - Utiliza st.session_state.sensor_id para filtrar por sensor específico

    Behavior:
        - Busca dados da próxima página usando fetch_data()
        - Concatena resultados aos dados já carregados
        - Mantém ordem cronológica através de ignore_index=True
    """
    st.session_state.page += 1
    df_new = fetch_data(
        page=st.session_state.page,
        station_id=st.session_state.estacao_id,
        sensor_id=st.session_state.sensor_id,
    )
    st.session_state.data = pd.concat(
        [st.session_state.data, df_new], ignore_index=True
    )


def export_to_excel(df, selected_columns):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df[selected_columns].to_excel(writer, index=False, sheet_name="Amostras")
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def show():
    st.title("📊 Medições dos Sensores")

    if "page" not in st.session_state:
        st.session_state.page = 1
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()
    if "filtered" not in st.session_state:
        st.session_state.filtered = False
    if "estacao_id" not in st.session_state:
        st.session_state.estacao_id = None
    if "previous_estacao_id" not in st.session_state:
        st.session_state.previous_estacao_id = None
    if "sensor_id" not in st.session_state:
        st.session_state.sensor_id = None

    # Seleção de estação usando seletor padronizado
    estacao_id, estacao_nome = selecionar_estacao()
    if estacao_id is None:
        enhanced_empty_state(
            title="Selecione uma Estação",
            description="Para visualizar as medições dos sensores, primeiro selecione uma estação de monitoramento.",
            icon="🏭",
            action_button={
                "label": "🔄 Atualizar Lista",
                "key": "refresh_stations_list"
            }
        )
        return
    st.session_state.estacao_id = estacao_id

    # Seleção de sensor usando seletor (depende da estação)
    sensor_id = selecionar_sensor(estacao_id)
    st.session_state.sensor_id = sensor_id

    # Resetar dados se a estação mudar
    if st.session_state.estacao_id != st.session_state.previous_estacao_id:
        st.session_state.page = 1
        st.session_state.data = pd.DataFrame()
        st.session_state.filtered = False
        st.session_state.previous_estacao_id = st.session_state.estacao_id

    # Filtro de datas
    # Filtros com melhor visual
    with st.expander("🗓️ Filtros de Data e Hora", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Período de Início**")
            start_date = st.date_input(
                "Data de Início", value=None, key="amostras_start_date"
            )
            start_time = st.time_input(
                "Hora de Início", value=None, key="amostras_start_time"
            )
        with col2:
            st.markdown("**Período de Fim**")
            end_date = st.date_input("Data de Fim", value=None, key="amostras_end_date")
            end_time = st.time_input("Hora de Fim", value=None, key="amostras_end_time")

        if st.button("🔍 Aplicar Filtros", type="primary"):
            # Valida se ambas as datas foram preenchidas
            if (start_date and end_date) and (start_date <= end_date):
                st.session_state.page = 1
                st.session_state.filtered = True
                start_date_str = format_datetime(start_date, start_time)
                end_date_str = format_datetime(end_date, end_time)
                
                with LoadingStates.spinner_with_cancel("Aplicando filtros..."):
                    st.session_state.data = fetch_data(
                        start_date=start_date_str,
                        end_date=end_date_str,
                        station_id=st.session_state.estacao_id,
                        sensor_id=sensor_id,
                        page=1,  # Reset para primeira página
                    )
                    
                ComponentLibrary.alert("Filtros aplicados com sucesso!", "success")
            else:
                ComponentLibrary.alert(
                    "Por favor, preencha corretamente a Data de Início e Data de Fim (Início <= Fim).",
                    "error"
                )

    # Se o usuário não aplicou filtros e não há dados carregados ainda, carregar a primeira página
    if st.session_state.page == 1 and st.session_state.data.empty:
        with st.spinner("Carregando medições iniciais..."):
            df = fetch_data(
                page=st.session_state.page,
                station_id=st.session_state.estacao_id,
                sensor_id=sensor_id,
            )
            
        st.session_state.data = df

    if not st.session_state.data.empty:
        # Cards informativos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ComponentLibrary.metric_card(
                title="Estação",
                value=estacao_nome.split(" (ID:")[0] if " (ID:" in estacao_nome else estacao_nome,
                icon="🏭"
            )
        
        with col2:
            total_measurements = len(st.session_state.data)
            ComponentLibrary.metric_card(
                title="Medições",
                value=str(total_measurements),
                description="registros carregados",
                icon="📊"
            )
        
        with col3:
            # Verificar se há dados recentes (menos de 24h)
            if "Data" in st.session_state.data.columns:
                latest_date = st.session_state.data["Data"].iloc[0] if len(st.session_state.data) > 0 else "N/A"
                ComponentLibrary.metric_card(
                    title="Última Medição",
                    value=str(latest_date)[:10] if latest_date != "N/A" else "N/A",
                    description="mais recente",
                    icon="🕓"
                )
        
        st.markdown("---")
        
        # Informações do período filtrado
        start_dt_display = display_datetime(
            st.session_state.get("amostras_start_date"),
            st.session_state.get("amostras_start_time"),
        )
        end_dt_display = display_datetime(
            st.session_state.get("amostras_end_date"),
            st.session_state.get("amostras_end_time"),
        )
        
        if ("Não especificado" not in start_dt_display) or ("Não especificado" not in end_dt_display):
            ComponentLibrary.card(
                title="🗓️ Período Filtrado",
                content=f"**De:** {start_dt_display}  \n**Até:** {end_dt_display}",
                color="info"
            )
        
        # Exibir dados
        st.markdown("### 📋 Dados das Medições")
        st.dataframe(st.session_state.data, use_container_width=True)

        # Botão para carregar mais dados com melhor visual
        if len(st.session_state.data) >= 15:  # Se há pelo menos uma página completa
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:  # Centralizar o botão
                if st.button("🔄 Carregar Mais Dados", type="secondary"):
                    with LoadingStates.spinner_with_cancel("Carregando mais dados..."):
                        load_more()
                    st.rerun()

        # Seção de exportação com melhor visual
        if not st.session_state.data.empty:
            st.markdown("---")
            
            with st.expander("📥 Exportar Dados", expanded=False):
                # Tabs para diferentes tipos de export
                export_tab1, export_tab2 = st.tabs(["📊 Excel (Local)", "🌐 CSV (API)"])
                
                with export_tab1:
                    st.markdown("**Exporte dados já carregados na tela para Excel:**")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        selected_columns = st.multiselect(
                            "Colunas para exportação",
                            st.session_state.data.columns.tolist(),
                            default=st.session_state.data.columns.tolist(),
                            help="Escolha quais colunas incluir no arquivo Excel",
                            key="excel_columns_multiselect"
                        )
                    
                    with col2:
                        st.markdown("**Resumo da Exportação:**")
                        st.info(f"📄 {len(st.session_state.data)} registros\n📊 {len(selected_columns) if selected_columns else 0} colunas")

                    if selected_columns:
                        excel_data = export_to_excel(st.session_state.data, selected_columns)
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name="medicoes_sensores.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            help="Clique para baixar os dados selecionados em formato Excel"
                        )
                    else:
                        ComponentLibrary.alert("Selecione pelo menos uma coluna para exportar.", "warning")
                
                with export_tab2:
                    st.markdown("**Export completo via API conforme filtros aplicados:**")
                    
                    # Mostrar parâmetros que serão usados no export
                    export_params = {}
                    if "amostras_start_date_str" in st.session_state and st.session_state["amostras_start_date_str"]:
                        export_params["startDate"] = st.session_state["amostras_start_date_str"]
                    if "amostras_end_date_str" in st.session_state and st.session_state["amostras_end_date_str"]:
                        export_params["endDate"] = st.session_state["amostras_end_date_str"]
                    if "selected_station_id" in st.session_state and st.session_state["selected_station_id"]:
                        export_params["stationId"] = st.session_state["selected_station_id"]
                    if "selected_sensor_id" in st.session_state and st.session_state["selected_sensor_id"]:
                        export_params["sensorId"] = st.session_state["selected_sensor_id"]
                    
                    if export_params:
                        st.markdown("**Parâmetros do Export:**")
                        for key, value in export_params.items():
                            st.markdown(f"- **{key}:** {value}")
                    else:
                        st.info("Export incluirá todos os dados disponíveis (sem filtros)")
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        sort_order = st.selectbox(
                            "Ordenação", 
                            ["desc", "asc"], 
                            help="Ordenação dos dados no CSV",
                            key="csv_sort_selector"
                        )
                    
                    with col2:
                        if st.button("📥 Baixar CSV da API", type="primary", use_container_width=True):
                            with LoadingStates.spinner_with_cancel("Gerando export CSV..."):
                                response = export_measurements_csv(
                                    token=st.session_state.get("token"),
                                    start_date=export_params.get("startDate"),
                                    end_date=export_params.get("endDate"),
                                    station_id=export_params.get("stationId"),
                                    sensor_id=export_params.get("sensorId"),
                                    sort=sort_order
                                )
                            
                            if response and response.status_code == 200:
                                # CSV content - create download button
                                st.download_button(
                                    label="📥 Download Arquivo CSV",
                                    data=response.content,
                                    file_name=f"measurements_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    type="secondary",
                                    help="Arquivo CSV gerado pela API"
                                )
                                ComponentLibrary.alert("Export CSV gerado com sucesso!", "success")
                            elif response and response.status_code == 500:
                                ComponentLibrary.alert("Erro interno do servidor ao gerar CSV.", "error")
                            else:
                                error_msg = "Erro ao gerar export CSV."
                                if response:
                                    error_msg += f" Status: {response.status_code}"
                                ComponentLibrary.alert(error_msg, "error")

    else:
        enhanced_empty_state(
            title="Nenhuma Medição Encontrada",
            description="Não foram encontradas medições para a estação selecionada. Isso pode acontecer se:\n- A estação não possui sensores ativos\n- Não há dados no período filtrado\n- Os sensores ainda não enviaram medições",
            icon="📊",
            action_button={
                "label": "🔄 Tentar Novamente",
                "key": "retry_measurements"
            }
        )


if __name__ == "__main__":
    show()
