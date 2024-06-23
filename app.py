from dotenv import load_dotenv
from streamlit_option_menu import option_menu

import src.amostras as amostras  # Relatórios
import src.dashboard as dashboard  # Gráficos
from config import st
from src.health_check import show_health_check

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

st.set_page_config(page_title="IrrigoSystem Dashboard", layout="wide")

st.markdown(
    """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        .css-1d391kg {
            margin-top: -2em;
        }
        .css-18e3th9 {
            padding-top: 1rem;
        }
        .css-15zrgzn {
            background-color: #f9f9f9;
        }
        .css-18ni7ap {
            padding-left: 0;
            padding-right: 0;
        }
        .css-1cpxqw2 {
            padding: 1rem;
        }
        .navbar {
            display: flex;
            justify-content: center;
            background-color: #f9f9f9;
            padding: 1rem;
            border-bottom: 1px solid #ddd;
        }
        .navbar-item {
            padding: 0.5rem 1rem;
            margin: 0 0.5rem;
            cursor: pointer;
            border-radius: 5px;
            color: #1f77b4;
            font-weight: bold;
        }
        .navbar-item:hover {
            background-color: #e1e1e1;
        }
        .navbar-item-active {
            background-color: #1f77b4;
            color: white;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def main():
    st.title("IrrigoSystem Dashboard")

    # Navegação horizontal com navbar
    app_mode = option_menu(
        menu_title=None,
        options=["Amostras", "Dashboard", "Health Check"],
        icons=["bar-chart", "cpu", "activity"],
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
    elif app_mode == "Health Check":
        show_health_check()


if __name__ == "__main__":
    main()
