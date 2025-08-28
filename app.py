
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
import src.energy_consumptions as energy_consumptions
import src.water_consumptions as water_consumptions  # Assumindo que existe este módulo

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
  padding: 10px 15px;
  text-align: center;
  border-radius: 6px;
  margin-bottom: 15px;
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
  margin-bottom: 20px;
  text-align: center;
  font-style: italic;
}}

/* CONTAINER DE LOGIN PERSONALIZADO */
.login-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 50px);
}}

.login-box {{
    background-color: #ffffff;
    padding: 20px 25px;
    border-radius: 8px;
    width: 350px;
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

/* SUBMENU STYLES */
.submenu-container {{
    background-color: #f0f0f0;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}}

.submenu-title {{
    font-family: 'Roboto', sans-serif;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 8px;
    color: {PRIMARY_COLOR};
}}

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    height: 40px;
    white-space: pre-wrap;
    background-color: white;
    border-radius: 4px;
    color: {TEXT_COLOR};
    font-size: 14px;
}}

.stTabs [aria-selected="true"] {{
    background-color: {PRIMARY_COLOR} !important;
    color: white !important;
}}
</style>
"""
def get_dashboard_custom_css():
    return """
    <style>
    /* Estilização para os expansores do dashboard */
    .streamlit-expanderHeader {
        background-color: #f0f7ff;
        border-radius: 5px;
        padding: 10px 15px;
        font-weight: 600;
        color: #1E88E5;
    }
    
    /* Conteúdo do expansor */
    .streamlit-expanderContent {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: none;
        border-radius: 0 0 5px 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
    """

def main():
    st.markdown(get_dashboard_custom_css(), unsafe_allow_html=True)

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

    # ---------- MENU DE NAVEGAÇÃO REORGANIZADO ----------
    # Menu horizontal com a nova estrutura solicitada
    app_mode = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Relatórios de Medição",     
            "Relatórios de Ativação",
            "Consumos",
            "Cadastrar Equipamentos",
            "Tarifas",
            "Usuários",
        ],
        icons=[
            "house",              # Dashboard
            "speedometer2",       # Relatórios de Medição
            "power",              # Relatórios de Ativação
            "bar-chart-line",     # Consumos
            "tools",              # Cadastrar Equipamentos
            "currency-dollar",    # Tarifas
            "people",             # Usuários
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

    # ---------- GESTÃO DE SUBMENUS ----------
    # Inicializar ou obter o estado do submenu
    if "submenu_selection" not in st.session_state:
        st.session_state.submenu_selection = {
            "Relatórios de Medição": "Medições",
            "Cadastrar Equipamentos": "Estações de Monitoramento",
            "Consumos": "Consumo de Água",
            "Controladores": "Controladores"  # Para as abas de Controladores/Válvulas
        }

    # CSS global para componentes
    st.markdown(generate_button_styles(), unsafe_allow_html=True)

    # ---------- RENDERIZAÇÃO DE CONTEÚDO BASEADO NO MENU ----------
    if app_mode == "Dashboard":
        show_enhanced_dashboard()
        
    elif app_mode == "Relatórios de Medição":
        # Usar tabs para Medições e Relatórios pré-programados
        tab1, tab2 = st.tabs(["📈 Relatórios Pré-programados", "📊 Todas as medições"])
        
        with tab1:
            measurement_reports.show()
            
        with tab2:
            measurements.show()
            
    elif app_mode == "Relatórios de Ativação":
        controller_activations.show()
            
    elif app_mode == "Consumos":
        # Submenu para tipos de consumo
        tab1, tab2 = st.tabs(["💧 Consumo de Água", "⚡ Consumo de Energia"])
        
        with tab1:
            water_consumptions.show()  # Assumindo que esse módulo existe
            
        with tab2:
            energy_consumptions.show()
            
    elif app_mode == "Cadastrar Equipamentos":
        # Submenu para tipos de equipamentos
        submenu = st.container()
        with submenu:
            col1, col2 = st.columns([3, 9])
            with col1:
                st.markdown('<div class="submenu-title">🔧 Selecione o tipo de equipamento:</div>', unsafe_allow_html=True)
            with col2:
                # Botões para submenu
                cols = st.columns([1, 1, 2])
                with cols[0]:
                    if st.button("Estações", key="btn_estacoes", 
                                 use_container_width=True,
                                 type="primary" if st.session_state.submenu_selection["Cadastrar Equipamentos"] == "Estações de Monitoramento" else "secondary"):
                        st.session_state.submenu_selection["Cadastrar Equipamentos"] = "Estações de Monitoramento"
                        st.experimental_rerun()
                with cols[1]:
                    if st.button("Controladores", key="btn_controladores", 
                                 use_container_width=True,
                                 type="primary" if st.session_state.submenu_selection["Cadastrar Equipamentos"] == "Controladores" else "secondary"):
                        st.session_state.submenu_selection["Cadastrar Equipamentos"] = "Controladores"
                        st.experimental_rerun()
        
        # Renderizar o conteúdo baseado na seleção do submenu
        if st.session_state.submenu_selection["Cadastrar Equipamentos"] == "Estações de Monitoramento":
            monitoring_stations.show()
            
        elif st.session_state.submenu_selection["Cadastrar Equipamentos"] == "Controladores":
            # Tabs para Controladores e Válvulas
            tab1, tab2 = st.tabs(["⚙️ Controladores", "🚿 Válvulas"])
            
            with tab1:
                controllers.show()
                
            with tab2:
                valves.show()
            
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

def fetch_health_data():
    """Busca dados do endpoint /api/health"""
    token = st.session_state.get("token")
    if not token:
        return None
    
    from api import api_request
    response = api_request("GET", "/api/health", token=token)
    
    if response and response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Erro ao processar resposta da API /api/health")
            return None
    else:
        st.error(f"Erro ao buscar dados de saúde: HTTP {response.status_code if response else 'Sem conexão'}")
        return None


def show_enhanced_dashboard():
    """
    Dashboard com seções reordenadas e cores padronizadas:
    - Cards verdes para dispositivos online e informações disponíveis
    - Cards cinzas para dispositivos offline
    - Texto colorido para condições de umidade
    """
    st.title("🏠 Dashboard - Visão Geral")

    # Buscar dados do endpoint /api/home e /api/health
    with st.spinner("Carregando dados do dashboard..."):
        home_data = fetch_home_data()
        health_data = fetch_health_data()
    
    if home_data and health_data:
        # Extrair dados conforme schema HomeResponse
        monitoring_stations = home_data.get("monitoringStations", []) or []
        controllers = home_data.get("controllers", []) or []
        gateway_status = home_data.get("gateway", False)
        
        # Obter status do broker a partir do endpoint health
        broker_status = health_data.get("broker", False)
        
        # Calcular métricas
        total_stations = len(monitoring_stations)
        active_stations = len([s for s in monitoring_stations if s.get("status", False)])
        total_controllers = len(controllers)
        online_controllers = len([c for c in controllers if c.get("status", False)])
        total_valves_on = sum(c.get("numberOfValvesOn", 0) for c in controllers)
        
        # Calcular sensores totais e ativos usando dados do health_data
        total_sensors = 0
        active_sensors = 0
        
        # Criar um mapeamento de estações e seus sensores ativos a partir do health_data
        health_stations = health_data.get("monitoringStations", []) or []
        station_sensors_map = {}
        
        for station in health_stations:
            station_id = station.get("id")
            station_sensors = station.get("sensors", [])
            
            # Contar sensores totais e ativos para esta estação
            total_station_sensors = len(station_sensors)
            active_station_sensors = sum(1 for s in station_sensors if s.get("status", False))
            
            # Armazenar no mapeamento
            station_sensors_map[station_id] = {
                "total": total_station_sensors,
                "active": active_station_sensors
            }
            
            # Adicionar ao total geral de sensores
            total_sensors += total_station_sensors
            active_sensors += active_station_sensors
        
        # CSS para altura padronizada dos cards
        st.markdown("""
        <style>
        /* Ajuste para padronizar altura dos cards */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            min-height: 155px;
            display: flex;
            flex-direction: column;
        }
        
        /* Centraliza conteúdo verticalmente */
        .stMetric {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Cores padrão para status online/offline
        ONLINE_COLOR = "#28a745"  # Verde
        OFFLINE_COLOR = "#6c757d"  # Cinza
        ONLINE_BG = "rgba(40, 167, 69, 0.1)"  # Verde claro com transparência
        OFFLINE_BG = "rgba(108, 117, 125, 0.1)"  # Cinza claro com transparência
        
        # === 1. Seção de Estações de Monitoramento ===
        stations_container = st.container()
        with stations_container:
            with st.expander("🏭 Estações de Monitoramento", expanded=True):
                st.markdown(f"Exibindo {len(monitoring_stations)} estação(ões) no sistema:")
                
                # Criar colunas para as estações (máx 3 por linha)
                for i in range(0, len(monitoring_stations), 3):
                    cols = st.columns(3)
                    for j, station in enumerate(monitoring_stations[i:i+3]):
                        if j < len(cols):
                            with cols[j]:
                                # Configurar cor de status online/offline
                                station_status = station.get("status", False)
                                status_text = "✅ Online" if station_status else "❌ Offline"
                                
                                # Definir cor do card baseado no status
                                card_color = ONLINE_COLOR if station_status else OFFLINE_COLOR
                                card_bg = ONLINE_BG if station_status else OFFLINE_BG
                                
                                # Obter dados de sensores do mapeamento criado a partir do health_data
                                station_id = station.get("id")
                                sensor_info = station_sensors_map.get(station_id, {"total": 0, "active": 0})
                                total_station_sensors = sensor_info["total"]
                                active_station_sensors = sensor_info["active"]
                                
                                # Obter dados de umidade
                                avg_moisture = station.get("averageMoisture", 0)
                                moisture_limit = station.get("moistureLimit", "N/A")
                                
                                # Determinar condição e cor da umidade (apenas para o texto)
                                if moisture_limit == "above":
                                    moisture_condition = "Umidade baixa"
                                    moisture_color = "#dc3545"  # Vermelho
                                elif moisture_limit == "between":
                                    moisture_condition = "Umidade normal"
                                    moisture_color = "#0d6efd"  # Azul
                                elif moisture_limit == "over":
                                    moisture_condition = "Umidade alta"
                                    moisture_color = "#6f42c1"  # Roxo
                                else:
                                    moisture_condition = "Umidade não definida"
                                    moisture_color = "#6c757d"  # Cinza
                                
                                station_name = station.get('name') or f"Estação {station.get('id', 'N/A')}"
                                
                                # Usando st.markdown com HTML para criar um card com estilo próprio
                                st.markdown(f"""
                                <div style="border: 1px solid {card_color}; 
                                           border-radius: 5px; 
                                           padding: 10px; 
                                           margin-bottom: 10px;
                                           background-color: {card_bg};">
                                    <h4 style="margin-top: 0; color: {card_color};">
                                        📍 {station_name}
                                    </h4>
                                    <p style="margin-bottom: 5px;"><strong>Status:</strong> {status_text}</p>
                                    <p style="margin-bottom: 5px;"><strong>Sensores:</strong> {active_station_sensors}/{total_station_sensors} ativos</p>
                                    <p style="margin-bottom: 5px;"><strong>Umidade Média:</strong> {avg_moisture:.1f}%</p>
                                    <p style="margin-bottom: 0;"><strong>Condição:</strong> <span style="color: {moisture_color}; font-weight: bold;">{moisture_condition}</span></p>
                                </div>
                                """, unsafe_allow_html=True)
        
        # === 2. Seção de Controladores ===
        controllers_container = st.container()
        with controllers_container:
            with st.expander("⚙️ Controladores", expanded=True):
                st.markdown(f"Exibindo {len(controllers)} controlador(es) no sistema:")
                
                # Criar colunas para os controladores (máx 3 por linha)
                for i in range(0, len(controllers), 3):
                    cols = st.columns(3)
                    for j, controller in enumerate(controllers[i:i+3]):
                        if j < len(cols):
                            with cols[j]:
                                controller_status = controller.get("status", False)
                                status_text = "✅ Online" if controller_status else "❌ Offline"
                                valves_on = controller.get("numberOfValvesOn", 0)
                                
                                # Definir cor do card baseado no status
                                card_color = ONLINE_COLOR if controller_status else OFFLINE_COLOR
                                card_bg = ONLINE_BG if controller_status else OFFLINE_BG
                                
                                controller_name = controller.get('name') or f"Controlador {controller.get('id', 'N/A')}"
                                
                                # Usando st.markdown com HTML para criar um card com estilo próprio
                                st.markdown(f"""
                                <div style="border: 1px solid {card_color}; 
                                           border-radius: 5px; 
                                           padding: 10px; 
                                           margin-bottom: 10px;
                                           background-color: {card_bg}">
                                    <h4 style="margin-top: 0; color: {card_color}">
                                        🎛️ {controller_name}
                                    </h4>
                                    <p style="margin-bottom: 5px;"><strong>Status:</strong> {status_text}</p>
                                    <p style="margin-bottom: 0;"><strong>Válvulas Ativas:</strong> {valves_on}</p>
                                </div>
                                """, unsafe_allow_html=True)
        
        # === 3. Seção de Métricas Principais ===
        metrics_container = st.container()
        with metrics_container:
            with st.expander("📊 Métricas Principais", expanded=True):
                # Cards de métricas principais com HTML
                col1, col2, col3, col4 = st.columns(4)

                # 1. Estações de Monitoramento
                with col1:
                    delta_color = ONLINE_COLOR if active_stations > 0 else OFFLINE_COLOR
                    delta_bg = ONLINE_BG if active_stations > 0 else OFFLINE_BG
                    delta_text = "Online" if active_stations > 0 else "Offline"
                    st.markdown(f"""
                    <div style="border: 1px solid {delta_color}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {delta_bg}">
                        <h4 style="margin-top: 0; color: {delta_color}">
                            🏭 Estações de Monitoramento
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {active_stations}/{total_stations} {delta_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # 2. Sensores
                with col2:
                    delta_color = ONLINE_COLOR if active_sensors > 0 else OFFLINE_COLOR
                    delta_bg = ONLINE_BG if active_sensors > 0 else OFFLINE_BG
                    delta_text = "Ativos" if active_sensors > 0 else "Inativos"
                    st.markdown(f"""
                    <div style="border: 1px solid {delta_color}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {delta_bg}">
                        <h4 style="margin-top: 0; color: {delta_color}">
                            📡 Sensores
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {active_sensors}/{total_sensors} {delta_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # 3. Controladores
                with col3:
                    delta_color = ONLINE_COLOR if online_controllers > 0 else OFFLINE_COLOR
                    delta_bg = ONLINE_BG if online_controllers > 0 else OFFLINE_BG
                    delta_text = "Online" if online_controllers > 0 else "Offline"
                    st.markdown(f"""
                    <div style="border: 1px solid {delta_color}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {delta_bg}">
                        <h4 style="margin-top: 0; color: {delta_color}">
                            ⚙️ Controladores
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {online_controllers}/{total_controllers} {delta_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # 4. Válvulas Ativas
                with col4:
                    # Válvulas ativas sempre em verde
                    st.markdown(f"""
                    <div style="border: 1px solid {ONLINE_COLOR}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {ONLINE_BG}">
                        <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                            💧 Válvulas Ativas
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {total_valves_on} No momento
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # === 4. Seção de Status do Sistema ===
        status_container = st.container()
        with status_container:
            with st.expander("🖥️ Status do Sistema", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                # Gateway Status
                with col1:
                    gateway_color = ONLINE_COLOR if gateway_status else OFFLINE_COLOR
                    gateway_bg = ONLINE_BG if gateway_status else OFFLINE_BG
                    st.markdown(f"""
                    <div style="border: 1px solid {gateway_color}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {gateway_bg}">
                        <h4 style="margin-top: 0; color: {gateway_color}">
                            Gateway
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {"✅ Online" if gateway_status else "❌ Offline"}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # API - Sempre online
                with col2:
                    st.markdown(f"""
                    <div style="border: 1px solid {ONLINE_COLOR}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {ONLINE_BG}">
                        <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                            API
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            🟢 Conectada
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Broker
                with col3:
                    broker_color = ONLINE_COLOR if broker_status else OFFLINE_COLOR
                    broker_bg = ONLINE_BG if broker_status else OFFLINE_BG
                    st.markdown(f"""
                    <div style="border: 1px solid {broker_color}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {broker_bg}">
                        <h4 style="margin-top: 0; color: {broker_color}">
                            Broker
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            {"✅ Online" if broker_status else "❌ Offline"}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Dados - Considerado como sempre disponível (verde)
                with col4:
                    st.markdown(f"""
                    <div style="border: 1px solid {ONLINE_COLOR}; 
                               border-radius: 5px; 
                               padding: 10px; 
                               margin-bottom: 10px;
                               background-color: {ONLINE_BG}">
                        <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                            Dados
                        </h4>
                        <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                            📊 {total_stations + total_controllers} dispositivos
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Fallback com dados estáticos se a API não estiver disponível
        st.info("🔄 Dados em tempo real não disponíveis. Exibindo informações do sistema.")
        
        # Cores padrão para fallback
        ONLINE_COLOR = "#28a745"  # Verde
        OFFLINE_COLOR = "#6c757d"  # Cinza
        ONLINE_BG = "rgba(40, 167, 69, 0.1)"  # Verde claro com transparência
        OFFLINE_BG = "rgba(108, 117, 125, 0.1)"  # Cinza claro com transparência
        
        # === 1. Estações - Fallback ===
        with st.expander("🏭 Estações de Monitoramento", expanded=True):
            st.warning("Não foi possível carregar dados das estações.")
            
        # === 2. Controladores - Fallback ===
        with st.expander("⚙️ Controladores", expanded=True):
            st.warning("Não foi possível carregar dados dos controladores.")
            
        # === 3. Métricas Principais - Fallback ===
        with st.expander("📊 Métricas Principais", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            # 1. Estações de Monitoramento - Fallback
            with col1:
                st.markdown(f"""
                <div style="border: 1px solid {OFFLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {OFFLINE_BG}">
                    <h4 style="margin-top: 0; color: {OFFLINE_COLOR}">
                        🏭 Estações de Monitoramento
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        0/0 Offline
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # 2. Sensores - Fallback
            with col2:
                st.markdown(f"""
                <div style="border: 1px solid {OFFLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {OFFLINE_BG}">
                    <h4 style="margin-top: 0; color: {OFFLINE_COLOR}">
                        📡 Sensores
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        0/0 Inativos
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # 3. Controladores - Fallback
            with col3:
                st.markdown(f"""
                <div style="border: 1px solid {OFFLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {OFFLINE_BG}">
                    <h4 style="margin-top: 0; color: {OFFLINE_COLOR}">
                        ⚙️ Controladores
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        0/0 Offline
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # 4. Válvulas Ativas - Fallback
            with col4:
                st.markdown(f"""
                <div style="border: 1px solid {ONLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {ONLINE_BG}">
                    <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                        💧 Válvulas Ativas
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        0 No momento
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
        # === 4. Status do Sistema - Fallback ===
        with st.expander("🖥️ Status do Sistema", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div style="border: 1px solid {OFFLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {OFFLINE_BG}">
                    <h4 style="margin-top: 0; color: {OFFLINE_COLOR}">
                        Gateway
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        ❌ Offline
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="border: 1px solid {ONLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {ONLINE_BG}">
                    <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                        Interface
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        ✅ Funcionando
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="border: 1px solid {OFFLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {OFFLINE_BG}">
                    <h4 style="margin-top: 0; color: {OFFLINE_COLOR}">
                        Broker
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        ❌ Offline
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div style="border: 1px solid {ONLINE_COLOR}; 
                           border-radius: 5px; 
                           padding: 10px; 
                           margin-bottom: 10px;
                           background-color: {ONLINE_BG}">
                    <h4 style="margin-top: 0; color: {ONLINE_COLOR}">
                        Modo
                    </h4>
                    <p style="margin-bottom: 0; text-align: center; font-weight: bold;">
                        📋 Configuração
                    </p>
                </div>
                """, unsafe_allow_html=True)


# Função auxiliar para criar cards HTML (opcional, para reuso)
def create_html_card(title, content, color_key="info"):
    """
    Cria um card HTML personalizado com título e conteúdo dentro da mesma caixinha.
    
    Args:
        title: Título do card
        content: Conteúdo do card (pode ser HTML)
        color_key: Cor do card (success, danger, warning, info)
    """
    color_map = {
        "success": {"border": "#28a745", "bg": "rgba(40, 167, 69, 0.1)", "text": "#28a745"},
        "danger": {"border": "#dc3545", "bg": "rgba(220, 53, 69, 0.1)", "text": "#dc3545"},
        "warning": {"border": "#fd7e14", "bg": "rgba(253, 126, 20, 0.1)", "text": "#fd7e14"},
        "info": {"border": "#0dcaf0", "bg": "rgba(13, 202, 240, 0.1)", "text": "#0dcaf0"},
    }
    
    color = color_map.get(color_key, color_map["info"])
    
    return f"""
    <div style="border: 1px solid {color['border']}; 
               border-radius: 5px; 
               padding: 10px; 
               margin-bottom: 10px;
               background-color: {color['bg']}">
        <h4 style="margin-top: 0; color: {color['text']}">
            {title}
        </h4>
        <div style="margin-bottom: 0;">
            {content}
        </div>
    </div>
    """


if __name__ == "__main__":
    main()
