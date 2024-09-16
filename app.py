# app.py

from dotenv import load_dotenv
from streamlit_option_menu import option_menu

import src.amostras as amostras  # Relatórios
import src.consumo_energia as consumo_energia  # Relatórios de Consumo de Energia
import src.controlador as controlador  # Dados do Controlador
import src.dashboard as dashboard  # Gráficos
import src.equipamentos as equipamentos  # Cadastro de Equipamentos
import src.health_check as health_check
from config import st
from login import login, logout

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

st.set_page_config(page_title="IrrigoSystem Dashboard", layout="wide")


def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()  # Chama a função de login
    else:
        st.title("IrrigoSystem Dashboard")

        # Botão de logout
        st.sidebar.button("Sair", on_click=logout)

        # Navegação horizontal com navbar
        app_mode = option_menu(
            menu_title=None,
            options=[
                "Amostras",
                "Dashboard",
                "Controladores",
                "Equipamentos",
                "Consumo de Energia",
                "Health Check",
            ],
            icons=[
                "clipboard-data",
                "bar-chart",
                "gear",
                "archive",
                "lightning-charge",
                "activity",
            ],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#f9f9f9"},
                "icon": {"color": "blue", "font-size": "18px"},
                "nav-link": {
                    "font-size": "18px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#1f77b4", "color": "white"},
            },
        )

        st.markdown("---")

        if app_mode == "Amostras":
            amostras.show()
        elif app_mode == "Dashboard":
            dashboard.show()
        elif app_mode == "Controladores":
            controlador.show()
        elif app_mode == "Equipamentos":
            equipamentos.show()
        elif app_mode == "Consumo de Energia":
            consumo_energia.show()
        elif app_mode == "Health Check":
            health_check.show_health_check()


if __name__ == "__main__":
    main()
