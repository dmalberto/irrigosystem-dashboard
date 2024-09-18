import os

import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_option_menu import option_menu

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o EncryptedCookieManager
cookies = EncryptedCookieManager(
    prefix="irrigosystem-",
    password=os.getenv("COOKIE_SECRET_PASSWORD"),
)

if not cookies.ready():
    st.stop()

# Importações dos módulos personalizados
import src.amostras as amostras
import src.consumo_energia as consumo_energia
import src.controlador as controlador
import src.dashboard as dashboard
import src.equipamentos as equipamentos
import src.health_check as health_check
from config import base_url
from login import login, logout


def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Verifica se há um token no cookie
    token = cookies.get("token")
    if token and not st.session_state["authenticated"]:
        st.session_state["authenticated"] = True
        st.session_state["token"] = token  # Atualiza o token na sessão

    if not st.session_state["authenticated"]:
        login(cookies)  # Passa o objeto cookies para a função de login
    else:
        st.title("IrrigoSystem Dashboard")

        # Botão de logout
        st.sidebar.button("Sair", on_click=logout, args=(cookies,))

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
        elif app_mode == "Energia":
            consumo_energia.show()
        elif app_mode == "Health Check":
            health_check.show_health_check()


if __name__ == "__main__":
    main()
