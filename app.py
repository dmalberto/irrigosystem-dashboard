import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv()
# Importações dos módulos
import src.controller_activations as controller_activations
import src.controllers as controllers
import src.consumptions as consumptions
import src.dashboard as dashboard
import src.health as health
import src.measurement_reports as measurement_reports
import src.measurements as measurements
import src.monitoring_stations as monitoring_stations
import src.tariff_schedules as tariff_schedules
import src.users as users
import src.valves as valves

# Design system
from src.design_tokens import DesignTokens, generate_button_styles
from src.ui_components import ComponentLibrary

# Exemplo da sua função de login/logout
from login import login, logout

# ---------- Configurações de Página ----------
st.set_page_config(
    page_title="IrrigoSystem – Monitoramento e Automação Sustentável",
    page_icon="💧",
    layout="wide",
)

# ---------- Paleta de Cores e Constantes ----------
PRIMARY_COLOR = "#5BAEDC"
SECONDARY_COLOR = "#FFFFFF"
TEXT_COLOR = "#212529"
MENU_BACKGROUND_COLOR = "#F7F7F7"
MENU_SELECTED_BACKGROUND_COLOR = "#5BAEDC"
MENU_HOVER_COLOR = "#D3D3D3"

# --- CSS Base para Header, Tagline, e Estilos Globais ---
CSS_BASE = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@700&family=Roboto:wght@400&display=swap');

/* RESET/BASE */
body, html, [class*="css"] {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

/* HEADER */
.header {{
  background-color: {PRIMARY_COLOR};
  color: {SECONDARY_COLOR};
  padding: 10px 15px;       /* Ajuste do padding */
  text-align: center;
  border-radius: 6px;
  margin-bottom: 15px;      /* Espaçamento do header para o resto */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  font-family: 'Lora', serif; 
  font-size: 24px;
}}

/* TAGLINE */
.tagline {{
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: {TEXT_COLOR};
  margin-top: -3px;
  margin-bottom: 20px; /* Espaçamento entre tagline e conteúdo */
  text-align: center;
  font-style: italic;
}}

/* CONTAINER DE LOGIN PERSONALIZADO */
.login-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 50px); /* Para centralizar verticalmente (aprox.) */
}}

.login-box {{
    background-color: #ffffff;
    padding: 20px 25px;
    border-radius: 8px;
    width: 350px;       /* Largura fixa da caixinha de login */
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}}

.login-title {{
    font-family: 'Lora', serif;
    font-size: 22px;
    margin-bottom: 15px;
    color: {PRIMARY_COLOR};
    text-align: center;
}}

.login-input > label {{
    font-family: 'Roboto', sans-serif;
    font-size: 14px;
    color: {TEXT_COLOR};
    margin-bottom: 5px;
    display: block;
}}

.login-button-container {{
    margin-top: 15px;
    text-align: center;
}}
</style>
"""


def main():
    # Injetar CSS básico
    st.markdown(CSS_BASE, unsafe_allow_html=True)

    # Chama a função de login (que verifica e atualiza session_state)
    login()

    # Se após chamar login() o usuário continua não autenticado, interrompe a execução
    if not st.session_state["authenticated"]:
        st.stop()

    # Se chegar aqui, significa que está autenticado!

    # ---------- HEADER E TAGLINE ----------
    st.markdown(
        """
        <div class="header">IrrigoSystem – Monitoramento e Automação Sustentável</div>
        <div class="tagline">Monitore, controle e otimize sua irrigação – em qualquer lugar, a qualquer momento.</div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown("## Status", unsafe_allow_html=True)
        health.show_health_in_sidebar()
        st.markdown("---")
        if st.button("Sair", key="logout", help="Clique para sair do sistema"):
            logout()

    # ---------- MENU DE NAVEGAÇÃO ----------

    # Menu horizontal original com todas as opções
    app_mode = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Medições",
            "Relatórios de Medições",
            "Controladores",
            "Válvulas",
            "Ativações de Bomba",
            "Estações de Monitoramento",
            "Consumos",
            "Tarifas",
            "Usuários",
        ],
        icons=[
            "house",
            "speedometer2",
            "file-earmark-bar-graph",
            "cpu",
            "water",
            "power",
            "broadcast",
            "bar-chart-line",
            "currency-dollar",
            "people",
        ],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "background-color": MENU_BACKGROUND_COLOR,
                "border-radius": "10px",
                "padding": "10px 0",
                "margin-bottom": "20px",
                "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
            },
            "nav-link": {
                "font-size": "14px",
                "font-weight": "500",
                "color": TEXT_COLOR,
                "border-radius": "8px",
                "padding": "8px 12px",
                "margin": "0 2px",
                "text-align": "center",
                "transition": "all 0.2s ease",
            },
            "nav-link:hover": {
                "background-color": MENU_HOVER_COLOR,
                "color": PRIMARY_COLOR,
            },
            "nav-link-selected": {
                "background-color": PRIMARY_COLOR,
                "color": SECONDARY_COLOR,
                "font-weight": "600",
            },
        },
    )
    st.markdown("---")

    # ---------- CARREGAMENTO DE PÁGINAS ----------

    # CSS global para componentes
    st.markdown(generate_button_styles(), unsafe_allow_html=True)

    if app_mode == "Dashboard":
        show_enhanced_dashboard()
    elif app_mode == "Medições":
        measurements.show()
    elif app_mode == "Relatórios de Medições":
        measurement_reports.show()
    elif app_mode == "Controladores":
        controllers.show()
    elif app_mode == "Válvulas":
        valves.show()
    elif app_mode == "Ativações de Bomba":
        controller_activations.show()
    elif app_mode == "Estações de Monitoramento":
        monitoring_stations.show()
    elif app_mode == "Consumos":
        consumptions.show()
    elif app_mode == "Tarifas":
        tariff_schedules.show()
    elif app_mode == "Usuários":
        users.show()


def fetch_home_data():
    """Busca dados do endpoint /api/home conforme Swagger"""
    token = st.session_state.get("token")
    if not token:
        return None
    
    from api import api_request
    response = api_request("GET", "/api/home", token=token)
    
    if response and response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta da API /api/home")
            return None
    elif response and response.status_code == 404:
        st.warning("Endpoint /api/home não está disponível na API atual.")
        return None
    else:
        st.error(f"Erro ao buscar dados do dashboard: HTTP {response.status_code if response else 'Sem conexão'}")
        return None


def show_enhanced_dashboard():
    """
    Dashboard melhorado com dados reais do endpoint /api/home
    """
    st.title("🏠 Dashboard - Visão Geral")

    # Buscar dados do endpoint /api/home
    with st.spinner("Carregando dados do dashboard..."):
        home_data = fetch_home_data()
    
    if home_data:
        # Extrair dados conforme schema HomeResponse
        monitoring_stations = home_data.get("monitoringStations", []) or []
        controllers = home_data.get("controllers", []) or []
        gateway_status = home_data.get("gateway", False)
        
        # Calcular métricas
        total_stations = len(monitoring_stations)
        active_stations = len([s for s in monitoring_stations if s.get("status", False)])
        total_controllers = len(controllers)
        online_controllers = len([c for c in controllers if c.get("status", False)])
        total_valves_on = sum(c.get("numberOfValvesOn", 0) for c in controllers)
        
        # Cards de métricas principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ComponentLibrary.metric_card(
                title="Estações de Monitoramento",
                value=f"{active_stations}/{total_stations}",
                delta="Online" if active_stations > 0 else "Offline",
                delta_color="normal" if active_stations > 0 else "inverse",
                icon="🏭"
            )

        with col2:
            controller_percentage = (online_controllers / total_controllers * 100) if total_controllers > 0 else 0
            ComponentLibrary.metric_card(
                title="Controladores Online",
                value=f"{controller_percentage:.0f}%",
                delta=f"{online_controllers}/{total_controllers}",
                delta_color="normal",
                icon="⚙️",
            )

        with col3:
            ComponentLibrary.metric_card(
                title="Válvulas Ativas",
                value=str(total_valves_on),
                delta="No momento",
                delta_color="normal",
                icon="💧",
            )

        with col4:
            ComponentLibrary.metric_card(
                title="Gateway",
                value="Online" if gateway_status else "Offline",
                delta="Conectado" if gateway_status else "Desconectado",
                delta_color="normal" if gateway_status else "inverse",
                icon="📡",
            )

        # Status do sistema detalhado
        st.markdown("---")
        
        # Cards de estações de monitoramento
        if monitoring_stations:
            ComponentLibrary.card(
                title="🏭 Estações de Monitoramento",
                content=f"Exibindo {len(monitoring_stations)} estação(ões) no sistema:",
                color="info"
            )
            
            # Criar colunas para as estações (máx 3 por linha)
            for i in range(0, len(monitoring_stations), 3):
                cols = st.columns(3)
                for j, station in enumerate(monitoring_stations[i:i+3]):
                    if j < len(cols):
                        with cols[j]:
                            status_color = "success" if station.get("status", False) else "error"
                            status_text = "✅ Online" if station.get("status", False) else "❌ Offline"
                            avg_moisture = station.get("averageMoisture", 0)
                            moisture_limit = station.get("moistureLimit", "N/A")
                            
                            station_name = station.get('name') or f"Estação {station.get('id', 'N/A')}"
                            ComponentLibrary.card(
                                title=f"📍 {station_name}",
                                content=f"""
                                **Status:** {status_text}
                                **Umidade Média:** {avg_moisture:.1f}%
                                **Limite:** {moisture_limit}
                                """,
                                color=status_color
                            )
        
        # Cards de controladores
        if controllers:
            ComponentLibrary.card(
                title="⚙️ Controladores",
                content=f"Exibindo {len(controllers)} controlador(es) no sistema:",
                color="info"
            )
            
            # Criar colunas para os controladores (máx 3 por linha)
            for i in range(0, len(controllers), 3):
                cols = st.columns(3)
                for j, controller in enumerate(controllers[i:i+3]):
                    if j < len(cols):
                        with cols[j]:
                            status_color = "success" if controller.get("status", False) else "error"
                            status_text = "✅ Online" if controller.get("status", False) else "❌ Offline"
                            valves_on = controller.get("numberOfValvesOn", 0)
                            
                            controller_name = controller.get('name') or f"Controlador {controller.get('id', 'N/A')}"
                            ComponentLibrary.card(
                                title=f"🎛️ {controller_name}",
                                content=f"""
                                **Status:** {status_text}
                                **Válvulas Ativas:** {valves_on}
                                """,
                                color=status_color
                            )
        
        # Status geral do sistema
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ComponentLibrary.card(
                title="Sistema",
                content="✅ Operacional" if (active_stations > 0 or online_controllers > 0) else "⚠️ Verificar",
                color="success" if (active_stations > 0 or online_controllers > 0) else "warning"
            )

        with col2:
            ComponentLibrary.card(
                title="API",
                content="🟢 Conectada",
                color="success"
            )

        with col3:
            ComponentLibrary.card(
                title="Gateway",
                content="🟢 Online" if gateway_status else "🔴 Offline",
                color="success" if gateway_status else "error"
            )

        with col4:
            ComponentLibrary.card(
                title="Dados",
                content=f"📊 {total_stations + total_controllers} dispositivos",
                color="info"
            )
    
    else:
        # Fallback com dados estáticos se a API não estiver disponível
        st.info("🔄 Dados em tempo real não disponíveis. Exibindo informações do sistema.")
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ComponentLibrary.card(title="Sistema", content="✅ Online", color="success")

        with col2:
            ComponentLibrary.card(title="Interface", content="🟢 Funcionando", color="success")

        with col3:
            ComponentLibrary.card(title="Status", content="⚠️ API Limitada", color="warning")

        with col4:
            ComponentLibrary.card(title="Modo", content="📋 Configuração", color="info")


if __name__ == "__main__":
    main()
