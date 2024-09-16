# login.py

import json

import streamlit as st
from requests import request

from config import base_url


def get_token(email, password):
    payload = json.dumps({"email": email, "password": password})
    headers = {"Content-Type": "application/json"}

    response = request(
        "POST", base_url + "/api/users/login", headers=headers, data=payload, timeout=10
    )

    if response.status_code != 200:
        st.error("Email ou senha inválidos.")
        return None

    return response.json()["token"]


def login():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        token = get_token(email, password)
        if token:
            st.session_state["token"] = token
            st.session_state["authenticated"] = True
            st.experimental_rerun()


def logout():
    st.session_state["authenticated"] = False
    st.session_state["token"] = None
    st.experimental_rerun()
