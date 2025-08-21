# src/users.py

import streamlit as st

from api import api_request
from src.utils import handle_api_response, validate_email, validate_required_fields


def create_user(token, data):
    endpoint = "/api/users/create"
    resp = api_request("POST", endpoint, token=token, json=data, timeout=30)
    return resp


def delete_user(token, email):
    endpoint = f"/api/users/{email}"
    resp = api_request("DELETE", endpoint, token=token, timeout=30)
    return resp


def show():
    st.title("Gerenciamento de Usuários")

    token = st.session_state.get("token")
    if not token:
        st.error("Usuário não autenticado.")
        return

    st.subheader("Criar Usuário")
    with st.form("CreateUser"):
        email = st.text_input("Email do Novo Usuário")
        password = st.text_input("Senha", type="password")
        confirm = st.text_input("Confirmação de Senha", type="password")
        role = st.selectbox("Role", ["admin", "user"])
        submitted_create = st.form_submit_button("Criar")
        if submitted_create:
            if validate_email(email) and password == confirm and len(password) >= 6:
                data = {
                    "email": email,
                    "password": password,
                    "passwordConfirmation": confirm,
                    "role": role,
                }
                resp = create_user(token, data)
                result = handle_api_response(
                    resp, 
                    success_message="Usuário criado com sucesso!",
                    error_message="Falha ao criar usuário"
                )
                if result:
                    st.rerun()
            elif password != confirm:
                st.error("Senhas não conferem.")
            elif len(password) < 6:
                st.error("Senha deve ter pelo menos 6 caracteres.")

    st.markdown("---")

    st.subheader("Excluir Usuário")
    with st.form("DeleteUser"):
        email_delete = st.text_input("Email do Usuário para Excluir")
        submitted_delete = st.form_submit_button("Excluir")
        if submitted_delete:
            if validate_email(email_delete):
                resp = delete_user(token, email_delete)
                result = handle_api_response(
                    resp,
                    success_message="Usuário excluído com sucesso!", 
                    error_message="Falha ao excluir usuário"
                )
                if result:
                    st.rerun()
            else:
                st.error("Informe um email válido para excluir.")


if __name__ == "__main__":
    show()
