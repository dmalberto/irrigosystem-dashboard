# api.py
import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

# Garante que variáveis de ambiente do .env sejam carregadas antes de uso
load_dotenv()

base_url = os.getenv("API_URL")


def get_token(email, password):
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    response = api_request(
        method="POST",
        endpoint="/api/users/login",
        data=json.dumps(payload),
        headers=headers,
    )
    if response is None:
        # Já mostramos erro no api_request
        return None

    if response.status_code == 200:
        try:
            return response.json().get("token")
        except (ValueError, KeyError):
            st.error("Resposta da API de login inválida.")
            return None
    else:
        st.error("Email ou senha inválidos.")
        return None


def api_request(method, endpoint, token=None, timeout=10, **kwargs):
    """
    Função utilitária para realizar chamadas à API,
    centralizando tratamento de erros e inclusão de cabeçalhos.
    """
    if not base_url:
        st.error("Variável de ambiente API_URL não configurada.")
        return None

    url = f"{base_url}{endpoint}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(
            method, url, headers=headers, timeout=timeout, **kwargs
        )
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Erro HTTP ao chamar a API: {http_err}")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com a API: {e}")
    return None
