# src/users.py
"""
Gerenciamento de Usuários - Padronizado com UI Foundations v3
"""

import streamlit as st

from api import api_request
from src.design_tokens import DesignTokens
from src.ui_components import (
    FormBuilder,
    ComponentLibrary,
    handle_api_response_v2,
    validate_email,
    validate_password
)


def create_user(token, data):
    endpoint = "/api/users/create"
    resp = api_request("POST", endpoint, token=token, json=data)
    return resp


def delete_user(token, email):
    endpoint = f"/api/users/{email}"
    resp = api_request("DELETE", endpoint, token=token)
    return resp


def show():
    st.title("👥 Gerenciamento de Usuários")

    token = st.session_state.get("token")
    if not token:
        ComponentLibrary.alert(
            "Usuário não autenticado. Faça login para acessar esta funcionalidade.",
            alert_type="error"
        )
        return

    # Tabs para organizar funcionalidades
    tab1, tab2 = st.tabs(["➕ Criar Usuário", "🗑️ Remover Usuário"])
    
    with tab1:
        show_create_user_form(token)
    
    with tab2:
        show_delete_user_form(token)


def show_create_user_form(token):
    """Formulário padronizado para criação de usuário"""
    
    # Usar FormBuilder para criar formulário padronizado
    form = FormBuilder(
        form_id="create_user",
        title="Cadastrar Novo Usuário",
        description="Preencha os dados para criar uma nova conta de acesso ao sistema."
    )
    
    form.add_text_field(
        label="Email",
        placeholder="usuario@exemplo.com",
        help_text="Endereço de email válido que será usado para login",
        required=True,
        key="user_email"
    )
    
    # Campos de senha customizados (não suportados pelo FormBuilder ainda)
    st.markdown("""
    <style>
    .password-field .stTextInput input {
        font-family: monospace;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("create_user_manual"):
        st.markdown("### 🔐 Configurações de Acesso")
        
        email = st.text_input(
            "Email *",
            placeholder="usuario@exemplo.com",
            help="Endereço de email válido para login",
        )
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Senha *",
                type="password",
                placeholder="Digite uma senha segura",
                help="Mínimo 8 caracteres, incluindo letras e números",
            )
        
        with col2:
            confirm = st.text_input(
                "Confirmação de Senha *",
                type="password", 
                placeholder="Digite a senha novamente",
                help="Deve ser idêntica à senha informada acima",
            )
        
        role = st.selectbox(
            "Perfil de Acesso *",
            ["user", "admin"],
            index=0,
            help="user = Acesso básico | admin = Acesso completo",
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("✅ Criar Usuário", type="primary", use_container_width=True)
        
        if submitted:
            # Validações
            errors = []
            
            if not email.strip():
                errors.append("Email é obrigatório.")
            elif not validate_email(email):
                errors.append("Email deve ter formato válido (exemplo@dominio.com).")
            
            password_valid, password_msg = validate_password(password)
            if not password_valid:
                errors.append(password_msg)
            
            if password != confirm:
                errors.append("Senhas não conferem.")
            
            # Exibir erros
            if errors:
                for error in errors:
                    ComponentLibrary.alert(error, alert_type="error")
                return
            
            # Criar usuário
            data = {
                "email": email,
                "password": password,
                "passwordConfirmation": confirm,
                "role": role,
            }
            
            resp = create_user(token, data)
            if handle_api_response_v2(resp, "✅ Usuário criado com sucesso!"):
                ComponentLibrary.alert(
                    f"Usuário **{email}** foi criado com perfil **{role}**.",
                    alert_type="success"
                )
                st.rerun()


def show_delete_user_form(token):
    """Formulário padronizado para remoção de usuário"""
    
    ComponentLibrary.alert(
        "⚠️ **ATENÇÃO**: Esta operação remove permanentemente o usuário e não pode ser desfeita.",
        alert_type="warning"
    )
    
    with st.form("delete_user"):
        st.markdown("### 🗑️ Remover Usuário")
        
        email_delete = st.text_input(
            "Email do Usuário *",
            placeholder="usuario@exemplo.com",
            help="Digite o email exato do usuário que será removido",
        )
        
        # Confirmação visual
        if email_delete.strip():
            st.markdown(f"""
            <div style="
                background-color: {DesignTokens.COLORS['error']}20;
                border: 2px solid {DesignTokens.COLORS['error']};
                border-radius: {DesignTokens.RADIUS['md']};
                padding: {DesignTokens.SPACING['4']};
                margin: {DesignTokens.SPACING['4']} 0;
                text-align: center;
            ">
                <strong>🚨 USUÁRIO A SER REMOVIDO: {email_delete}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Checkbox de confirmação
            confirm_deletion = st.checkbox(
                f"Confirmo que quero EXCLUIR PERMANENTEMENTE o usuário {email_delete}",
                help="Esta confirmação é obrigatória para realizar a exclusão"
            )
        else:
            confirm_deletion = False
        
        st.markdown("---")
        submitted = st.form_submit_button(
            "🗑️ CONFIRMAR EXCLUSÃO", 
            type="primary",
            use_container_width=True,
            disabled=not confirm_deletion
        )
        
        if submitted:
            # Validações
            if not email_delete.strip():
                ComponentLibrary.alert("Email é obrigatório.", alert_type="error")
                return
            
            if not validate_email(email_delete):
                ComponentLibrary.alert("Email deve ter formato válido.", alert_type="error")
                return
                
            if not confirm_deletion:
                ComponentLibrary.alert("Você deve confirmar a exclusão.", alert_type="error")
                return
            
            # Excluir usuário
            resp = delete_user(token, email_delete)
            if handle_api_response_v2(resp, f"✅ Usuário {email_delete} foi removido com sucesso!"):
                ComponentLibrary.alert(
                    f"O usuário **{email_delete}** foi excluído permanentemente.",
                    alert_type="success"
                )
                st.rerun()


if __name__ == "__main__":
    show()
