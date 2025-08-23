import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv()
# Importações dos módulos
import src.controller_activations as controller_activations
import src.controllers as controllers
import src.dashboard as dashboard
import src.energy_consumptions as energy_consumptions
import src.health as health
import src.measurement_reports as measurement_reports
import src.measurements as measurements
import src.monitoring_stations as monitoring_stations
import src.tariff_schedules as tariff_schedules
import src.users as users
import src.valves as valves
import src.water_consumptions as water_consumptions
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

    # ---------- SISTEMA DE NAVEGAÇÃO CATEGORIZADO ----------
    
    # Definir categorias e páginas
    MENU_CATEGORIES = {
        "📊 Monitoramento": {
            "icon": "bar-chart-line",
            "pages": ["Dashboard", "Medições", "Relatórios de Medições"],
            "modules": ["dashboard", "measurements", "measurement_reports"]
        },
        "🎮 Controle": {
            "icon": "sliders", 
            "pages": ["Controladores", "Válvulas", "Ativações de Bomba"],
            "modules": ["controllers", "valves", "controller_activations"]
        },
        "⚡ Consumo": {
            "icon": "lightning-charge",
            "pages": ["Consumo de Energia", "Consumo de Água"],
            "modules": ["energy_consumptions", "water_consumptions"]
        },
        "⚙️ Configuração": {
            "icon": "gear",
            "pages": ["Estações de Monitoramento", "Tarifas", "Usuários"],
            "modules": ["monitoring_stations", "tariff_schedules", "users"]
        }
    }
    
    # Navegação com tabs categorizadas  
    category_tabs = st.tabs(list(MENU_CATEGORIES.keys()))
    
    app_mode = None
    selected_module = None
    
    for i, (category, config) in enumerate(MENU_CATEGORIES.items()):
        with category_tabs[i]:
            # Menu horizontal dentro de cada categoria
            if config["pages"]:
                # Dashboard sempre primeiro na categoria Monitoramento
                default_idx = 0
                page_selected = option_menu(
                    menu_title=None,
                    options=config["pages"],
                    icons=["house" if page == "Dashboard" else config["icon"] for page in config["pages"]],
                    default_index=default_idx,
                    orientation="horizontal",
                    styles={
                        "container": {
                            "background-color": DesignTokens.COLORS["background"]["secondary"],
                            "border-radius": DesignTokens.RADIUS["lg"],
                            "padding": DesignTokens.SPACING["3"],
                            "margin-bottom": DesignTokens.SPACING["4"],
                            "box-shadow": DesignTokens.SHADOWS["base"],
                        },
                        "nav-link": {
                            "font-family": DesignTokens.TYPOGRAPHY["font_families"]["primary"],
                            "font-size": DesignTokens.TYPOGRAPHY["sizes"]["sm"],
                            "font-weight": DesignTokens.TYPOGRAPHY["weights"]["medium"],
                            "color": DesignTokens.COLORS["text"]["primary"],
                            "border-radius": DesignTokens.RADIUS["md"],
                            "padding": f"{DesignTokens.SPACING['3']} {DesignTokens.SPACING['4']}",
                            "margin": DesignTokens.SPACING["1"],
                            "text-align": "center",
                            "transition": "all 0.2s ease",
                        },
                        "nav-link:hover": {
                            "background-color": DesignTokens.COLORS["primary"] + "20",
                            "color": DesignTokens.COLORS["primary"],
                        },
                        "nav-link-selected": {
                            "background-color": DesignTokens.COLORS["primary"],
                            "color": DesignTokens.COLORS["text"]["inverse"],
                            "font-weight": DesignTokens.TYPOGRAPHY["weights"]["semibold"],
                        }
                    }
                )
                
                # Mapear página selecionada para módulo
                if page_selected in config["pages"]:
                    page_idx = config["pages"].index(page_selected)
                    app_mode = page_selected
                    selected_module = config["modules"][page_idx]
                    break
    st.markdown("---")

    # ---------- CARREGAMENTO DE PÁGINAS ----------
    
    # CSS global para componentes
    st.markdown(generate_button_styles(), unsafe_allow_html=True)
    
    # Dashboard como default se nenhuma página foi selecionada
    if not app_mode:
        app_mode = "Dashboard"
        selected_module = "dashboard"
    
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
    elif app_mode == "Consumo de Energia":
        energy_consumptions.show()
    elif app_mode == "Consumo de Água":
        water_consumptions.show()
    elif app_mode == "Estações de Monitoramento":
        monitoring_stations.show()
    elif app_mode == "Tarifas":
        tariff_schedules.show()
    elif app_mode == "Usuários":
        users.show()


def show_enhanced_dashboard():
    """
    Dashboard melhorado com cards de visão geral e navegação rápida
    """
    st.title("🏠 Dashboard - Visão Geral")
    
    # Cards de métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ComponentLibrary.metric_card(
            title="Estações Ativas",
            value="12",
            delta="+2 hoje",
            icon="🏭"
        )
    
    with col2:
        ComponentLibrary.metric_card(
            title="Controladores Online", 
            value="98%",
            delta="Normal",
            delta_color="normal",
            icon="🎮"
        )
    
    with col3:
        ComponentLibrary.metric_card(
            title="Consumo Hoje",
            value="245 kWh",
            delta="-12%",
            delta_color="normal",
            icon="⚡"
        )
    
    with col4:
        ComponentLibrary.metric_card(
            title="Economia Mensal",
            value="R$ 1.247",
            delta="+8%",
            delta_color="normal", 
            icon="💰"
        )
    
    st.markdown("---")
    
    # Seção de ações rápidas
    st.subheader("🚀 Ações Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ComponentLibrary.card(
            title="Monitoramento",
            content="Visualizar medições em tempo real dos sensores e estações de monitoramento.",
            icon="📊",
            color="primary",
            actions=[
                {"label": "Ver Medições", "key": "goto_measurements"},
                {"label": "Relatórios", "key": "goto_reports"}
            ]
        )
    
    with col2:
        ComponentLibrary.card(
            title="Controle",
            content="Gerenciar controladores, válvulas e configurações de automação do sistema.", 
            icon="🎮",
            color="secondary",
            actions=[
                {"label": "Controladores", "key": "goto_controllers"},
                {"label": "Válvulas", "key": "goto_valves"}
            ]
        )
    
    with col3:
        ComponentLibrary.card(
            title="Consumo",
            content="Analisar consumo de energia e água com gráficos detalhados e projeções.",
            icon="⚡",
            color="warning",
            actions=[
                {"label": "Energia", "key": "goto_energy"},
                {"label": "Água", "key": "goto_water"}
            ]
        )
    
    # Status do sistema
    st.markdown("---")
    st.subheader("🔧 Status do Sistema") 
    
    try:
        # Usar o dashboard original como fallback
        dashboard.show()
    except Exception as e:
        ComponentLibrary.alert(
            f"Erro ao carregar dados do dashboard: {str(e)}",
            alert_type="error"
        )


if __name__ == "__main__":
    main()
