# GUIA DE PADRÕES UI - IRRIGOSYSTEM DASHBOARD

## OBJETIVO
Este guia estabelece padrões consistentes para todos os componentes de interface, baseado na especificação OpenAPI Swagger e nas melhores práticas de UX.

---

## 1. DATAS E HORÁRIOS

### 1.1 Controles de Data
**Usar sempre `st.date_input()` para campos de data.**

```python
# ✅ CORRETO
start_date = st.date_input(
    "Data de Início *", 
    value=date.today() - timedelta(days=7),
    help="Selecione a data inicial do período"
)

# ❌ INCORRETO  
start_date = st.text_input("Data (Formato: YYYY-MM-DD)")
```

### 1.2 Controles de Horário
**Usar sempre `st.time_input()` para campos de horário.**

```python
# ✅ CORRETO
start_time = st.time_input(
    "Início (Diurno) *",
    value=time(6, 0),
    help="Horário de início do período diurno"
)

# ❌ INCORRETO
start_time = st.text_input("Início (Diurno)", value="06:00:00")
```

### 1.3 Intervalos de Data (Períodos)
**Implementar sempre validação de range e defaults sensatos.**

```python
# Defaults recomendados
end_date_default = date.today()
start_date_default = end_date_default - timedelta(days=7)

# Validação obrigatória
if start_date > end_date:
    st.error("Data de início deve ser anterior à data de fim.")
    return

# Limite máximo de faixa (quando necessário)
if (end_date - start_date).days > 62:
    st.error("Período máximo permitido é de 62 dias.")
    return
```

### 1.4 Fuso Horário e Formatos
- **Display**: `dd/MM/yyyy HH:mm:ss` (formato brasileiro)
- **API**: ISO-8601 UTC Z (`2025-01-23T14:30:00Z`)
- **Conversão**: Sempre converter para UTC ao enviar para API

```python
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
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return iso_string
```

---

## 2. CAMPOS NUMÉRICOS

### 2.1 Identificadores (IDs)
**Sempre usar seletores em vez de input manual.**

```python
# ✅ CORRETO - Seletor com nome + ID
controller_options = {
    f"{ctrl['name']} (ID: {ctrl['id']})": ctrl['id']
    for ctrl in controllers
}
selected_id = st.selectbox("Selecione o Controlador *", controller_options.keys())

# ❌ INCORRETO - Input manual
controller_id = st.number_input("ID do Controlador", min_value=1)
```

### 2.2 Valores Monetários
**Step adequado e validação de range.**

```python
# ✅ CORRETO
tariff = st.number_input(
    "Tarifa (R$/kWh) *",
    min_value=0.01,
    max_value=10.00,
    step=0.01,
    format="%.4f",
    help="Valor da tarifa em reais por quilowatt-hora"
)

# ❌ INCORRETO
tariff = st.number_input("Tarifa", step=0.1)
```

### 2.3 Percentuais
**Validação de range 0-100.**

```python
# ✅ CORRETO
discount = st.number_input(
    "Desconto (%)",
    min_value=0.0,
    max_value=100.0,
    step=0.1,
    format="%.1f",
    help="Percentual de desconto (0 a 100%)"
)

# ❌ INCORRETO
discount = st.number_input("Desconto", step=0.1)
```

### 2.4 Coordenadas Geográficas
**Validação de range geográfico.**

```python
# ✅ CORRETO
latitude = st.number_input(
    "Latitude *",
    min_value=-90.0,
    max_value=90.0,
    format="%.6f",
    value=-23.5505,  # Default São Paulo
    help="Coordenada de latitude (-90 a 90)"
)

longitude = st.number_input(
    "Longitude *", 
    min_value=-180.0,
    max_value=180.0,
    format="%.6f",
    value=-46.6333,  # Default São Paulo
    help="Coordenada de longitude (-180 a 180)"
)

# ❌ INCORRETO
latitude = st.number_input("Latitude", format="%.6f")
```

### 2.5 Potências e Medidas Físicas
**Unidades claras e validação de domínio.**

```python
# ✅ CORRETO
pump_power = st.number_input(
    "Potência da Bomba (W) *",
    min_value=1.0,
    max_value=50000.0,  # 50kW máximo
    step=1.0,
    help="Potência nominal em watts"
)

efficiency = st.number_input(
    "Eficiência *",
    min_value=0.01,
    max_value=1.0,
    step=0.01,
    format="%.2f",
    help="Eficiência da bomba (0.01 a 1.00)"
)
```

---

## 3. SELETORES E IDs

### 3.1 Padrão de Exibição
**Formato obrigatório: "Nome (ID: X)"**

```python
# ✅ CORRETO - Controladores
controller_options = {
    f"{ctrl['name']} (ID: {ctrl['id']})": ctrl['id']
    for ctrl in controllers
}

# ✅ CORRETO - Tarifas  
tariff_options = {
    f"{tariff['date'][:10]} (ID: {tariff['id']})": tariff['id']
    for tariff in tariffs
}

# ❌ INCORRETO - Apenas IDs
controller_ids = [ctrl['id'] for ctrl in controllers]
```

### 3.2 Seletores Dependentes
**Desabilitar até selecionar o pai.**

```python
# ✅ CORRETO
station_id = st.selectbox("Selecione a Estação *", station_options.keys())

if station_id:
    sensors = get_sensors_by_station(token, station_id)
    sensor_options = {f"Sensor #{s['id']}": s['id'] for s in sensors}
    sensor_id = st.selectbox("Selecione o Sensor", sensor_options.keys())
else:
    st.info("Selecione uma estação primeiro para carregar os sensores.")
    sensor_id = None
```

### 3.3 Cache e Performance
**Cache leve para listas (60-120s).**

```python
@st.cache_data(ttl=120)  # 2 minutos
def get_controllers_cached(token):
    return get_controllers(token)

# Usar em seletores
controllers = get_controllers_cached(token)
```

### 3.4 Opções "Todos" para Filtros
**Quando aplicável, oferecer opção de não filtrar.**

```python
# ✅ CORRETO - Filtros opcionais
filter_options = {"Todos os Controladores": None}
filter_options.update({
    f"{ctrl['name']} (ID: {ctrl['id']})": ctrl['id']
    for ctrl in controllers
})

selected = st.selectbox("Filtrar por Controlador", filter_options.keys())
controller_id = filter_options[selected]  # None = não filtra
```

---

## 4. PAGINAÇÃO E ORDENAÇÃO

### 4.1 Parâmetros Padrão do Swagger
**Usar sempre os padrões definidos na API.**

```python
# ✅ PADRÕES OBRIGATÓRIOS
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 15  
DEFAULT_SORT = "desc"

# Implementação
def fetch_data(page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE, sort=DEFAULT_SORT):
    params = {
        "page": page,
        "pageSize": page_size, 
        "sort": sort
    }
```

### 4.2 Controles de Paginação
**Mostrar controles quando há mais dados.**

```python
# ✅ CORRETO
if len(data) >= DEFAULT_PAGE_SIZE:  # Página completa = tem mais dados
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Carregar Mais Dados", use_container_width=True):
            load_more_data()
            st.rerun()
```

### 4.3 Indicadores de Estado
**Feedback visual durante carregamento.**

```python
# ✅ CORRETO
with st.spinner("Carregando dados..."):
    data = fetch_data()

if data.empty:
    st.info("📭 Nenhum resultado encontrado para os filtros informados.")
else:
    st.dataframe(data, use_container_width=True)
```

---

## 5. MENSAGENS E ESTADOS

### 5.1 Estados de Carregamento
```python
# ✅ PADRÕES DE MENSAGENS
LOADING = "Carregando..."
EMPTY = "Nenhum resultado encontrado para os filtros informados."
ERROR_CONNECTION = "Erro ao conectar com a API. Tente novamente."
ERROR_AUTH = "Usuário não autenticado."
```

### 5.2 Mapeamento de Status Codes HTTP
```python
def handle_api_response(response, success_message="Operação realizada com sucesso!"):
    """Padroniza tratamento de respostas da API."""
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
        500: "Erro interno do servidor. Tente novamente em alguns minutos."
    }
    
    message = status_messages.get(response.status_code, 
                                f"Erro inesperado: {response.status_code}")
    
    if 200 <= response.status_code < 300:
        st.success(message)
        return True
    else:
        st.error(message)
        return False
```

### 5.3 Validações e Erros
**Validação client-side before submit.**

```python
# ✅ CORRETO - Validação prévia
def validate_form_data(name, email, password, confirm_password):
    errors = []
    
    if not name.strip():
        errors.append("Nome é obrigatório.")
    
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append("Email deve ter formato válido.")
        
    if len(password) < 8:
        errors.append("Senha deve ter pelo menos 8 caracteres.")
        
    if password != confirm_password:
        errors.append("Senhas não conferem.")
    
    return errors

# Uso no formulário
if st.form_submit_button("Salvar"):
    errors = validate_form_data(name, email, password, confirm_password)
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Proceed with API call
```

---

## 6. ACESSIBILIDADE E USABILIDADE

### 6.1 Campos Obrigatórios
**Marcar sempre com asterisco (*).**

```python
# ✅ CORRETO
name = st.text_input(
    "Nome *", 
    help="Nome do controlador (obrigatório)",
    placeholder="Digite o nome do controlador"
)

# ❌ INCORRETO
name = st.text_input("Nome")
```

### 6.2 Help Text e Placeholders
**Orientação clara para campos complexos.**

```python
# ✅ CORRETO
email = st.text_input(
    "Email *",
    placeholder="usuario@exemplo.com",
    help="Endereço de email válido para login"
)

password = st.text_input(
    "Senha *", 
    type="password",
    help="Mínimo 8 caracteres, incluindo letras e números",
    placeholder="Digite sua senha"
)
```

### 6.3 Títulos e Seções
**Hierarquia clara e títulos em PT-BR.**

```python
# ✅ CORRETO
st.title("Gerenciamento de Controladores")  # H1
st.subheader("Criar Novo Controlador")      # H2  
st.markdown("### Dados Básicos")            # H3

# ❌ INCORRETO
st.write("## Create Controller")  # Inglês
```

### 6.4 Layout Responsivo
**Colunas adequadas para diferentes telas.**

```python
# ✅ CORRETO - Layout adaptativo
col1, col2 = st.columns([2, 1])  # Proporção 2:1
with col1:
    name = st.text_input("Nome *")
with col2:
    status = st.selectbox("Status", ["Ativo", "Inativo"])

# Para formulários complexos
col1, col2, col3 = st.columns(3)
# Distribua campos relacionados
```

---

## 7. VALIDAÇÕES POR TIPO DE CAMPO

### 7.1 Email
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### 7.2 Senhas
```python
def validate_password(password):
    """
    Regras: mín 8 chars, pelo menos 1 letra, 1 número
    """
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres."
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Senha deve conter pelo menos uma letra."
        
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número."
    
    return True, "Senha válida."
```

### 7.3 Coordenadas Geográficas
```python
def validate_coordinates(lat, lon):
    """Valida se coordenadas estão em ranges válidos."""
    if not (-90 <= lat <= 90):
        return False, "Latitude deve estar entre -90 e 90 graus."
    
    if not (-180 <= lon <= 180):  
        return False, "Longitude deve estar entre -180 e 180 graus."
    
    return True, "Coordenadas válidas."
```

---

## 8. COMPONENTES REUTILIZÁVEIS

### 8.1 Seletor de Controlador Padrão
```python
def controller_selector(token, label="Selecione o Controlador *", 
                       include_all_option=False, cache_ttl=120):
    """Seletor padronizado de controladores."""
    
    @st.cache_data(ttl=cache_ttl)
    def get_controllers_cached(token):
        return get_controllers(token)
    
    controllers = get_controllers_cached(token)
    if not controllers:
        st.warning("Nenhum controlador cadastrado.")
        return None, None
        
    options = {}
    if include_all_option:
        options["Todos os Controladores"] = None
        
    options.update({
        f"{ctrl['name']} (ID: {ctrl['id']})": ctrl['id']
        for ctrl in controllers
    })
    
    choice = st.selectbox(label, options.keys())
    return options[choice], choice
```

### 8.2 Filtro de Data Padrão
```python
def date_range_filter(default_days=7, max_days=62):
    """Filtro padronizado de range de datas."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Data de Início *",
            value=date.today() - timedelta(days=default_days),
            help=f"Data inicial do período (máx {max_days} dias)"
        )
    
    with col2:
        end_date = st.date_input(
            "Data de Fim *",
            value=date.today(),
            help="Data final do período"
        )
    
    # Validação
    if start_date > end_date:
        st.error("Data de início deve ser anterior à data de fim.")
        return None, None
        
    if (end_date - start_date).days > max_days:
        st.error(f"Período máximo permitido é de {max_days} dias.")
        return None, None
    
    return start_date, end_date
```

---

## 9. CHECKLIST DE IMPLEMENTAÇÃO

### ✅ Antes de Implementar
- [ ] Conferir parâmetros no Swagger
- [ ] Definir validações necessárias  
- [ ] Escolher controles adequados
- [ ] Definir defaults sensatos
- [ ] Planejar mensagens de erro

### ✅ Durante Implementação
- [ ] Usar componentes padronizados
- [ ] Implementar validação client-side
- [ ] Adicionar help text adequado
- [ ] Marcar campos obrigatórios (*)
- [ ] Testar todos os fluxos de erro

### ✅ Após Implementação  
- [ ] Testar com dados inválidos
- [ ] Verificar responsividade
- [ ] Validar acessibilidade básica
- [ ] Conferir consistência visual
- [ ] Documentar componentes novos

---

**Versão**: 1.0  
**Última Atualização**: 23/08/2025  
**Próxima Revisão**: Após aplicação da Fase 2