# src/ui_components.py
"""
UI Foundations + Padronização Global - v3
Sistema completo de componentes padronizados com Design Tokens,
FormBuilder, ComponentLibrary e estados avançados de UI/UX.
"""

import re
import time as time_module
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import streamlit as st

from src.design_tokens import DesignTokens, get_color, get_spacing, get_shadow, generate_button_styles


def format_datetime_for_api(date_value, time_value=None):
    """Converte para ISO-8601 UTC Z para envio à API."""
    if date_value:
        if time_value:
            dt = datetime.combine(date_value, time_value)
        else:
            dt = datetime.combine(date_value, time.min)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def format_datetime_for_display(iso_string):
    """Converte ISO para formato brasileiro de exibição."""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return iso_string


def controller_selector(
    token, label="Selecione o Controlador *", include_all_option=False
):
    """Seletor padronizado de controladores conforme padrão 'Nome (ID: X)'."""
    # Import here to avoid circular dependency
    from src.controllers import get_controllers

    @st.cache_data(ttl=120)  # 2 minutos
    def get_controllers_cached(token):
        return get_controllers(token)

    controllers = get_controllers_cached(token)
    if not controllers:
        st.warning("Nenhum controlador cadastrado.")
        return None, None

    options = {}
    if include_all_option:
        options["Todos os Controladores"] = None

    options.update(
        {f"{ctrl['name']} (ID: {ctrl['id']})": ctrl["id"] for ctrl in controllers}
    )

    choice = st.selectbox(label, options.keys())
    return options[choice], choice


def date_range_filter(default_days=7, max_days=62):
    """Filtro padronizado de range de datas."""

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Data de Início *",
            value=date.today() - timedelta(days=default_days),
            help=f"Data inicial do período (máx {max_days} dias)",
        )

    with col2:
        end_date = st.date_input(
            "Data de Fim *", value=date.today(), help="Data final do período"
        )

    # Validação
    if start_date > end_date:
        st.error("Data de início deve ser anterior à data de fim.")
        return None, None

    if (end_date - start_date).days > max_days:
        st.error(f"Período máximo permitido é de {max_days} dias.")
        return None, None

    return start_date, end_date


def validate_email(email):
    """Validação de formato de email."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validação de força de senha.
    Regras: mín 8 chars, pelo menos 1 letra, 1 número
    """
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres."

    if not re.search(r"[A-Za-z]", password):
        return False, "Senha deve conter pelo menos uma letra."

    if not re.search(r"\d", password):
        return False, "Senha deve conter pelo menos um número."

    return True, "Senha válida."


def validate_coordinates(lat, lon):
    """Valida se coordenadas estão em ranges geográficos válidos."""
    if not (-90 <= lat <= 90):
        return False, "Latitude deve estar entre -90 e 90 graus."

    if not (-180 <= lon <= 180):
        return False, "Longitude deve estar entre -180 e 180 graus."

    return True, "Coordenadas válidas."


# Função removida - usar handle_api_response_v2


def geographic_coordinates_input(lat_value=None, lon_value=None):
    """Inputs padronizados para coordenadas geográficas."""
    col1, col2 = st.columns(2)

    with col1:
        latitude = st.number_input(
            "Latitude *",
            min_value=-90.0,
            max_value=90.0,
            format="%.6f",
            value=lat_value if lat_value is not None else -23.5505,  # Default São Paulo
            help="Coordenada de latitude (-90 a 90)",
        )

    with col2:
        longitude = st.number_input(
            "Longitude *",
            min_value=-180.0,
            max_value=180.0,
            format="%.6f",
            value=lon_value if lon_value is not None else -46.6333,  # Default São Paulo
            help="Coordenada de longitude (-180 a 180)",
        )

    return latitude, longitude


def monetary_input(label, value=None, min_value=0.01, max_value=10.0, help_text=""):
    """Input padronizado para valores monetários."""
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=0.01,
        format="%.4f",
        value=value if value is not None else min_value,
        help=help_text,
    )


def percentage_input(label, value=None, min_value=0.0, max_value=100.0, help_text=""):
    """Input padronizado para percentuais."""
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=0.1,
        format="%.1f",
        value=value if value is not None else 0.0,
        help=help_text,
    )


def power_input(label, value=None, min_value=1.0, max_value=50000.0, help_text=""):
    """Input padronizado para potências (W)."""
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=0.1,  # Step adequado para double conforme Swagger
        value=value if value is not None else 100.0,
        help=help_text,
    )


def show_loading_state(message="Carregando..."):
    """Estado de carregamento padronizado."""
    return st.spinner(message)


def show_empty_state(message="Nenhum resultado encontrado para os filtros informados."):
    """Estado vazio padronizado."""
    st.info(f"📭 {message}")


def show_error_state(message="Erro ao conectar com a API."):
    """Estado de erro padronizado."""
    st.error(f"⚠️ {message}")


# =============================================================================
# SISTEMA DE CACHE COM INVALIDAÇÃO
# =============================================================================


class CacheManager:
    """Gerencia cache com TTL e invalidação automática após mutations."""

    def __init__(self):
        self._cache_keys = {
            "controllers": "cache_controllers",
            "stations": "cache_stations",
            "sensors": "cache_sensors",
            "valves": "cache_valves",
            "tariffs": "cache_tariffs",
        }

    def invalidate_cache(self, entity_type: str):
        """Invalida cache de uma entidade específica."""
        if entity_type in self._cache_keys:
            cache_key = self._cache_keys[entity_type]
            if hasattr(st, "cache_data"):
                # Clear specific cache for entity
                st.session_state[f"{cache_key}_invalidated"] = (
                    datetime.now().timestamp()
                )

    def invalidate_dependent_caches(self, parent_entity: str):
        """Invalida caches dependentes (ex: ao alterar estação, invalidar sensores)."""
        dependencies = {"stations": ["sensors"], "controllers": ["valves"]}

        if parent_entity in dependencies:
            for dep in dependencies[parent_entity]:
                self.invalidate_cache(dep)


cache_manager = CacheManager()


# =============================================================================
# HELPERS DE CASTING PARA TIPOS SWAGGER
# =============================================================================


def cast_to_int32(value: Union[int, float, str]) -> int:
    """Cast para int32 conforme swagger."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def cast_to_int64(value: Union[int, float, str]) -> int:
    """Cast para int64 conforme swagger."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def cast_to_double(value: Union[int, float, str]) -> float:
    """Cast para double conforme swagger."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# =============================================================================
# TRATAMENTO DE API RESPONSE COM 429/RETRY-AFTER
# =============================================================================


def handle_api_response_v2(
    response, success_message="Operação realizada com sucesso!"
) -> bool:
    """Tratamento completo de respostas da API incluindo 429/Retry-After."""
    if not response:
        st.error("Erro ao conectar com a API. Verifique sua conexão.")
        return False

    status_messages = {
        200: success_message,
        201: success_message,
        204: success_message,
        400: "Dados inválidos. Verifique os campos obrigatórios.",
        401: "Usuário não autorizado. Faça login novamente.",
        404: "Registro não encontrado.",
        409: "Conflito: registro já existe.",
        429: "Muitas requisições. Aguarde antes de tentar novamente.",
        500: "Erro interno do servidor. Tente novamente em alguns minutos.",
    }

    # Tratamento especial para 429 com Retry-After
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                wait_seconds = int(retry_after)
                st.warning(
                    f"⏱️ Limite de requisições atingido. Aguarde {wait_seconds} segundos."
                )

                # Adicionar countdown visual
                if "retry_countdown" not in st.session_state:
                    st.session_state.retry_countdown = wait_seconds

                progress_bar = st.progress(0)
                for i in range(wait_seconds):
                    progress_bar.progress((i + 1) / wait_seconds)
                    time_module.sleep(1)
                progress_bar.empty()

            except (ValueError, TypeError):
                st.error(status_messages[429])
        else:
            st.error(status_messages[429])
        return False

    message = status_messages.get(
        response.status_code, f"Erro inesperado: {response.status_code}"
    )

    if 200 <= response.status_code < 300:
        st.success(message)
        return True
    else:
        st.error(message)
        return False


# Manter compatibilidade com versão anterior
handle_api_response = handle_api_response_v2


# =============================================================================
# VALIDADORES AVANÇADOS
# =============================================================================


def validate_percentage_range(
    value: float, min_val: float = 0.0, max_val: float = 100.0
) -> Tuple[bool, str]:
    """Validação de percentuais com range customizável."""
    if not min_val <= value <= max_val:
        return False, f"Valor deve estar entre {min_val}% e {max_val}%."
    return True, "Percentual válido."


def validate_monetary_value(
    value: float, min_val: float = 0.01, max_val: float = 10.0
) -> Tuple[bool, str]:
    """Validação de valores monetários."""
    if value < min_val:
        return False, f"Valor deve ser no mínimo R$ {min_val:.2f}."
    if value > max_val:
        return False, f"Valor deve ser no máximo R$ {max_val:.2f}."
    return True, "Valor monetário válido."


def validate_id_positive(value: int) -> Tuple[bool, str]:
    """Validação de IDs (deve ser ≥ 1)."""
    if value < 1:
        return False, "ID deve ser um número positivo (≥ 1)."
    return True, "ID válido."


def validate_flow_rate(value: float) -> Tuple[bool, str]:
    """Validação de flow rate para válvulas."""
    if value <= 0:
        return False, "Vazão deve ser maior que zero."
    if value > 1000:  # Limite razoável para vazão
        return False, "Vazão deve ser menor que 1000 L/min."
    return True, "Vazão válida."


def validate_moisture_limits(lower: float, upper: float) -> Tuple[bool, str]:
    """Validação de limites de umidade."""
    if lower >= upper:
        return False, "Limite inferior deve ser menor que o superior."
    if not (0 <= lower <= 100) or not (0 <= upper <= 100):
        return False, "Limites devem estar entre 0% e 100%."
    return True, "Limites de umidade válidos."


# =============================================================================
# INPUTS ESPECIALIZADOS EXPANDIDOS
# =============================================================================


def flow_rate_input(
    label: str, value: Optional[float] = None, help_text: str = ""
) -> float:
    """Input padronizado para vazão (L/min)."""
    return st.number_input(
        label,
        min_value=0.1,
        max_value=1000.0,
        step=0.1,
        format="%.1f",
        value=value if value is not None else 10.0,
        help=help_text or "Vazão em litros por minuto",
    )


def moisture_limit_input(
    label: str, value: Optional[float] = None, help_text: str = ""
) -> float:
    """Input padronizado para limites de umidade (%)."""
    return st.number_input(
        label,
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        value=value if value is not None else 50.0,
        help=help_text or "Limite de umidade em percentual",
    )


def voltage_input(
    label: str, value: Optional[float] = None, help_text: str = ""
) -> float:
    """Input padronizado para voltagem (V)."""
    return st.number_input(
        label,
        min_value=0.0,
        max_value=24.0,
        step=0.1,
        format="%.2f",
        value=value if value is not None else 12.0,
        help=help_text or "Voltagem em volts",
    )


def temperature_input(
    label: str, value: Optional[float] = None, help_text: str = ""
) -> float:
    """Input padronizado para temperatura (°C)."""
    return st.number_input(
        label,
        min_value=-50.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        value=value if value is not None else 25.0,
        help=help_text or "Temperatura em graus Celsius",
    )


# =============================================================================
# SELETORES COM CACHE E FORMATO NOME (ID: X)
# =============================================================================


@st.cache_data(ttl=120, show_spinner="Carregando estações...")
def get_monitoring_stations_cached(token: str) -> List[Dict[str, Any]]:
    """Cache para estações de monitoramento."""
    from src.monitoring_stations import get_monitoring_stations

    return get_monitoring_stations(token)


@st.cache_data(ttl=120, show_spinner="Carregando sensores...")
def get_sensors_cached(token: str, station_id: int) -> List[Dict[str, Any]]:
    """Cache para sensores de uma estação específica."""
    from api import api_request

    endpoint = f"/api/monitoring-stations/{station_id}/sensors"
    response = api_request("GET", endpoint, token=token)
    if response and response.status_code == 200:
        return response.json() if isinstance(response.json(), list) else []
    return []


@st.cache_data(ttl=120, show_spinner="Carregando válvulas...")
def get_valves_cached(token: str, controller_id: int) -> List[Dict[str, Any]]:
    """Cache para válvulas de um controlador específico."""
    from api import api_request

    endpoint = f"/api/controllers/{controller_id}/valves"
    response = api_request("GET", endpoint, token=token)
    if response and response.status_code == 200:
        return response.json() if isinstance(response.json(), list) else []
    return []


def station_selector(
    token: str,
    label: str = "Selecione a Estação de Monitoramento *",
    include_all_option: bool = False,
) -> Tuple[Optional[int], Optional[str]]:
    """Seletor padronizado de estações com formato 'Nome (ID: X)'."""

    stations = get_monitoring_stations_cached(token)
    if not stations:
        st.warning("Nenhuma estação de monitoramento cadastrada.")
        return None, None

    options = {}
    if include_all_option:
        options["Todas as Estações"] = None

    options.update(
        {
            f"{station['name']} (ID: {station['id']})": cast_to_int64(station["id"])
            for station in stations
            if "id" in station and "name" in station
        }
    )

    if not options:
        st.warning("Nenhuma estação disponível.")
        return None, None

    choice = st.selectbox(label, options.keys())
    return options[choice], choice


def sensor_selector(
    token: str,
    station_id: Optional[int],
    label: str = "Selecione o Sensor *",
    include_all_option: bool = False,
) -> Tuple[Optional[int], Optional[str]]:
    """Seletor dependente de sensores - desabilitado até estação ser definida."""

    if not station_id:
        st.selectbox(label, ["Selecione uma estação primeiro"], disabled=True)
        return None, None

    sensors = get_sensors_cached(token, cast_to_int64(station_id))
    if not sensors:
        st.warning(f"Nenhum sensor cadastrado para a estação ID {station_id}.")
        return None, None

    options = {}
    if include_all_option:
        options["Todos os Sensores"] = None

    options.update(
        {
            f"Sensor {sensor['id']} (ID: {sensor['id']})": cast_to_int32(sensor["id"])
            for sensor in sensors
            if "id" in sensor
        }
    )

    if not options:
        st.warning(f"Nenhum sensor disponível para a estação ID {station_id}.")
        return None, None

    choice = st.selectbox(label, options.keys())
    return options[choice], choice


def valve_selector(
    token: str,
    controller_id: Optional[int],
    label: str = "Selecione a Válvula *",
    include_all_option: bool = False,
) -> Tuple[Optional[int], Optional[str]]:
    """Seletor dependente de válvulas - desabilitado até controlador ser definido."""

    if not controller_id:
        st.selectbox(label, ["Selecione um controlador primeiro"], disabled=True)
        return None, None

    valves = get_valves_cached(token, cast_to_int64(controller_id))
    if not valves:
        st.warning(f"Nenhuma válvula cadastrada para o controlador ID {controller_id}.")
        return None, None

    options = {}
    if include_all_option:
        options["Todas as Válvulas"] = None

    options.update(
        {
            f"Válvula {valve['id']} (Vazão: {valve.get('flowRate', 0):.1f} L/min)": cast_to_int32(
                valve["id"]
            )
            for valve in valves
            if "id" in valve
        }
    )

    if not options:
        st.warning(f"Nenhuma válvula disponível para o controlador ID {controller_id}.")
        return None, None

    choice = st.selectbox(label, options.keys())
    return options[choice], choice


# =============================================================================
# PAGINAÇÃO E ORDENAÇÃO PADRONIZADAS
# =============================================================================


def pagination_controls(
    current_page: int = 1, page_size: int = 15, sort_order: str = "desc"
) -> Dict[str, Any]:
    """Controles padronizados de paginação conforme swagger."""

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        page = st.number_input(
            "Página",
            min_value=1,
            value=current_page,
            help="Número da página (padrão: 1)",
        )

    with col2:
        size = st.selectbox(
            "Itens por página",
            options=[10, 15, 20, 50],
            index=1,  # Default 15
            help="Quantidade de itens por página (padrão: 15)",
        )

    with col3:
        sort = st.selectbox(
            "Ordenação",
            options=["desc", "asc"],
            index=0,  # Default desc
            help="Ordem de classificação (padrão: decrescente)",
        )

    return {"page": cast_to_int32(page), "pageSize": cast_to_int32(size), "sort": sort}


# =============================================================================
# VALIDAÇÃO DE TARIFFS COM CRUZAMENTO DE MEIA-NOITE
# =============================================================================


def validate_tariff_times_v2(
    day_start: time, day_end: time, night_start: time, night_end: time
) -> Tuple[bool, str]:
    """Validação completa de horários de tarifa incluindo cruzamento de meia-noite."""

    # Converter para minutos para facilitar cálculos
    day_start_min = day_start.hour * 60 + day_start.minute
    day_end_min = day_end.hour * 60 + day_end.minute
    night_start_min = night_start.hour * 60 + night_start.minute
    night_end_min = night_end.hour * 60 + night_end.minute

    # Validação básica: período diurno deve ser consistente
    if day_start_min >= day_end_min:
        return False, "Horário de início diurno deve ser anterior ao fim diurno."

    # Validação: período noturno pode cruzar meia-noite
    # Ex: 18:00-06:00 (noite cruza meia-noite)
    night_crosses_midnight = night_start_min > night_end_min

    if not night_crosses_midnight:
        # Período noturno não cruza meia-noite - validação normal
        if night_start_min >= night_end_min:
            return False, "Horário de início noturno deve ser anterior ao fim noturno."

        # Verificar sobreposição entre períodos
        if not (day_end_min <= night_start_min or night_end_min <= day_start_min):
            return False, "Períodos diurno e noturno não podem se sobrepor."
    else:
        # Período noturno cruza meia-noite - validação especial
        # Verificar se não há sobreposição com período diurno
        if not (day_end_min <= night_start_min and night_end_min <= day_start_min):
            return (
                False,
                "Período noturno (que cruza meia-noite) não pode sobrepor o período diurno.",
            )

    return True, "Horários de tarifa válidos."


# Manter compatibilidade
validate_tariff_times = validate_tariff_times_v2


# =============================================================================
# PERSISTÊNCIA DE FORMULÁRIO
# =============================================================================


def save_form_state(form_key: str, form_data: Dict[str, Any]):
    """Salva estado do formulário para recuperação em caso de erro."""
    st.session_state[f"form_backup_{form_key}"] = form_data


def restore_form_state(form_key: str) -> Optional[Dict[str, Any]]:
    """Restaura estado do formulário salvo."""
    return st.session_state.get(f"form_backup_{form_key}")


def clear_form_state(form_key: str):
    """Limpa estado do formulário após sucesso."""
    if f"form_backup_{form_key}" in st.session_state:
        del st.session_state[f"form_backup_{form_key}"]


# =============================================================================
# SEGURANÇA - INPUTS DE SENHA
# =============================================================================


def secure_password_input(
    label: str, help_text: str = "", placeholder: str = ""
) -> str:
    """Input seguro de senha - não persiste em session_state."""
    return st.text_input(
        label,
        type="password",
        help=help_text or "Digite uma senha segura (mín. 8 caracteres)",
        placeholder=placeholder or "Digite sua senha",
        autocomplete="new-password",  # Evita autocomplete do browser
    )


# =============================================================================
# INVALIDAÇÃO DE CACHE PÓS-MUTATION
# =============================================================================


def invalidate_caches_after_mutation(entity_type: str):
    """Invalida caches relevantes após create/update/delete."""
    cache_manager.invalidate_cache(entity_type)
    cache_manager.invalidate_dependent_caches(entity_type)

    # Force rerun para refletir mudanças
    st.rerun()


# =============================================================================
# NAVEGAÇÃO 3.2.2 - RÓTULOS PT-BR CLAROS
# =============================================================================

NAVIGATION_LABELS = {
    "Monitoramento": {
        "icon": "📊",
        "sections": {
            "dashboard": "Painel Principal",
            "measurements": "Medições dos Sensores",
            "measurement_reports": "Relatórios de Medições",
            "health": "Status dos Dispositivos",
        },
    },
    "Controle": {
        "icon": "🎮",
        "sections": {
            "controllers": "Controladores de Bomba",
            "controller_activations": "Ativações de Bomba",
            "valves": "Válvulas de Irrigação",
        },
    },
    "Consumo": {
        "icon": "⚡",
        "sections": {
            "energy_consumptions": "Consumo de Energia",
            "water_consumptions": "Consumo de Água",
        },
    },
    "Configuração": {
        "icon": "⚙️",
        "sections": {
            "monitoring_stations": "Estações de Monitoramento",
            "tariff_schedules": "Tarifas de Energia",
        },
    },
    "Sistema": {"icon": "👥", "sections": {"users": "Usuários do Sistema"}},
}


def get_navigation_label(module_name: str) -> str:
    """Retorna rótulo PT-BR claro para módulo de navegação."""
    for category, data in NAVIGATION_LABELS.items():
        if module_name in data["sections"]:
            return data["sections"][module_name]
    return module_name.replace("_", " ").title()


# ========== FORMBUILDER CLASS ==========

class FormBuilder:
    """
    Sistema de formulários padronizados com validação e styling unificado
    """
    
    def __init__(self, form_id: str, title: str, description: str = None):
        self.form_id = form_id
        self.title = title
        self.description = description
        self.fields = []
        self.validators = []
        self.submit_button_config = {
            "label": "✅ Salvar",
            "type": "primary",
            "use_container_width": True
        }
    
    def add_text_field(self, label: str, key: str = None, placeholder: str = "", 
                       help_text: str = "", required: bool = False, max_chars: int = None):
        """Adiciona campo de texto"""
        self.fields.append({
            "type": "text",
            "label": label + (" *" if required else ""),
            "key": key or f"{self.form_id}_{label.lower().replace(' ', '_')}",
            "placeholder": placeholder,
            "help": help_text,
            "required": required,
            "max_chars": max_chars
        })
        return self
    
    def add_number_field(self, label: str, key: str = None, min_value: float = None,
                        max_value: float = None, value: float = None, step: float = None,
                        help_text: str = "", required: bool = False):
        """Adiciona campo numérico"""
        self.fields.append({
            "type": "number",
            "label": label + (" *" if required else ""),
            "key": key or f"{self.form_id}_{label.lower().replace(' ', '_')}",
            "min_value": min_value,
            "max_value": max_value,
            "value": value,
            "step": step,
            "help": help_text,
            "required": required
        })
        return self
    
    def add_selectbox(self, label: str, options: List[str], key: str = None,
                     index: int = 0, help_text: str = "", required: bool = False):
        """Adiciona campo de seleção"""
        self.fields.append({
            "type": "selectbox",
            "label": label + (" *" if required else ""),
            "key": key or f"{self.form_id}_{label.lower().replace(' ', '_')}",
            "options": options,
            "index": index,
            "help": help_text,
            "required": required
        })
        return self
        
    def add_date_field(self, label: str, key: str = None, value: date = None,
                      min_value: date = None, max_value: date = None,
                      help_text: str = "", required: bool = False):
        """Adiciona campo de data"""
        self.fields.append({
            "type": "date",
            "label": label + (" *" if required else ""),
            "key": key or f"{self.form_id}_{label.lower().replace(' ', '_')}",
            "value": value,
            "min_value": min_value,
            "max_value": max_value,
            "help": help_text,
            "required": required
        })
        return self
    
    def add_checkbox(self, label: str, key: str = None, value: bool = False,
                    help_text: str = ""):
        """Adiciona checkbox"""
        self.fields.append({
            "type": "checkbox",
            "label": label,
            "key": key or f"{self.form_id}_{label.lower().replace(' ', '_')}",
            "value": value,
            "help": help_text
        })
        return self
    
    def add_validator(self, field_key: str, validator_func, error_message: str):
        """Adiciona validador customizado"""
        self.validators.append({
            "field_key": field_key,
            "validator": validator_func,
            "error_message": error_message
        })
        return self
    
    def set_submit_button(self, label: str = "✅ Salvar", button_type: str = "primary"):
        """Configura botão de submit"""
        self.submit_button_config = {
            "label": label,
            "type": button_type,
            "use_container_width": True
        }
        return self
    
    def render(self) -> Tuple[Dict[str, Any], bool]:
        """Renderiza o formulário e retorna valores + status de submit"""
        
        # CSS styling para o form
        st.markdown(f"""
        <style>
        .form-container {{
            background-color: {get_color("background.primary")};
            padding: {get_spacing("6")};
            border-radius: {DesignTokens.RADIUS["lg"]};
            box-shadow: {get_shadow("base")};
            margin-bottom: {get_spacing("6")};
        }}
        .form-title {{
            color: {get_color("text.primary")};
            font-family: {DesignTokens.TYPOGRAPHY["font_families"]["heading"]};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["2xl"]};
            font-weight: {DesignTokens.TYPOGRAPHY["weights"]["bold"]};
            margin-bottom: {get_spacing("2")};
        }}
        .form-description {{
            color: {get_color("text.secondary")};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["base"]};
            margin-bottom: {get_spacing("6")};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            # Título e descrição
            st.markdown(f'<h2 class="form-title">{self.title}</h2>', unsafe_allow_html=True)
            if self.description:
                st.markdown(f'<p class="form-description">{self.description}</p>', unsafe_allow_html=True)
            
            with st.form(self.form_id):
                values = {}
                
                # Renderizar campos
                for field in self.fields:
                    if field["type"] == "text":
                        values[field["key"]] = st.text_input(
                            field["label"],
                            key=field["key"],
                            placeholder=field.get("placeholder", ""),
                            help=field.get("help", ""),
                            max_chars=field.get("max_chars")
                        )
                    
                    elif field["type"] == "number":
                        values[field["key"]] = st.number_input(
                            field["label"],
                            key=field["key"],
                            min_value=field.get("min_value"),
                            max_value=field.get("max_value"),
                            value=field.get("value"),
                            step=field.get("step"),
                            help=field.get("help", "")
                        )
                    
                    elif field["type"] == "selectbox":
                        values[field["key"]] = st.selectbox(
                            field["label"],
                            field["options"],
                            key=field["key"],
                            index=field.get("index", 0),
                            help=field.get("help", "")
                        )
                    
                    elif field["type"] == "date":
                        values[field["key"]] = st.date_input(
                            field["label"],
                            key=field["key"],
                            value=field.get("value"),
                            min_value=field.get("min_value"),
                            max_value=field.get("max_value"),
                            help=field.get("help", "")
                        )
                    
                    elif field["type"] == "checkbox":
                        values[field["key"]] = st.checkbox(
                            field["label"],
                            key=field["key"],
                            value=field.get("value", False),
                            help=field.get("help", "")
                        )
                
                # Botão de submit com styling
                st.markdown(generate_button_styles(), unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    self.submit_button_config["label"],
                    type=self.submit_button_config["type"],
                    use_container_width=self.submit_button_config["use_container_width"]
                )
                
                # Validação
                if submitted:
                    errors = []
                    
                    # Validações de required
                    for field in self.fields:
                        if field.get("required", False):
                            field_value = values.get(field["key"])
                            if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                                errors.append(f"Campo '{field['label']}' é obrigatório.")
                    
                    # Validações customizadas
                    for validator in self.validators:
                        field_value = values.get(validator["field_key"])
                        if not validator["validator"](field_value):
                            errors.append(validator["error_message"])
                    
                    # Exibir erros
                    if errors:
                        for error in errors:
                            st.error(error)
                        return values, False
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        return values, submitted


# ========== COMPONENT LIBRARY ==========

class ComponentLibrary:
    """
    Biblioteca de componentes visuais padronizados
    """
    
    @staticmethod
    def card(title: str, content: str, actions: List[Dict] = None, 
             icon: str = None, color: str = "primary"):
        """
        Card padronizado com título, conteúdo e ações opcionais
        """
        card_color = get_color(color)
        
        st.markdown(f"""
        <style>
        .custom-card {{
            background-color: {get_color("background.primary")};
            padding: {get_spacing("6")};
            border-radius: {DesignTokens.RADIUS["lg"]};
            box-shadow: {get_shadow("md")};
            border-left: 4px solid {card_color};
            margin-bottom: {get_spacing("4")};
        }}
        .card-title {{
            color: {card_color};
            font-family: {DesignTokens.TYPOGRAPHY["font_families"]["heading"]};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["lg"]};
            font-weight: {DesignTokens.TYPOGRAPHY["weights"]["semibold"]};
            margin-bottom: {get_spacing("3")};
        }}
        .card-content {{
            color: {get_color("text.primary")};
            line-height: {DesignTokens.TYPOGRAPHY["line_heights"]["relaxed"]};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            
            # Título com ícone opcional
            title_html = f"{icon} {title}" if icon else title
            st.markdown(f'<h3 class="card-title">{title_html}</h3>', unsafe_allow_html=True)
            
            # Conteúdo
            st.markdown(f'<div class="card-content">{content}</div>', unsafe_allow_html=True)
            
            # Ações (botões)
            if actions:
                st.markdown("<br>", unsafe_allow_html=True)
                cols = st.columns(len(actions))
                for i, action in enumerate(actions):
                    with cols[i]:
                        if st.button(action["label"], key=action.get("key", f"action_{i}")):
                            if action.get("callback"):
                                action["callback"]()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def metric_card(title: str, value: str, delta: str = None, 
                   delta_color: str = "normal", icon: str = "📊"):
        """
        Card de métrica com valor, delta e ícone
        """
        delta_colors = {
            "normal": get_color("success"),
            "inverse": get_color("error"),
            "off": get_color("text.secondary")
        }
        
        st.markdown(f"""
        <style>
        .metric-card {{
            background: linear-gradient(135deg, {get_color("primary")}15 0%, {get_color("background.primary")} 100%);
            padding: {get_spacing("6")};
            border-radius: {DesignTokens.RADIUS["xl"]};
            box-shadow: {get_shadow("lg")};
            text-align: center;
            margin-bottom: {get_spacing("4")};
        }}
        .metric-icon {{
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["3xl"]};
            margin-bottom: {get_spacing("2")};
        }}
        .metric-title {{
            color: {get_color("text.secondary")};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["sm"]};
            font-weight: {DesignTokens.TYPOGRAPHY["weights"]["medium"]};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: {get_spacing("2")};
        }}
        .metric-value {{
            color: {get_color("text.primary")};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["4xl"]};
            font-weight: {DesignTokens.TYPOGRAPHY["weights"]["bold"]};
            margin-bottom: {get_spacing("2")};
        }}
        .metric-delta {{
            color: {delta_colors.get(delta_color, delta_colors["normal"])};
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["sm"]};
            font-weight: {DesignTokens.TYPOGRAPHY["weights"]["semibold"]};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                {f'<div class="metric-delta">{delta}</div>' if delta else ''}
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def alert(message: str, alert_type: str = "info", dismissible: bool = True):
        """
        Alerta padronizado com diferentes tipos
        """
        type_configs = {
            "info": {"color": get_color("info"), "icon": "ℹ️"},
            "success": {"color": get_color("success"), "icon": "✅"},
            "warning": {"color": get_color("warning"), "icon": "⚠️"},
            "error": {"color": get_color("error"), "icon": "❌"}
        }
        
        config = type_configs.get(alert_type, type_configs["info"])
        
        st.markdown(f"""
        <style>
        .custom-alert {{
            background-color: {config["color"]}15;
            border: 1px solid {config["color"]}50;
            border-left: 4px solid {config["color"]};
            color: {get_color("text.primary")};
            padding: {get_spacing("4")};
            border-radius: {DesignTokens.RADIUS["md"]};
            margin-bottom: {get_spacing("4")};
            display: flex;
            align-items: center;
            gap: {get_spacing("3")};
        }}
        .alert-icon {{
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["lg"]};
        }}
        .alert-message {{
            flex: 1;
            font-size: {DesignTokens.TYPOGRAPHY["sizes"]["base"]};
            line-height: {DesignTokens.TYPOGRAPHY["line_heights"]["normal"]};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="custom-alert">
            <div class="alert-icon">{config["icon"]}</div>
            <div class="alert-message">{message}</div>
        </div>
        """, unsafe_allow_html=True)


# ========== ENHANCED LOADING STATES ==========

class LoadingStates:
    """
    Estados de loading avançados com progress e cancelamento
    """
    
    @staticmethod
    @contextmanager
    def progress_with_status(title: str, total_steps: int = 100):
        """Loading com barra de progresso e status textual"""
        
        # Container para o loading
        loading_container = st.container()
        
        with loading_container:
            st.markdown(f"""
            <style>
            .loading-container {{
                background-color: {get_color("background.secondary")};
                padding: {get_spacing("6")};
                border-radius: {DesignTokens.RADIUS["lg"]};
                text-align: center;
                margin: {get_spacing("4")} 0;
            }}
            .loading-title {{
                color: {get_color("text.primary")};
                font-size: {DesignTokens.TYPOGRAPHY["sizes"]["lg"]};
                font-weight: {DesignTokens.TYPOGRAPHY["weights"]["semibold"]};
                margin-bottom: {get_spacing("4")};
            }}
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="loading-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="loading-title">{title}</div>', unsafe_allow_html=True)
            
            # Elementos de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        try:
            yield progress_bar, status_text, loading_container
        finally:
            loading_container.empty()
    
    @staticmethod
    @contextmanager
    def spinner_with_cancel(message: str, cancel_callback=None):
        """Spinner com opção de cancelamento"""
        
        col1, col2 = st.columns([4, 1])
        
        with col2:
            if cancel_callback and st.button("❌ Cancelar", key="cancel_loading"):
                cancel_callback()
                st.stop()
        
        with col1:
            with st.spinner(message):
                yield


# ========== ENHANCED EMPTY STATES ==========

def enhanced_empty_state(title: str, description: str, action_button: Dict = None, 
                        icon: str = "📭", illustration: str = None):
    """
    Estado vazio informativo com call-to-action opcional
    """
    
    st.markdown(f"""
    <style>
    .empty-state {{
        text-align: center;
        padding: {get_spacing("12")} {get_spacing("6")};
        background-color: {get_color("background.secondary")};
        border-radius: {DesignTokens.RADIUS["xl"]};
        margin: {get_spacing("8")} 0;
    }}
    .empty-icon {{
        font-size: {DesignTokens.TYPOGRAPHY["sizes"]["5xl"]};
        margin-bottom: {get_spacing("4")};
        opacity: 0.7;
    }}
    .empty-title {{
        color: {get_color("text.primary")};
        font-family: {DesignTokens.TYPOGRAPHY["font_families"]["heading"]};
        font-size: {DesignTokens.TYPOGRAPHY["sizes"]["2xl"]};
        font-weight: {DesignTokens.TYPOGRAPHY["weights"]["bold"]};
        margin-bottom: {get_spacing("3")};
    }}
    .empty-description {{
        color: {get_color("text.secondary")};
        font-size: {DesignTokens.TYPOGRAPHY["sizes"]["base"]};
        line-height: {DesignTokens.TYPOGRAPHY["line_heights"]["relaxed"]};
        margin-bottom: {get_spacing("6")};
        max-width: 480px;
        margin-left: auto;
        margin-right: auto;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de ação opcional
    if action_button:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(action_button["label"], type="primary", use_container_width=True):
                if action_button.get("callback"):
                    action_button["callback"]()
