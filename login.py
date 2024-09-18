import json

import streamlit as st
from requests import request

from config import base_url


def get_token(email, password):
    payload = json.dumps({"email": email, "password": password})
    headers = {"Content-Type": "application/json"}

    try:
        response = request(
            "POST",
            base_url + "/api/users/login",
            headers=headers,
            data=payload,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Erro ao conectar com a API de login: {e}")
        return None

    if response.status_code != 200:
        st.error("Email ou senha inválidos.")
        return None

    try:
        return response.json()["token"]
    except (ValueError, KeyError):
        st.error("Resposta da API de login inválida.")
        return None


def login(cookies):
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not password:
            st.error("Por favor, preencha ambos os campos.")
        else:
            token = get_token(email, password)
            if token:
                # Define o cookie com o token
                cookies["token"] = token
                cookies.save()
                st.session_state["authenticated"] = True
                st.session_state["token"] = token
                st.experimental_rerun()


def logout(cookies):
    # Remove o cookie de token
    if "token" in cookies:
        del cookies["token"]
        cookies.save()
    st.session_state["authenticated"] = False
    st.session_state["token"] = None
    st.experimental_rerun()
