import streamlit as st

from api import get_token


def login():
    # Inicializa "authenticated" se não existir
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Se o usuário já tem um token válido na sessão, mantemos autenticado
    if "token" in st.session_state and st.session_state["token"]:
        st.session_state["authenticated"] = True
        return  # Já está autenticado, sai da função

    # Caso não esteja autenticado, exibe campos de login
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not password:
            st.error("Por favor, preencha ambos os campos.")
        else:
            token = get_token(email, password)
            if token:
                st.session_state["token"] = token
                st.session_state["authenticated"] = True
                st.experimental_rerun()  # Forçar recarregamento para exibir o app
            else:
                st.error("Credenciais inválidas.")


def logout():
    st.session_state.pop("token", None)
    st.session_state["authenticated"] = False
    st.experimental_rerun()
