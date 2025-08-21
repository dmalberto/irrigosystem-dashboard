from datetime import date, datetime, time, timedelta

import pandas as pd
import streamlit as st

from api import api_request


def format_datetime(date_value, time_value):
    """Converte (date, time) do Streamlit em string ISO8601, ex: '2025-01-08T07:31:20'."""
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.isoformat()
    return None


def display_datetime(date_value, time_value):
    """Formata data e hora para exibição (DD/MM/YYYY HH:MM:SS)."""
    if date_value:
        if time_value:
            return datetime.combine(date_value, time_value).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        return datetime.combine(date_value, time.min).strftime("%d/%m/%Y %H:%M:%S")
    return "Não especificado"


def fetch_controllers(token):
    """
    GET /api/controllers: retorna lista de controladores
    Ex.: [{"id":2, "pumpPower":..., ...}, ...]
    """
    endpoint = "/api/controllers"
    response = api_request("GET", endpoint, token=token)
    if not response or response.status_code != 200:
        st.error("Falha ao obter lista de controladores.")
        return []
    return response.json() if isinstance(response.json(), list) else []


def fetch_statuses(token, controller_id, page=1, start_date=None, end_date=None):
    """
    GET /api/controllers/{controllerId}/statuses
    Parametros fixos de paginação: pageSize=15, sort=desc
    Recebe 'page' e datas para filtrar
    """
    endpoint = f"/api/controllers/{controller_id}/statuses"
    params = {"page": page, "pageSize": 15, "sort": "desc"}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    response = api_request("GET", endpoint, token=token, params=params)
    return response


def load_more_statuses():
    """
    Incrementa a página e faz nova requisição, concatenando
    os dados em st.session_state.act_data
    """
    st.session_state.act_page += 1

    resp = fetch_statuses(
        token=st.session_state["token"],
        controller_id=st.session_state["act_controller_id"],
        page=st.session_state["act_page"],
        start_date=st.session_state.get("act_start_date_str"),
        end_date=st.session_state.get("act_end_date_str"),
    )
    if resp and resp.status_code == 200:
        df_new = pd.DataFrame(resp.json())
        if not df_new.empty:
            st.session_state.act_data = pd.concat(
                [st.session_state.act_data, df_new], ignore_index=True
            )
    else:
        st.warning("Não foi possível carregar mais dados.")


def show():
    st.title("Ativações (Statuses do Controlador)")

    token = st.session_state.get("token", None)
    if not token:
        st.error("Usuário não autenticado.")
        return

    # -----------------------------------------------------------------
    # Inicializa variáveis de estado, caso não existam
    # -----------------------------------------------------------------
    if "act_page" not in st.session_state:
        st.session_state.act_page = 1

    if "act_data" not in st.session_state:
        st.session_state.act_data = pd.DataFrame()

    if "act_controller_id" not in st.session_state:
        st.session_state.act_controller_id = None

    if "act_previous_controller_id" not in st.session_state:
        st.session_state.act_previous_controller_id = None

    if "act_start_date_str" not in st.session_state:
        st.session_state.act_start_date_str = None

    if "act_end_date_str" not in st.session_state:
        st.session_state.act_end_date_str = None

    # -----------------------------------------------------------------
    # Obtem lista de controladores p/ selectbox
    # -----------------------------------------------------------------
    controllers = fetch_controllers(token)
    if not controllers:
        st.warning("Nenhum controlador cadastrado ou falha ao obter lista.")
        return

    controllers_dict = {
        f"Controlador #{c['id']}": c["id"] for c in controllers if "id" in c
    }
    selected_label = st.selectbox(
        "Selecione o Controlador", list(controllers_dict.keys())
    )
    controller_id = controllers_dict[selected_label]

    # Se o controlador mudou, resetar paginação/dados
    if controller_id != st.session_state.act_previous_controller_id:
        st.session_state.act_page = 1
        st.session_state.act_data = pd.DataFrame()
        st.session_state.act_controller_id = controller_id
        st.session_state.act_previous_controller_id = controller_id

    # -----------------------------------------------------------------
    # Filtros de data
    # Vamos usar o mesmo padrão: fim = hoje, início = hoje-30 dias
    # -----------------------------------------------------------------
    end_date_default = date.today()
    start_date_default = end_date_default - timedelta(days=30)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data de Início", value=start_date_default)
    with col2:
        end_date = st.date_input("Data de Fim", value=end_date_default)

    # Checkbox para filtrar horário
    filtrar_por_horario = st.checkbox("Deseja filtrar por horário?", value=False)

    if filtrar_por_horario:
        col3, col4 = st.columns(2)
        with col3:
            start_time = st.time_input("Hora de Início", value=time(0, 0, 0))
        with col4:
            end_time = st.time_input("Hora de Fim", value=time(23, 59, 59))
    else:
        start_time = time(0, 0, 0)
        end_time = time(23, 59, 59)

    # -----------------------------------------------------------------
    # Botão para aplicar filtros e resetar paginação
    # -----------------------------------------------------------------
    if st.button("Aplicar Filtros"):
        if start_date > end_date:
            st.error("Data de início maior que a data de fim.")
            return
        start_date_str = format_datetime(start_date, start_time)
        end_date_str = format_datetime(end_date, end_time)

        # Salva no session_state
        st.session_state.act_start_date_str = start_date_str
        st.session_state.act_end_date_str = end_date_str

        # Resetar paginação e dados
        st.session_state.act_page = 1
        st.session_state.act_data = pd.DataFrame()

        # Faz a primeira busca
        with st.spinner("Carregando dados..."):
            resp = fetch_statuses(
                token,
                controller_id,
                st.session_state.act_page,
                start_date_str,
                end_date_str,
            )

        if resp and resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            st.session_state.act_data = df
        else:
            st.warning("Nenhum dado disponível ou falha na requisição.")

    # -----------------------------------------------------------------
    # Se temos act_data vazio e nenhuma requisição feita, busca inicial
    # (caso o usuário não clique no botão 'Aplicar Filtros')
    # -----------------------------------------------------------------
    if st.session_state.act_page == 1 and st.session_state.act_data.empty:
        # Carregamos sem filtros customizados, usando start_date/end_date default
        # (ou seja, se o user não clicou em filtrar, mas a gente assume 30 dias)
        if start_date > end_date:
            st.error("Data de início maior que a data de fim.")
            return
        st.session_state.act_start_date_str = format_datetime(start_date, start_time)
        st.session_state.act_end_date_str = format_datetime(end_date, end_time)

        with st.spinner("Carregando dados iniciais..."):
            resp = fetch_statuses(
                token,
                controller_id,
                st.session_state.act_page,
                st.session_state.act_start_date_str,
                st.session_state.act_end_date_str,
            )
        if resp and resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            st.session_state.act_data = df
        else:
            st.warning("Nenhum dado disponível ou falha na requisição.")

    # -----------------------------------------------------------------
    # Exibição da tabela e botão "Carregar mais"
    # -----------------------------------------------------------------
    if not st.session_state.act_data.empty:
        # Exibir cabeçalho com infos
        start_disp = display_datetime(start_date, start_time)
        end_disp = display_datetime(end_date, end_time)
        st.markdown(f"**Controlador Selecionado**: {controller_id}")
        if ("Não especificado" not in start_disp) or (
            "Não especificado" not in end_disp
        ):
            st.markdown(f"**Período:** {start_disp} até {end_disp}")

        st.table(st.session_state.act_data)

        # "Carregar mais" só aparece se já houve alguma busca
        if st.button("Carregar mais"):
            load_more_statuses()
            # Força o rerun
            st.rerun()

        # Inserir um "anchor" para autoscroll no final da página
        # Esse hack faz a tela rolar para o final após o rerun
        st.markdown("<div id='bottom_of_table'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <script>
                var bottom = document.getElementById('bottom_of_table');
                if (bottom) { bottom.scrollIntoView(); }
            </script>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Nenhum dado disponível para os filtros selecionados.")


if __name__ == "__main__":
    show()
