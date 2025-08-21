# IrrigoSystem Dashboard

Dashboard web para o sistema de irrigação inteligente IrrigoSystem, construído com Streamlit.

## Funcionalidades

- **Gerenciamento de Controladores**: CRUD completo para controladores de irrigação
- **Estações de Monitoramento**: Gerenciamento de estações e sensores
- **Consumo de Energia**: Relatórios e análises de consumo energético
- **Ativações de Bomba**: Monitoramento de ativações com análises visuais
- **Válvulas**: Gerenciamento de válvulas por controlador
- **Tarifas**: Configuração de tarifas de energia
- **Usuários**: Gerenciamento de usuários do sistema
- **Dashboard**: Visualizações em tempo real dos sensores
- **Relatórios**: Relatórios de medições e análises

## Como rodar local

### Pré-requisitos

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) ou [Anaconda](https://www.anaconda.com/)
- Git
- Windows PowerShell (ou equivalente)

### Configuração do ambiente

1. **Clone o repositório:**
   ```powershell
   git clone <url-do-repositorio>
   cd irrigosystem-dashboard
   ```

2. **Crie e ative o ambiente conda:**
   ```powershell
   conda env create -f environment.yml
   conda activate irrigosystem
   ```

3. **Execute os testes para validar a configuração:**
   ```powershell
   python -m pytest -q
   ```

4. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   API_URL=http://localhost:3000
   ```

5. **Inicie a aplicação:**
   ```powershell
   streamlit run app.py
   ```

### Estrutura do projeto

```
├── src/                    # Código fonte principal
│   ├── activations.py      # Módulo de ativações de bomba
│   ├── amostras.py         # Módulo de amostras de sensores
│   ├── consumo_energia.py  # Módulo de consumo de energia
│   ├── controllers.py      # Módulo de controladores
│   ├── dashboard.py        # Dashboard principal
│   ├── equipamentos.py     # Módulo de equipamentos
│   ├── health_check.py     # Health check do sistema
│   ├── tariff_schedules.py # Módulo de tarifas
│   ├── users.py           # Módulo de usuários
│   ├── utils.py           # Utilitários compartilhados
│   └── valves.py          # Módulo de válvulas
├── tests/                 # Testes automatizados
├── api.py                # Configurações da API
├── app.py                # Aplicação principal Streamlit
├── login.py              # Sistema de login
├── requirements.txt      # Dependências Python (pip)
├── environment.yml       # Ambiente conda reproduzível
└── swagger.yml          # Especificação da API
```

### Executando testes

Para executar todos os testes:
```powershell
python -m pytest
```

Para executar testes com mais detalhes:
```powershell
python -m pytest -v
```

Para executar apenas testes específicos:
```powershell
python -m pytest tests/test_consumo_energia.py
```

### API

O dashboard consome uma API RESTful cujas especificações estão definidas no arquivo `swagger.yml`. 

Principais endpoints:
- `/api/controllers` - Gerenciamento de controladores
- `/api/monitoring-stations` - Estações de monitoramento
- `/api/measurements` - Medições dos sensores
- `/api/energy-consumptions` - Consumo de energia
- `/api/tariff-schedules` - Tarifas de energia
- `/api/users` - Gerenciamento de usuários

### Tecnologias utilizadas

- **Frontend**: Streamlit
- **Gráficos**: Plotly
- **Dados**: Pandas
- **Requests**: HTTP client
- **Testes**: Pytest
- **Ambiente**: Conda

### Desenvolvimento

1. Ative o ambiente:
   ```powershell
   conda activate irrigosystem
   ```

2. Execute os testes antes de fazer commits:
   ```powershell
   python -m pytest -q
   ```

3. Para adicionar novas dependências:
   ```powershell
   # Instale via pip
   pip install nova-dependencia
   
   # Atualize o requirements.txt
   pip freeze > requirements.txt
   
   # Atualize o environment.yml
   conda env export > environment.yml
   ```

### Troubleshooting

**Erro de importação do módulo `src.utils`:**
- Certifique-se de estar na raiz do projeto
- Verifique se o arquivo `src/__init__.py` existe

**Erro de conexão com API:**
- Verifique se a variável `API_URL` está configurada no arquivo `.env`
- Verifique se a API está rodando no endereço especificado

**Testes falhando:**
- Execute `conda activate irrigosystem` antes dos testes
- Verifique se todas as dependências foram instaladas corretamente