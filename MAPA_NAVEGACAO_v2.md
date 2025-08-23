# MAPA DE NAVEGAÇÃO 3.2.2 - UI FOUNDATIONS v2

**Rótulos PT-BR claros e organizados por domínios conforme especificação**

---

## 📊 MONITORAMENTO

**Domínio**: Coleta e visualização de dados dos sensores de campo

### Telas/Módulos:
- **`dashboard`** → **Painel Principal**
  - *Descrição*: Visão geral do sistema com status dos dispositivos
  - *Funcionalidade*: Dashboard executivo com indicadores principais
  
- **`measurements`** → **Medições dos Sensores**  
  - *Descrição*: Consulta detalhada de medições coletadas
  - *Parâmetros Swagger*: `startDate`, `endDate`, `stationId`, `sensorId`, `page`, `pageSize`, `sort`
  - *Funcionalidade*: Listagem paginada + exportação CSV
  
- **`measurement_reports`** → **Relatórios de Medições**
  - *Descrição*: Relatórios consolidados e análises estatísticas
  - *Funcionalidade*: Médias, gráficos e comparativos
  
- **`health`** → **Status dos Dispositivos**
  - *Descrição*: Monitoramento da saúde dos equipamentos
  - *Funcionalidade*: Alertas de conectividade e falhas

---

## 🎮 CONTROLE

**Domínio**: Gerenciamento de bombas, válvulas e automação

### Telas/Módulos:
- **`controllers`** → **Controladores de Bomba**
  - *Descrição*: CRUD de controladores de irrigação
  - *Parâmetros Swagger*: `id` (int64), `name`, `pumpPower`, `efficiency`, `powerFactor`, `latitude`, `longitude`
  - *Funcionalidade*: Criar/editar/excluir controladores
  
- **`controller_activations`** → **Ativações de Bomba**
  - *Descrição*: Histórico de acionamentos das bombas
  - *Parâmetros Swagger*: `controllerId` (int64), `startDate`, `endDate`, `page`, `pageSize`, `sort`
  - *Funcionalidade*: Consulta paginada de ativações
  
- **`valves`** → **Válvulas de Irrigação**
  - *Descrição*: Gerenciamento de válvulas por controlador
  - *Parâmetros Swagger*: `controllerId` (int64), `id` (int32), `flowRate`
  - *Funcionalidade*: CRUD com seletor dependente Controller→Valve

---

## ⚡ CONSUMO

**Domínio**: Análise de consumo energético e hídrico

### Telas/Módulos:
- **`energy_consumptions`** → **Consumo de Energia**
  - *Descrição*: Análise de gastos energéticos por período
  - *Parâmetros Swagger*: `controllerId` (int64), `period`
  - *Funcionalidade*: Relatórios de custo energético
  
- **`water_consumptions`** → **Consumo de Água**
  - *Descrição*: Medição do volume de água utilizado
  - *Parâmetros Swagger*: `controllerId` (int64), `period`
  - *Funcionalidade*: Análise de eficiência hídrica

---

## ⚙️ CONFIGURAÇÃO

**Domínio**: Cadastros básicos e configurações do sistema

### Telas/Módulos:
- **`monitoring_stations`** → **Estações de Monitoramento**
  - *Descrição*: CRUD de estações e sensores associados
  - *Parâmetros Swagger*: `id` (int64), `name`, `moistureUpperLimit`, `moistureLowerLimit`, `latitude`, `longitude`, `controllerId`
  - *Funcionalidade*: Gestão de estações + seletor dependente Station→Sensor
  
- **`tariff_schedules`** → **Tarifas de Energia**
  - *Descrição*: Configuração de tarifas diurnas/noturnas
  - *Parâmetros Swagger*: `id` (int32), `date`, `daytimeStart`, `daytimeEnd`, `nighttimeStart`, `nighttimeEnd`, `daytimeTariff`, `nighttimeTariff`, `nighttimeDiscount`
  - *Funcionalidade*: CRUD de tarifas com validação de horários

---

## 👥 SISTEMA

**Domínio**: Administração de usuários e segurança

### Telas/Módulos:
- **`users`** → **Usuários do Sistema**
  - *Descrição*: Gerenciamento de contas e permissões
  - *Parâmetros Swagger*: `email`, `password`, `passwordConfirmation`, `role`
  - *Funcionalidade*: Criar/excluir usuários com validações

---

## PADRÕES DE NAVEGAÇÃO IMPLEMENTADOS

### Formato de Seletores:
- **Padrão**: `"Nome (ID: X)"` ou `"Data (ID: X)"` para tarifas
- **Exemplo**: `"Bomba Setor A (ID: 123)"`, `"15/01/2025 (ID: 5)"`

### Seletores Dependentes:
- **Estação → Sensor**: Sensor desabilitado até estação ser selecionada
- **Controlador → Válvula**: Válvula desabilitada até controlador ser selecionado

### Cache com TTL:
- **Duração**: 120 segundos para todas as listagens
- **Invalidação**: Automática após create/update/delete
- **Indicadores**: Spinners durante carregamento

### Paginação Padrão:
- **Defaults**: `page=1`, `pageSize=15`, `sort=desc`
- **Controles**: Visíveis quando suportado pela API
- **Máximos**: Configuráveis por tela (62-90 dias)

### Estados Padronizados:
- **Loading**: Spinner com mensagem contextual
- **Empty**: Ícone 📭 + mensagem explicativa
- **Error**: ⚠️ + mapeamento de códigos HTTP
- **429**: Countdown visual respeitando Retry-After

---

## CASTING POR TIPO SWAGGER

### int32:
- `sensorId`, `stationId`, `tariffId`, `page`, `pageSize`, `valve.id`

### int64:
- `controllerId`, `monitoringStation.id`, `measurement.id`

### double:
- `pumpPower`, `efficiency`, `powerFactor`, `latitude`, `longitude`, `flowRate`, `daytimeTariff`, `nighttimeTariff`, `moistureUpperLimit`, `moistureLowerLimit`

### date-time:
- `startDate`, `endDate`, `date` (todas formatadas ISO-8601 UTC Z)

---

## VALIDAÇÕES IMPLEMENTADAS

### Campos Obrigatórios:
- Marcados com `*` no label
- Placeholders informativos
- Help text explicativo

### Ranges de Valores:
- **Coordenadas**: lat (-90,90), lon (-180,180)
- **Percentuais**: 0-100% 
- **Monetários**: R$ 0,01-10,00 (step 0,01)
- **IDs**: ≥ 1 (números positivos)
- **Vazão**: > 0 L/min

### Períodos de Data:
- **Padrão**: Últimos 7 dias
- **Máximo**: 62-90 dias (conforme tela)
- **Validação**: start ≤ end

### Persistência de Formulário:
- Estado salvo em `session_state`
- Restauração em caso de erro de validação/API
- Limpeza após sucesso

---

*Mapa gerado automaticamente pelo UI Foundations v2*  
*Data: 23/08/2025*