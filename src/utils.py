"""
Utilidades compartilhadas para o sistema de irrigação.
Inclui tratamento de erros, validações e componentes comuns de UI.
"""

import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Union


def handle_api_response(response, success_message: str = "", error_message: str = "", 
                       expected_status: int = 200) -> Optional[Any]:
    """
    Padroniza o tratamento de respostas da API.
    
    Args:
        response: Resposta da API
        success_message: Mensagem de sucesso (opcional)
        error_message: Mensagem de erro personalizada
        expected_status: Status code esperado (padrão: 200)
        
    Returns:
        Dados da resposta em caso de sucesso, None em caso de erro
    """
    if not response:
        st.error(f"{error_message} - Sem resposta da API.")
        return None
        
    if response.status_code == expected_status:
        if success_message:
            st.success(success_message)
        try:
            return response.json()
        except ValueError:
            return True  # Para DELETE que pode não retornar JSON
    else:
        status_messages = {
            400: "Dados inválidos enviados",
            401: "Usuário não autenticado",
            403: "Acesso negado", 
            404: "Recurso não encontrado",
            409: "Conflito - recurso já existe",
            500: "Erro interno do servidor"
        }
        
        status_msg = status_messages.get(response.status_code, f"Erro HTTP {response.status_code}")
        full_error = f"{error_message} - {status_msg}"
        
        try:
            error_detail = response.text
            if error_detail:
                full_error += f" - {error_detail}"
        except:
            pass
            
        st.error(full_error)
        return None


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Valida se todos os campos obrigatórios estão preenchidos.
    
    Args:
        data: Dicionário com os dados
        required_fields: Lista de campos obrigatórios
        
    Returns:
        True se todos os campos estão válidos, False caso contrário
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        st.error(f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}")
        return False
    return True


def validate_email(email: str) -> bool:
    """Valida formato de email básico."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        st.error("Formato de email inválido.")
        return False
    return True


def validate_date_range(start_date, end_date) -> bool:
    """Valida se o intervalo de datas é válido."""
    if start_date and end_date and start_date > end_date:
        st.error("Data de início deve ser anterior à data de fim.")
        return False
    return True


def validate_positive_number(value: float, field_name: str) -> bool:
    """Valida se o número é positivo."""
    if value < 0:
        st.error(f"{field_name} deve ser um valor positivo.")
        return False
    return True


def safe_dataframe_display(data: List[Dict], columns_mapping: Optional[Dict[str, str]] = None,
                          empty_message: str = "Nenhum dado disponível.",
                          set_index: Optional[str] = None) -> None:
    """
    Exibe DataFrame de forma segura com formatação padrão.
    
    Args:
        data: Lista de dicionários com os dados
        columns_mapping: Mapeamento de nomes de colunas
        empty_message: Mensagem quando não há dados
        set_index: Coluna para usar como índice
    """
    if not data:
        st.info(empty_message)
        return
    
    df = pd.DataFrame(data)
    
    if columns_mapping and not df.empty:
        df.rename(columns=columns_mapping, inplace=True)
    
    if set_index and set_index in df.columns:
        df.set_index(set_index, inplace=True)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info(empty_message)


def create_pagination_controls(current_page: int, has_more_data: bool = True) -> bool:
    """
    Cria controles de paginação padronizados.
    
    Args:
        current_page: Página atual
        has_more_data: Se há mais dados para carregar
        
    Returns:
        True se o usuário clicou em "Carregar mais"
    """
    if has_more_data:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.text(f"Página: {current_page}")
        with col2:
            return st.button("Carregar mais")
    else:
        st.info("Todos os dados foram carregados.")
    return False


def format_currency(value: float) -> str:
    """Formata valor monetário em reais."""
    return f"R$ {value:.2f}"


def format_percentage(value: float) -> str:
    """Formata valor como porcentagem."""
    return f"{value:.1f}%"


def create_form_section(title: str, fields: List[Dict[str, Any]], 
                       submit_label: str = "Enviar") -> Optional[Dict[str, Any]]:
    """
    Cria uma seção de formulário padronizada.
    
    Args:
        title: Título da seção
        fields: Lista de definições de campos
        submit_label: Texto do botão de envio
        
    Returns:
        Dicionário com os valores do formulário ou None se não submetido
    """
    st.subheader(title)
    
    form_key = title.lower().replace(" ", "_")
    with st.form(form_key):
        form_data = {}
        
        for field in fields:
            field_type = field.get("type", "text")
            field_name = field["name"]
            field_label = field.get("label", field_name)
            
            if field_type == "text":
                form_data[field_name] = st.text_input(
                    field_label, 
                    value=field.get("default", ""),
                    help=field.get("help")
                )
            elif field_type == "number":
                form_data[field_name] = st.number_input(
                    field_label,
                    min_value=field.get("min_value", 0.0),
                    max_value=field.get("max_value", None),
                    value=field.get("default", 0.0),
                    step=field.get("step", 1.0),
                    help=field.get("help")
                )
            elif field_type == "select":
                form_data[field_name] = st.selectbox(
                    field_label,
                    options=field["options"],
                    index=field.get("default_index", 0),
                    help=field.get("help")
                )
            elif field_type == "email":
                form_data[field_name] = st.text_input(
                    field_label,
                    value=field.get("default", ""),
                    help=field.get("help")
                )
            elif field_type == "password":
                form_data[field_name] = st.text_input(
                    field_label,
                    type="password",
                    help=field.get("help")
                )
        
        if st.form_submit_button(submit_label):
            return form_data
    
    return None