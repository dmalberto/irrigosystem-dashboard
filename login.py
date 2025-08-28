
import streamlit as st
import os
import pickle
from datetime import datetime, timedelta

from api import get_token

# Constante para armazenamento da sessão
SESSION_FILE = ".session_data"
SESSION_EXPIRY_DAYS = 30  # Tempo de validade da sessão persistente

def login():
    # Inicializa "authenticated" se não existir
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        
    # Verificar se existe uma sessão salva válida
    if not st.session_state["authenticated"]:
        load_saved_session()
    
    # Se o usuário já tem um token válido na sessão, mantemos autenticado
    if "token" in st.session_state and st.session_state["token"]:
        st.session_state["authenticated"] = True
        return  # Já está autenticado, sai da função

    # Caso não esteja autenticado, exibe campos de login
    st.title("Login")

    # Usando st.form para capturar o Enter automaticamente
    with st.form(key="login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Senha", type="password", key="login_password")
        
        # Adiciona opção "Manter conectado"
        keep_logged_in = st.checkbox("Manter conectado", value=False, key="keep_logged_in")
        
        # O botão de submit do form captura o Enter automaticamente
        submit_button = st.form_submit_button(label="Entrar")
        
        # Quando o formulário é enviado (clique no botão ou Enter)
        if submit_button:
            process_login(email, password, keep_logged_in)

def process_login(email, password, keep_logged_in=False):
    """Processa a tentativa de login"""
    if not email or not password:
        st.error("Por favor, preencha ambos os campos.")
    else:
        token = get_token(email, password)
        if token:
            st.session_state["token"] = token
            st.session_state["authenticated"] = True
            
            # Se o usuário marcou "Manter conectado", salva a sessão
            if keep_logged_in:
                save_session(token, email)
                
            st.rerun()  # Forçar recarregamento para exibir o app
        else:
            st.error("Credenciais inválidas.")

def save_session(token, email):
    """Salva a sessão para uso futuro"""
    try:
        # Cria um dicionário com as informações da sessão
        expiry_date = datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)
        session_data = {
            "token": token,
            "email": email,
            "expiry": expiry_date
        }
        
        # Salva os dados em um arquivo com pickle
        with open(SESSION_FILE, 'wb') as file:
            pickle.dump(session_data, file)
    except Exception as e:
        print(f"Erro ao salvar sessão: {str(e)}")

def load_saved_session():
    """Carrega uma sessão salva anteriormente"""
    try:
        # Verifica se o arquivo de sessão existe
        if not os.path.exists(SESSION_FILE):
            return False
        
        # Carrega os dados da sessão
        with open(SESSION_FILE, 'rb') as file:
            session_data = pickle.load(file)
        
        # Verifica se a sessão expirou
        if session_data.get("expiry") < datetime.now():
            # Sessão expirada, remove o arquivo
            os.remove(SESSION_FILE)
            return False
        
        # Restaura a sessão
        st.session_state["token"] = session_data.get("token")
        
        return True
    except Exception as e:
        print(f"Erro ao carregar sessão: {str(e)}")
        return False

def logout():
    """Remove o token e marca como não autenticado"""
    st.session_state.pop("token", None)
    st.session_state["authenticated"] = False
    
    # Remove o arquivo de sessão se existir
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except:
            pass
    
    st.rerun()
