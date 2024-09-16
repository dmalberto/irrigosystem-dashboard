# config.py

import os

import streamlit as st
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Cookies Manager
cookies = EncryptedCookieManager(
    prefix="irrigosystem-",  # Prefixo para identificar os cookies da aplicação
    password=os.getenv(
        "COOKIE_SECRET_PASSWORD"
    ),  # Senha segura armazenada em variável de ambiente
)

# Inicializa os cookies
if not cookies.ready():
    # Aguarda a inicialização dos cookies
    st.stop()

# Exporta o cookies manager para uso nos demais módulos
st.cookies = cookies

# Define a base URL da API
base_url = "http://54.86.43.17"
