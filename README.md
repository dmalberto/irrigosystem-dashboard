# IrrigoSystem Dashboard

> Sistema de monitoramento e automação para irrigação inteligente

## Sobre o Projeto

O IrrigoSystem Dashboard é uma aplicação web desenvolvida em Streamlit que permite o controle e monitoramento completo de sistemas de irrigação inteligente. O sistema gerencia estações de monitoramento, sensores de umidade, controladores de irrigação e fornece análises detalhadas de consumo.

## Funcionalidades Principais

### 🏭 Monitoramento
- **Estações de Monitoramento**: Cadastro e gerenciamento de estações
- **Sensores**: CRUD completo de sensores por estação  
- **Medições**: Visualização e análise de dados de umidade do solo
- **Relatórios**: Relatórios customizáveis com filtros avançados

### ⚙️ Controle de Irrigação
- **Controladores**: Gerenciamento de controladores de irrigação
- **Válvulas**: Configuração e controle de válvulas por controlador
- **Ativações**: Histórico completo de ativações do sistema
- **Automação**: Controle automatizado baseado em dados dos sensores

### 📊 Análise de Consumo
- **Energia**: Monitoramento de consumo energético dos equipamentos
- **Água**: Controle de consumo hídrico por período
- **Tarifas**: Configuração de tarifas elétricas dinâmicas
- **Relatórios**: Análises comparativas e projeções de consumo

### 👥 Gestão de Sistema
- **Usuários**: Sistema de autenticação e gerenciamento de usuários
- **Dashboard**: Visão geral do sistema com métricas principais
- **Health Check**: Monitoramento da saúde da API

## Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip ou conda
- Git

### Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd irrigosystem-dashboard
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

## Configuração de Ambiente

### Variáveis Obrigatórias

```env
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Authentication
JWT_SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT=3600

# Database (se aplicável)
DATABASE_URL=your-database-url

# Cache Configuration
CACHE_TTL=300
ENABLE_CACHE=true
```

## Estrutura do Projeto

```
├── app.py                     # Aplicação principal Streamlit
├── api.py                     # Cliente HTTP centralizado
├── login.py                   # Sistema de autenticação
├── swagger.yml                # Especificação OpenAPI 3.0.1
├── requirements.txt           # Dependências Python
├── .env.example              # Template de configuração
├── src/
│   ├── ui_components.py      # Componentes de interface reutilizáveis
│   ├── design_tokens.py      # Sistema de design (cores, tipografia)
│   ├── dashboard.py          # Dashboard principal
│   ├── controllers.py        # Gestão de controladores
│   ├── valves.py             # Gestão de válvulas
│   ├── controller_activations.py  # Histórico de ativações
│   ├── monitoring_stations.py     # Estações de monitoramento
│   ├── measurements.py             # Medições e sensores
│   ├── measurement_reports.py      # Relatórios de medições
│   ├── consumptions.py             # Análise de consumo
│   ├── energy_consumptions.py      # Consumo de energia
│   ├── water_consumptions.py       # Consumo de água
│   ├── tariff_schedules.py         # Tarifas elétricas
│   ├── users.py                   # Gestão de usuários
│   └── health.py                  # Health checks
└── tests/
    ├── test_controller_activations_contract.py
    ├── test_measurements_export_contract.py
    └── test_monitoring_stations_crud_contract.py
```

## API e Integração

### Cliente HTTP

O sistema utiliza um cliente HTTP centralizado (`api.py`) que gerencia:

- **Autenticação**: Tokens JWT automáticos
- **Rate Limiting**: Controle de taxa com retry
- **Error Handling**: Tratamento padronizado de erros HTTP
- **Timeout**: Configuração flexível de timeout
- **Logging**: Log detalhado de requests/responses

### Endpoints Principais

| Funcionalidade | Método | Endpoint | Parâmetros |
|----------------|---------|----------|------------|
| **Controladores** | GET/POST/PUT/DELETE | `/api/controllers` | id (int64) |
| **Válvulas** | GET/POST/PUT/DELETE | `/api/controllers/{id}/valves` | controllerId, id |
| **Estações** | GET/POST/PUT/DELETE | `/api/monitoring-stations` | id (int64) |
| **Sensores** | GET/POST/PUT/DELETE | `/api/monitoring-stations/{id}/sensors` | stationId, sensorId |
| **Medições** | GET | `/api/measurements` | dateRange, pagination |
| **Consumo** | GET | `/api/consumptions/energy` | controllerId, period |
| **Ativações** | GET | `/api/controllers/{id}/activations` | controllerId, period |
| **Usuários** | GET/POST/DELETE | `/api/users` | email |

### Tipos de Dados

O sistema segue rigorosamente a especificação Swagger:

- **int32**: IDs de sensores, páginas, tamanhos
- **int64**: IDs de controladores, estações  
- **double**: Coordenadas, limites, valores de medição
- **date-time**: Timestamps em formato ISO-8601
- **string**: Nomes, descrições, períodos

## Interface do Usuário

### Componentes Reutilizáveis

```python
# Exemplos de uso dos componentes
from src.ui_components import ComponentLibrary

# Card informativo
ComponentLibrary.metric_card(
    title="Total Controladores",
    value="12",
    icon="⚙️"
)

# Estado vazio
enhanced_empty_state(
    title="Nenhuma estação cadastrada",
    message="Comece criando sua primeira estação",
    icon="🏭"
)

# Seletor padronizado
controller_id, name = controller_selector(
    token, 
    label="Selecione o Controlador",
    include_all_option=True
)
```

### Design System

O projeto utiliza um sistema de design consistente:

```python
# design_tokens.py
COLORS = {
    'primary': '#1f77b4',
    'success': '#28a745', 
    'warning': '#ffc107',
    'danger': '#dc3545'
}

SPACING = {
    'xs': '0.25rem',
    'sm': '0.5rem', 
    'md': '1rem',
    'lg': '1.5rem'
}
```

## Testes

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_controller_activations_contract.py -v

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

### Tipos de Teste

- **Testes Contratuais**: Validam integração com API conforme Swagger
- **Testes Unitários**: Validam funções individuais
- **Testes de Interface**: Validam comportamento da UI

## Desenvolvimento

### Adicionando Nova Funcionalidade

1. **Defina o endpoint** no `swagger.yml`
2. **Implemente a função** no módulo apropriado em `src/`
3. **Use `api_request()`** para comunicação HTTP
4. **Aplique componentes UI** do `ComponentLibrary`
5. **Adicione testes** contratuais
6. **Documente** no README se necessário

### Padrões de Código

```python
# Nomenclatura de funções
def get_controllers(token):          # ✅ Boa
def fetch_controller_data(token):    # ❌ Evitar

# Type casting conforme Swagger
station_id = cast_to_int64(raw_id)   # ✅ int64 para estações
sensor_id = cast_to_int32(raw_id)    # ✅ int32 para sensores

# Error handling
response = api_request("GET", endpoint, token=token)
if not response or response.status_code != 200:
    st.error("Erro ao carregar dados")
    return None

# Cache invalidation
invalidate_caches_after_mutation("controllers")
```

### Estrutura de Commits

```bash
# Tipos de commit
feat: nova funcionalidade
fix: correção de bug
refactor: refatoração de código
docs: atualizações de documentação
test: adição/correção de testes
chore: tarefas de manutenção
```

## Deployment

### Ambiente de Produção

1. **Configure variáveis de produção**
```env
API_BASE_URL=https://api.irrigosystem.com
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

2. **Execute com configurações otimizadas**
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
```

## Monitoramento e Logs

### Health Checks

O sistema inclui endpoints de saúde para monitoramento:

- `/api/health` - Status geral da API
- Verificações automáticas de conectividade
- Métricas de performance em tempo real

### Troubleshooting

**Problemas Comuns:**

1. **Timeout na API**
   - Verificar `API_TIMEOUT` no `.env`
   - Confirmar conectividade com backend

2. **Cache desatualizado**
   - Limpar cache: `st.cache_data.clear()`
   - Verificar `CACHE_TTL` nas configurações

3. **Errors de autenticação**
   - Verificar token JWT válido
   - Confirmar `JWT_SECRET_KEY` configurado

## Contribuição

### Como Contribuir

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Implemente as mudanças seguindo os padrões
4. Adicione testes para nova funcionalidade
5. Commit suas mudanças (`git commit -m 'feat: adicionar nova funcionalidade'`)
6. Push para a branch (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

### Diretrizes

- **Código limpo**: Siga PEP 8 e use formatação consistente
- **Documentação**: Documente funções públicas e mudanças significativas
- **Testes**: Mantenha coverage > 80%
- **Backward compatibility**: Evite breaking changes
- **Performance**: Considere impacto em performance para mudanças na UI

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para dúvidas, problemas ou sugestões:

- Abra uma [Issue](../../issues) no repositório
- Consulte a documentação da API no Swagger
- Verifique os logs da aplicação para troubleshooting

---

**Versão atual**: v2.0.0  
**Última atualização**: 2025-08-24