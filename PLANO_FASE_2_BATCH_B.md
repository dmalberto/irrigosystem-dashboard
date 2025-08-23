# PLANO DA FASE 2 - BATCH B
## Aplicação dos Padrões UI (Implementação)

### OBJETIVO
Aplicar sistematicamente os padrões definidos no Guia de Padrões UI, corrigindo os 23 problemas críticos identificados na auditoria.

---

## 1. CONTROLADORES - PRIORIDADE ALTA

### 1.1 Arquivo: `src/controllers.py`

#### **Tela: Criar Controlador (show_create_controller)**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Potência (W) * | step=1.0 → step=0.1 | `step=0.1` (format double) |
| Latitude * | Adicionar validação geográfica | `min_value=-90.0, max_value=90.0, value=-23.5505` |
| Longitude * | Adicionar validação geográfica | `min_value=-180.0, max_value=180.0, value=-46.6333` |
| Todos os campos | Adicionar placeholders | `placeholder="Ex: Bomba Setor A"` |

#### **Tela: Editar Controlador (show_edit_controller)**  
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Potência (W) * | step=1.0 → step=0.1 | `step=0.1` |
| Latitude * | Adicionar validação | Range -90 a 90 |
| Longitude * | Adicionar validação | Range -180 a 180 |

**Componente Novo**: Criar `controller_form_fields()` reutilizável.

---

## 2. TARIFAS - PRIORIDADE CRÍTICA

### 2.1 Arquivo: `src/tariff_schedules.py`

#### **Tela: Criar Tarifa (show_create_tariff)**
| Campo Atual | Mudança | Implementação Nova |
|-------------|---------|-------------------|
| Data (text_input) | → date_input | `st.date_input("Data da Tarifa *", value=date.today())` |
| Início Diurno (text_input) | → time_input | `st.time_input("Início (Diurno) *", value=time(6, 0))` |
| Fim Diurno (text_input) | → time_input | `st.time_input("Fim (Diurno) *", value=time(18, 0))` |
| Início Noturno (text_input) | → time_input | `st.time_input("Início (Noturno) *", value=time(18, 0))` |
| Fim Noturno (text_input) | → time_input | `st.time_input("Fim (Noturno) *", value=time(6, 0))` |
| Tarifa Diurna (step=0.1) | → step=0.01 | `step=0.01, format="%.4f"` |
| Tarifa Noturna (step=0.1) | → step=0.01 | `step=0.01, format="%.4f"` |
| Desconto (step=0.1) | → validação % | `max_value=100.0, step=0.1, format="%.1f %%"` |

**Validação Nova**:
```python
def validate_tariff_times(day_start, day_end, night_start, night_end):
    # Lógica para validar sobreposição de horários
    pass

def format_tariff_for_api(date_val, time_start, time_end):
    # Combinar date + time → ISO format
    pass
```

#### **Tela: Editar Tarifa (show_edit_tariff)**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Seletor Tarifa | IDs apenas → Nome + ID | `f"{tariff['date'][:10]} (ID: {tariff['id']})"` |
| Data | text_input → date_input | Converter de display para date object |
| Todos os horários | text_input → time_input | Converter "HH:MM:SS" para time object |
| Tarifas | step=0.1 → step=0.01 | Format monetário |

#### **Tela: Excluir Tarifa (show_delete_tariff)**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Seletor Tarifa | IDs apenas → Nome + ID | Padrão "Data (ID: X)" |
| Botão Confirmar | Sem warning → Warning | Adicionar st.warning com detalhes |

**Componente Novo**: Criar `tariff_selector()` e `time_inputs_group()`.

---

## 3. USUÁRIOS - PRIORIDADE ALTA

### 3.1 Arquivo: `src/users.py`

#### **Tela: Criar Usuário (CreateUser)**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Email | Sem validação → Validação email | `validate_email()` + placeholder |
| Senha | Sem validação → Validação força | `validate_password()` + help text |
| Role | Hardcoded → Dinâmico | Buscar de enum/API ou manter com default |

#### **Tela: Excluir Usuário (DeleteUser)**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Email | Sem validação → Validação format | `validate_email()` |

**Validações Novas**:
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Mín 8 chars, 1 letra, 1 número
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    if not re.search(r'[A-Za-z]', password):
        return False, "Pelo menos uma letra"  
    if not re.search(r'\d', password):
        return False, "Pelo menos um número"
    return True, "Senha válida"
```

---

## 4. ATIVAÇÕES DE BOMBA - PRIORIDADE MÉDIA

### 4.1 Arquivo: `src/controller_activations.py`

#### **Seletor de Controlador**
| Campo Atual | Mudança | Implementação |
|-------------|---------|---------------|
| "Controlador #X" | → "Nome (ID: X)" | Usar `controller_selector()` padrão |

#### **Filtros de Data**
| Campo | Mudança | Implementação |
|-------|---------|---------------|
| Validação range | Adicionar limite máximo | Max 90 dias entre start/end |
| Feedback visual | Melhorar loading states | Spinner + mensagens adequadas |

**Componente**: Reutilizar `date_range_filter()` do Guia.

---

## 5. COMPONENTES REUTILIZÁVEIS - CRIAR NOVOS

### 5.1 Arquivo Novo: `src/ui_components.py`

```python
# Componentes padronizados para reutilização
def controller_selector(token, label="Selecione o Controlador *", include_all=False)
def date_range_filter(default_days=7, max_days=62)  
def tariff_selector(token, label="Selecione a Tarifa")
def validate_email(email)
def validate_password(password)
def validate_coordinates(lat, lon)
def handle_api_response(response, success_msg)
```

### 5.2 Imports Necessários
Adicionar em cada arquivo que usa componentes:
```python
from src.ui_components import controller_selector, validate_email, handle_api_response
```

---

## 6. CRONOGRAMA DE IMPLEMENTAÇÃO

### **SEMANA 1: Componentes Base**
- [ ] Criar `src/ui_components.py` 
- [ ] Implementar validações (email, password, coordinates)
- [ ] Implementar `controller_selector()` padrão
- [ ] Implementar `handle_api_response()` padrão

### **SEMANA 2: Tarifas (Crítico)**
- [ ] Refatorar `show_create_tariff()` - date/time inputs
- [ ] Refatorar `show_edit_tariff()` - seletores + validações  
- [ ] Refatorar `show_delete_tariff()` - warnings
- [ ] Testes de validação de horários sobrepostos

### **SEMANA 3: Usuários e Controladores**
- [ ] Refatorar formulários de usuários - validações
- [ ] Refatorar formulários de controladores - coordenadas
- [ ] Implementar placeholders e help text
- [ ] Testes de validação geográfica

### **SEMANA 4: Ativações e Acabamento**
- [ ] Refatorar seletores em ativações 
- [ ] Implementar filtros de data padronizados
- [ ] Testes de integração
- [ ] Revisão final e documentação

---

## 7. TESTES E VALIDAÇÃO

### 7.1 Casos de Teste por Módulo

#### **Controladores**
- [ ] Criar com coordenadas inválidas (lat > 90, lon < -180)
- [ ] Editar com potência negativa  
- [ ] Campos obrigatórios vazios
- [ ] Nomes duplicados

#### **Tarifas**
- [ ] Datas inválidas (início > fim)
- [ ] Horários sobrepostos (diurno vs noturno)
- [ ] Tarifas negativas ou zero
- [ ] Desconto > 100%

#### **Usuários**
- [ ] Emails inválidos (sem @, sem domínio) 
- [ ] Senhas fracas (< 8 chars, só números)
- [ ] Senhas não conferem
- [ ] Roles inválidos

#### **Ativações**
- [ ] Ranges de data > limite máximo
- [ ] Controlador inexistente
- [ ] Paginação com dados grandes

### 7.2 Testes de Regressão
- [ ] Todas as funcionalidades existentes continuam funcionando
- [ ] APIs recebem parâmetros nos formatos corretos
- [ ] Performance não degradou
- [ ] Layout responsivo mantido

---

## 8. MÉTRICAS DE SUCESSO

### 8.1 Quantitativas
- **Problemas Críticos**: 11/11 resolvidos (100%)
- **Problemas Importantes**: 8/8 resolvidos (100%) 
- **Conformidade Swagger**: 67% → 95%
- **Campos com Validação**: 43% → 90%

### 8.2 Qualitativas
- **UX**: Formulários intuitivos e sem frustração
- **Consistência**: Padrões aplicados uniformemente
- **Acessibilidade**: Campos claros e help text adequado
- **Manutenibilidade**: Componentes reutilizáveis criados

---

## 9. RISCOS E MITIGAÇÕES

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Quebra de APIs existentes | Alto | Baixo | Testes de regressão extensivos |
| Resistance à mudança de UX | Médio | Médio | Documentar benefícios + treinamento |
| Performance degradada | Médio | Baixo | Profiling + otimização cache |
| Validações muito rígidas | Médio | Médio | Validações graduais + feedback |

---

## 10. ENTREGÁVEIS DA FASE 2

### 10.1 Código
- [ ] `src/ui_components.py` - Componentes reutilizáveis
- [ ] `src/controllers.py` - Formulários padronizados
- [ ] `src/tariff_schedules.py` - Date/time inputs implementados
- [ ] `src/users.py` - Validações de email/senha
- [ ] `src/controller_activations.py` - Seletores padronizados

### 10.2 Documentação
- [ ] `CHANGELOG_FASE_2.md` - Log de mudanças
- [ ] `TESTES_BATCH_B.md` - Relatório de testes
- [ ] `COMPONENTES_UI.md` - Documentação dos componentes
- [ ] Atualização do `GUIA_PADROES_UI.md`

### 10.3 Validação
- [ ] Suite de testes automatizados
- [ ] Relatório de conformidade Swagger
- [ ] Benchmarks de performance
- [ ] Screenshots before/after

---

**Confirmação**: swagger.yml não será modificado nesta fase.  
**Responsável**: Equipe de Desenvolvimento  
**Prazo**: 4 semanas  
**Próxima Fase**: Batch C (módulos restantes)