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

    # ---------- MENU HORIZONTAL (Option Menu) ----------
    app_mode = option_menu(
        menu_title=None,
        options=[
            "Medições",
            "Dashboard",
            "Controladores",
            "Válvulas",
            "Consumo de Energia",
            "Consumo de Água",
            "Tarifas",
            "Relatórios de Medições",
            "Ativações de Bomba",
            "Usuários",
            "Estações de Monitoramento",
        ],
        icons=[
            "clipboard-data",
            "bar-chart",
            "gear",
            "droplet-half",
            "lightning-charge",
            "droplet",
            "cash-stack",
            "journal-code",
            "clock-history",
            "people",
            "tools",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            # Barra de botões
            "container": {
                "background-color": MENU_BACKGROUND_COLOR,
                "border-radius": "5px",
                "padding": "5px 8px",  # Pouco padding
                "margin-bottom": "10px",
                "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                "border": "1px solid #e8e8e8",
                "display": "flex",
                "justify-content": "space-evenly",
                "flex-wrap": "wrap",
            },
            # Ícone dentro do botão
            "icon": {
                "font-size": "1.1rem",
                "margin-bottom": "3px",
            },
            # Botões
            "nav-link": {
                "height": "70px",  # Aumentamos altura
                "width": "110px",  # Reduzimos largura
                "display": "flex",
                "flex-direction": "column",  # Ícone acima do texto
                "justify-content": "center",
                "align-items": "center",
                "font-family": "'Roboto', sans-serif",
                "font-size": "14px",
                "font-weight": "400",
                "color": TEXT_COLOR,
                "text-align": "center",
                "margin": "4px",
                "padding": "4px",  # Pouco padding interno
                "border-radius": "4px",
                "background-color": MENU_BACKGROUND_COLOR,
                "transition": "all 0.3s ease-in-out",
            },
            # Hover
            "nav-link:hover": {
                "background-color": MENU_HOVER_COLOR,
                "font-weight": "400",
                "color": TEXT_COLOR,
            },
            # Selecionado
            "nav-link-selected": {
                "background-color": MENU_SELECTED_BACKGROUND_COLOR,
                "color": SECONDARY_COLOR,
                "font-weight": "400",
            },
        },
    )
    st.markdown("---")

    # ---------- CARREGAMENTO DE PÁGINAS ----------
    if app_mode == "Medições":
        measurements.show()
    elif app_mode == "Dashboard":
        dashboard.show()
    elif app_mode == "Controladores":
        controllers.show()
    elif app_mode == "Válvulas":
        valves.show()
    elif app_mode == "Consumo de Energia":
        energy_consumptions.show()
    elif app_mode == "Consumo de Água":
        water_consumptions.show()
    elif app_mode == "Tarifas":
        tariff_schedules.show()
    elif app_mode == "Relatórios de Medições":
        measurement_reports.show()
    elif app_mode == "Ativações de Bomba":
        controller_activations.show()
    elif app_mode == "Usuários":
        users.show()
    elif app_mode == "Estações de Monitoramento":
        monitoring_stations.show()


if __name__ == "__main__":
    main()
