# src/controlador.py

from datetime import datetime, time

import pandas as pd
import plotly.express as px
import streamlit as st
from requests import request

from config import base_url


# Função para formatar data e hora
def format_datetime(date_value, time_value):
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        return None


# Função para buscar status dos controladores da API
def fetch_controller_statuses(controller_id, start_date=None, end_date=None):
    url = f"{base_url}/api/controllers/{controller_id}/statuses?pageSize=10000"
    params = []

    if start_date:
        params.append(f"startDate={start_date}")
    if end_date:
        params.append(f"endDate={end_date}")

    if params:
        url += "&" + "&".join(params)

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()

    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        if not df.empty and "date" in df.columns:
            # Converte a data de UTC para UTC-3
            df["date"] = (
                pd.to_datetime(df["date"])
                .dt.tz_localize("UTC")
                .dt.tz_convert("America/Sao_Paulo")
            )
        return df
    else:
        st.error("Falha ao obter status do controlador.")
        return pd.DataFrame()


# Função para obter a lista de controladores
def obter_lista_controladores():
    url = f"{base_url}/api/controllers"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return []
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        controllers = response.json()
        return controllers
    else:
        st.error("Falha ao obter lista de controladores.")
        return []


# Função para criar um novo controlador
def criar_controlador(nome, potencia, eficiencia, fator_potencia):
    url = f"{base_url}/api/controllers"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "name": nome,
        "power": potencia,
        "efficiency": eficiencia,
        "powerFactor": fator_potencia,
    }
    response = request("POST", url, headers=headers, json=data)
    if response.status_code == 201:
        st.success("Controlador criado com sucesso!")
    else:
        st.error("Falha ao criar controlador.")


# Função para editar um controlador existente
def editar_controlador(controller_id, nome, potencia, eficiencia, fator_potencia):
    url = f"{base_url}/api/controllers/{controller_id}"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "name": nome,
        "power": potencia,
        "efficiency": eficiencia,
        "powerFactor": fator_potencia,
    }
    response = request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        st.success("Controlador atualizado com sucesso!")
    else:
        st.error("Falha ao atualizar controlador.")


# Função para excluir um controlador
def excluir_controlador(controller_id):
    url = f"{base_url}/api/controllers/{controller_id}"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    response = request("DELETE", url, headers=headers)
    if response.status_code == 204:
        st.success("Controlador excluído com sucesso!")
    else:
        st.error("Falha ao excluir controlador.")


# Função para renomear colunas
def rename_columns(df):
    if not df.empty:
        columns_mapping = {
            "id": "ID",
            "date": "Data",
            "operationMode": "Modo de Operação",
            "valve1": "Válvula 1",
            "valve2": "Válvula 2",
            "valve3": "Válvula 3",
            "valve4": "Válvula 4",
            "valve5": "Válvula 5",
            "power": "Potência (W)",
            "efficiency": "Eficiência (%)",
            "powerFactor": "Fator de Potência",
        }
        df.rename(columns=columns_mapping, inplace=True)


# Funções para Gerenciamento de Válvulas


# Função para buscar válvulas de um controlador
def fetch_valvulas(controller_id):
    url = f"{base_url}/api/controllers/{controller_id}/valves"
    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return pd.DataFrame()
    headers = {"Authorization": f"Bearer {token}"}
    response = request("GET", url, headers=headers)
    if response.status_code == 200:
        valves = response.json()
        valves_df = pd.DataFrame(valves)
        if not valves_df.empty and "flowRate" in valves_df.columns:
            valves_df["flowRate"] = valves_df["flowRate"].astype(float)
        return valves_df
    else:
        st.error("Falha ao obter válvulas do controlador.")
        return pd.DataFrame()


# Função para adicionar uma nova válvula
def adicionar_valvula(controller_id, valve_name, flow_rate):
    url = f"{base_url}/api/controllers/{controller_id}/valves"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": valve_name, "flowRate": flow_rate}
    response = request("POST", url, headers=headers, json=data)
    if response.status_code == 201:
        st.success("Válvula adicionada com sucesso!")
    else:
        st.error("Falha ao adicionar válvula.")


# Função para editar uma válvula existente
def editar_valvula(controller_id, valve_id, valve_name, flow_rate):
    url = f"{base_url}/api/controllers/{controller_id}/valves/{valve_id}"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": valve_name, "flowRate": flow_rate}
    response = request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        st.success("Válvula atualizada com sucesso!")
    else:
        st.error("Falha ao atualizar válvula.")


# Função para excluir uma válvula
def excluir_valvula(controller_id, valve_id):
    url = f"{base_url}/api/controllers/{controller_id}/valves/{valve_id}"
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    response = request("DELETE", url, headers=headers)
    if response.status_code == 204:
        st.success("Válvula excluída com sucesso!")
    else:
        st.error("Falha ao excluir válvula.")


# Função para exibir gerenciamento de válvulas
def gerenciamento_valvulas(controller_id):
    st.subheader("Gerenciamento de Válvulas")

    # Listar válvulas
    valves_df = fetch_valvulas(controller_id)
    if not valves_df.empty:
        valves_df_display = valves_df[["id", "name", "flowRate"]]
        valves_df_display.rename(
            columns={
                "id": "ID da Válvula",
                "name": "Nome da Válvula",
                "flowRate": "Taxa de Fluxo (L/min)",
            },
            inplace=True,
        )
        st.dataframe(valves_df_display)
    else:
        st.warning("Nenhuma válvula cadastrada para este controlador.")

    st.markdown("### Adicionar Nova Válvula")
    with st.form("Adicionar Válvula"):
        valve_name = st.text_input("Nome da Válvula")
        flow_rate = st.number_input("Taxa de Fluxo (L/min)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            if valve_name and flow_rate:
                adicionar_valvula(controller_id, valve_name, flow_rate)
                st.experimental_rerun()
            else:
                st.error("Por favor, preencha todos os campos.")

    if not valves_df.empty:
        st.markdown("### Editar ou Excluir Válvula")
        selected_valve = st.selectbox("Selecione a Válvula", valves_df["id"])
        action = st.radio("Selecione a Ação", ["Editar", "Excluir"])

        if action == "Editar":
            valve_info = valves_df[valves_df["id"] == selected_valve].iloc[0]
            with st.form("Editar Válvula"):
                new_valve_name = st.text_input(
                    "Nome da Válvula", value=valve_info["name"]
                )
                new_flow_rate = st.number_input(
                    "Taxa de Fluxo (L/min)",
                    value=float(valve_info["flowRate"]),
                    min_value=0.0,
                    step=0.1,
                )
                submitted = st.form_submit_button("Atualizar")
                if submitted:
                    editar_valvula(
                        controller_id, selected_valve, new_valve_name, new_flow_rate
                    )
                    st.experimental_rerun()

        elif action == "Excluir":
            if st.button("Confirmar Exclusão"):
                excluir_valvula(controller_id, selected_valve)
                st.experimental_rerun()


# Função para exibir dados do controlador
def show():
    st.title("Gerenciamento de Controladores")

    # Listar todos os controladores
    st.subheader("Listagem de Controladores")

    controllers = obter_lista_controladores()
    if controllers:
        controllers_df = pd.DataFrame(controllers)
        rename_columns(controllers_df)
        st.dataframe(
            controllers_df[
                ["ID", "name", "Potência (W)", "Eficiência (%)", "Fator de Potência"]
            ]
        )

        # Botões de ação: Editar e Excluir
        st.markdown("### Ações nos Controladores")
        selected_controller = st.selectbox(
            "Selecione o Controlador para Ação", controllers_df["ID"]
        )
        action = st.radio("Selecione a Ação", ["Editar", "Excluir"])

        if action == "Editar":
            with st.form("Editar Controlador"):
                controller = controllers_df[
                    controllers_df["ID"] == selected_controller
                ].iloc[0]
                nome = st.text_input("Nome do Controlador", value=controller["name"])
                potencia = st.number_input(
                    "Potência (W)", value=float(controller["Potência (W)"])
                )
                eficiencia = st.number_input(
                    "Eficiência (%)", value=float(controller["Eficiência (%)"])
                )
                fator_potencia = st.number_input(
                    "Fator de Potência", value=float(controller["Fator de Potência"])
                )
                submitted = st.form_submit_button("Atualizar")
                if submitted:
                    editar_controlador(
                        selected_controller, nome, potencia, eficiencia, fator_potencia
                    )
                    st.experimental_rerun()

        elif action == "Excluir":
            if st.button("Confirmar Exclusão"):
                excluir_controlador(selected_controller)
                st.experimental_rerun()

    else:
        st.warning("Nenhum controlador cadastrado.")

    st.markdown("---")

    # Adicionar novo controlador
    st.subheader("Adicionar Novo Controlador")
    with st.form("Adicionar Controlador"):
        nome = st.text_input("Nome do Controlador")
        potencia = st.number_input("Potência (W)", min_value=0.0, step=1.0)
        eficiencia = st.number_input(
            "Eficiência (%)", min_value=0.0, max_value=100.0, step=0.1
        )
        fator_potencia = st.number_input(
            "Fator de Potência", min_value=0.0, max_value=1.0, step=0.01
        )
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            if nome and potencia and eficiencia and fator_potencia:
                criar_controlador(nome, potencia, eficiencia, fator_potencia)
                st.experimental_rerun()
            else:
                st.error("Por favor, preencha todos os campos.")

    st.markdown("---")

    # Selecionar controlador para visualizar detalhes e status
    st.subheader("Detalhes e Status do Controlador")
    controlador_id = st.selectbox(
        "Selecione o Controlador para Visualizar",
        controllers_df["ID"] if controllers else [],
    )

    if controlador_id:
        # Obter detalhes do controlador
        controller = next(
            (item for item in controllers if item["id"] == controlador_id), None
        )
        if controller:
            st.markdown(f"**Nome:** {controller['name']}")
            st.markdown(f"**Potência (W):** {controller['power']}")
            st.markdown(f"**Eficiência (%):** {controller['efficiency']}")
            st.markdown(f"**Fator de Potência:** {controller['powerFactor']}")

            # Gerenciamento de Válvulas
            gerenciamento_valvulas(controlador_id)

            # Filtros de data e hora
            with st.expander("Filtrar por data e hora"):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Data de Início", value=None, key="ctrl_start_date"
                    )
                    start_time = st.time_input(
                        "Hora de Início", value=None, key="ctrl_start_time"
                    )
                with col2:
                    end_date = st.date_input(
                        "Data de Fim", value=None, key="ctrl_end_date"
                    )
                    end_time = st.time_input(
                        "Hora de Fim", value=None, key="ctrl_end_time"
                    )

            start_date_str = format_datetime(start_date, start_time)
            end_date_str = format_datetime(end_date, end_time)

            df = fetch_controller_statuses(
                controlador_id,
                start_date=start_date_str,
                end_date=end_date_str,
            )

            if not df.empty:
                # Exibir cabeçalho com as informações dos filtros aplicados
                start_dt_display = (
                    f"{start_date.strftime('%d/%m/%Y')} {start_time.strftime('%H:%M:%S')}"
                    if start_date and start_time
                    else "Não especificado"
                )
                end_dt_display = (
                    f"{end_date.strftime('%d/%m/%Y')} {end_time.strftime('%H:%M:%S')}"
                    if end_date and end_time
                    else "Não especificado"
                )
                st.markdown(f"**Período:** {start_dt_display} **até** {end_dt_display}")

                st.dataframe(df)

                # Processar dados para gráficos
                df.sort_values("date", inplace=True)

                # Gráfico do estado da bomba (operationMode)
                if "operationMode" in df.columns:
                    fig = px.scatter(
                        df,
                        x="date",
                        y="operationMode",
                        title="Modo de Operação da Bomba",
                        labels={"operationMode": "Modo de Operação"},
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Gráficos dos estados das válvulas
                for valve in ["valve1", "valve2", "valve3", "valve4", "valve5"]:
                    if valve in df.columns:
                        df[valve + "_status"] = df[valve].apply(
                            lambda x: x["status"] if pd.notnull(x) else None
                        )
                        fig = px.line(
                            df,
                            x="date",
                            y=valve + "_status",
                            title=f"Status da {valve}",
                            markers=True,
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Nenhum dado disponível para os filtros selecionados.")


if __name__ == "__main__":
    show()
