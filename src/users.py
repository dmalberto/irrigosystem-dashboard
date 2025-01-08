# src/users.py

import streamlit as st

from api import api_request


def create_user(token, data):
    endpoint = "/api/users/create"
    resp = api_request("POST", endpoint, token=token, json=data)
    return resp


def delete_user(token, email):
    endpoint = f"/api/users/{email}"
    resp = api_request("DELETE", endpoint, token=token)
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
            if email and password == confirm:
                data = {
                    "email": email,
                    "password": password,
                    "passwordConfirmation": confirm,
                    "role": role,
                }
                resp = create_user(token, data)
                if resp and resp.status_code == 200:
                    st.success("Usuário criado com sucesso!")
                else:
                    st.error("Falha ao criar usuário.")
                    if resp is not None:
                        st.write(resp.text)
            else:
                st.error("Senhas não conferem ou email vazio.")

    st.markdown("---")

    st.subheader("Excluir Usuário")
    with st.form("DeleteUser"):
        email_delete = st.text_input("Email do Usuário para Excluir")
        submitted_delete = st.form_submit_button("Excluir")
        if submitted_delete:
            if email_delete:
                resp = delete_user(token, email_delete)
                if resp and resp.status_code == 200:
                    st.success("Usuário excluído com sucesso!")
                else:
                    st.error("Falha ao excluir usuário.")
                    if resp is not None:
                        st.write(resp.text)
            else:
                st.error("Informe o email do usuário para excluir.")


if __name__ == "__main__":
    show()
