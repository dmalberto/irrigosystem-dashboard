# src/users.py

import streamlit as st

from api import api_request
from src.ui_components import (handle_api_response, validate_email,
                               validate_password)


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
        email = st.text_input(
            "Email *",
            placeholder="usuario@exemplo.com",
            help="Endereço de email válido para login",
        )
        password = st.text_input(
            "Senha *",
            type="password",
            placeholder="Digite uma senha segura",
            help="Mínimo 8 caracteres, incluindo letras e números",
        )
        confirm = st.text_input(
            "Confirmação de Senha *",
            type="password",
            placeholder="Digite a senha novamente",
            help="Deve ser idêntica à senha informada acima",
        )
        role = st.selectbox(
            "Perfil *",
            ["admin", "user"],
            index=1,  # Default to 'user'
            help="Nível de permissão do usuário",
        )
        submitted_create = st.form_submit_button("Criar")
        if submitted_create:
            # Validações
            if not email.strip():
                st.error("Email é obrigatório.")
                return

            if not validate_email(email):
                st.error("Email deve ter formato válido (exemplo@dominio.com).")
                return

            password_valid, password_msg = validate_password(password)
            if not password_valid:
                st.error(password_msg)
                return

            if password != confirm:
                st.error("Senhas não conferem.")
                return

            data = {
                "email": email,
                "password": password,
                "passwordConfirmation": confirm,
                "role": role,
            }

            resp = create_user(token, data)
            handle_api_response(resp, "Usuário criado com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()

    st.markdown("---")

    st.subheader("Excluir Usuário")
    with st.form("DeleteUser"):
        email_delete = st.text_input(
            "Email do Usuário para Excluir *",
            placeholder="usuario@exemplo.com",
            help="Digite o email exato do usuário que deve ser removido",
        )

        # Warning para operação destrutiva
        if email_delete:
            st.warning(
                f"⚠️ **ATENÇÃO**: Esta operação irá excluir permanentemente o usuário **{email_delete}**"
            )

        submitted_delete = st.form_submit_button("🗑️ Confirmar Exclusão", type="primary")
        if submitted_delete:
            if not email_delete.strip():
                st.error("Email é obrigatório.")
                return

            if not validate_email(email_delete):
                st.error("Email deve ter formato válido.")
                return

            resp = delete_user(token, email_delete)
            handle_api_response(resp, "Usuário excluído com sucesso!")
            if resp and 200 <= resp.status_code < 300:
                st.rerun()


if __name__ == "__main__":
    show()
