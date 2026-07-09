# 🚀 GUIA DE USO - Modal "Marcar Consulta" Integrado ao Banco

## 📋 Resumo da Implementação

O modal "Marcar Consulta" foi completamente reformulado com integração total ao banco de dados MySQL, seguindo arquitetura em camadas e boas práticas de desenvolvimento.

---

## 🎯 Como Usar

### 1. **Abrir o Modal**
- Na tela da Agenda, clique no botão **"➕ Marcar Consulta"**
- Uma janela modal abrirá com o formulário

### 2. **Preenchimento dos Campos**

#### **👤 Campo Paciente** (Obrigatório)
```
- Digite no mínimo 2 caracteres
- Busca por: Nome ou CPF
- Exemplo: "Jo" → lista pacientes com "Jo" no nome
- Exemplo: "123" → lista pacientes com "123" no CPF
- Selecione um paciente da lista
- O ID é armazenado automaticamente
```

#### **🩺 Campo Médico** (Obrigatório)
```
- Pré-carregado com médicos da sua clínica
- Exibe: Nome do Médico - Especialidade
- Ao selecionar:
  - Especialidade é preenchida automaticamente
  - Horários ocupados são listados em tempo real
```

#### **📅 Campo Data** (Obrigatório)
```
- Formato: DD/MM/YYYY
- Exemplo: 15/03/2025
- Restrições:
  - Não aceita datas no passado
  - Valida formato automaticamente
```

#### **🕐 Campo Hora** (Obrigatório)
```
- Formato: HH:MM (24h)
- Exemplo: 14:30 (2:30 PM)
- Validação dinâmica:
  - Mostra horários já ocupados
  - Não permite duplicatas
```

#### **🦷 Campo Especialidade** (Automático)
```
- Preenchido automaticamente ao selecionar médico
- Campo desabilitado (somente leitura)
- Não é possível editar manualmente
```

#### **📝 Campo Observações** (Opcional)
```
- Texto livre
- Limite: sem limite específico
- Salvo exatamente como digitado
```

### 3. **Validação e Salvamento**

Clique em **"✓ Salvar Consulta"**

O sistema valida:
1. ✓ Paciente selecionado
2. ✓ Médico selecionado
3. ✓ Data válida (não passada, formato correto)
4. ✓ Hora válida (formato correto)
5. ✓ Especialidade preenchida
6. ✓ Horário não duplicado
7. ✓ Conexão com banco funcionando

**Se tudo estiver OK:**
- ✓ Consulta é salva no banco
- ✓ ID da consulta é exibido
- ✓ Modal é fechado automaticamente
- ✓ Agenda é atualizada em tempo real

**Se houver erro:**
- ✗ Mensagem clara do problema
- ✗ Modal permanece aberto
- ✗ Você pode corrigir e tentar novamente

---

## 🔧 Detalhes Técnicos

### Arquitetura de Camadas

```
┌─────────────────────────────────────────┐
│  Views (CustomTkinter)                   │ ← Modal
│  abrir_dialogo_marcar_consulta()        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Controllers (consulta_controller.py)    │
│  - buscar_pacientes_dinamico()          │
│  - listar_medicos_por_clinica()         │
│  - validar_data_consulta()              │
│  - validar_hora_consulta()              │
│  - verificar_disponibilidade_horario()  │
│  - salvar_nova_consulta()               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Services                                 │
│  • paciente_service.py                  │
│  • medico_service.py                    │
│  • consulta_service.py                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Database (get_connection)              │
│  Conexão MySQL Aiven                    │
└─────────────────────────────────────────┘
```

### Queries Utilizadas

**Pacientes:**
```sql
SELECT id, nome, cpf
FROM odontoPro_paciente
WHERE clinica_id = %s AND (
    LOWER(nome) LIKE LOWER(%s) OR
    REPLACE(REPLACE(cpf, '.', ''), '-', '') LIKE %s
)
ORDER BY nome ASC
LIMIT 20
```

**Médicos:**
```sql
SELECT DISTINCT m.id, m.nome
FROM odontoPro_medico m
JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id
WHERE m.clinica_id = %s
ORDER BY m.nome ASC
```

**Validar Horário:**
```sql
SELECT COUNT(*) as total
FROM odontoPro_consulta
WHERE medico_id = %s
  AND DATE(data_hora) = %s
  AND TIME(data_hora) = %s
  AND status != 'cancelada'
```

**Criar Consulta:**
```sql
INSERT INTO odontoPro_consulta
(clinica_id, paciente_id, medico_id, data_hora, status, observacoes)
VALUES (%s, %s, %s, %s, %s, %s)
```

### Validações no Código

```python
# Data
def validar_data_consulta(data_str):
    - Formato DD/MM/YYYY
    - Não permite passado
    - Retorna: (válido, mensagem, datetime_obj)

# Hora
def validar_hora_consulta(hora_str):
    - Formato HH:MM
    - Retorna: (válido, mensagem, time_obj)

# Horário Disponível
def verificar_disponibilidade_horario(medico_id, data, hora):
    - Verifica conflitos
    - Ignora consultas canceladas
    - Retorna: (disponível, mensagem)

# Salvar
def salvar_nova_consulta(...):
    - Valida paciente exists
    - Valida médico pertence à clínica
    - Verifica horário disponível
    - Insere com transação
    - Retorna resultado completo
```

---

## ⚡ Performance

- **Busca de Pacientes:** Paginada (max 20 resultados)
- **Carregamento de Médicos:** Em background (thread safe)
- **Validações:** Em tempo real, sem bloqueio UI
- **Consultas:** Otimizadas com índices de banco

---

## 🛡️ Segurança

- ✓ Queries parametrizadas (previne SQL Injection)
- ✓ Validação de clinica_id (não permite entre clinicas)
- ✓ Conexão segura com SSL/TLS (Aiven)
- ✓ Campos obrigatórios validados
- ✓ Tratamento de exceções robusto

---

## 📊 Estrutura de Dados

**Tabelas Utilizadas (nenhuma nova criada):**

```
odontoPro_paciente
├─ id (PK)
├─ nome
├─ cpf
├─ email
├─ telefone
└─ clinica_id (FK)

odontoPro_medico
├─ id (PK)
├─ nome
└─ clinica_id (FK)

odontoPro_medico_especialidades
├─ medico_id (FK)
├─ especialidade_id (FK)

odontoPro_especialidade
├─ id (PK)
└─ nome

odontoPro_consulta
├─ id (PK) ← Retornado após salvar
├─ clinica_id (FK)
├─ paciente_id (FK)
├─ medico_id (FK)
├─ data_hora
├─ status
└─ observacoes
```

---

## 🐛 Troubleshooting

### "Nenhum paciente encontrado"
- Verifique o nome/CPF digitado
- Digite pelo menos 2 caracteres
- Confirme se paciente pertence à sua clínica

### "Horário já reservado"
- Verifique os horários listados na interface
- Selecione um horário diferente
- Cancele outra consulta se necessário

### "Médico não encontrado"
- Seu médico foi cadastrado?
- Médico está vinculado à sua clínica?
- Médico tem especialidade cadastrada?

### "Erro ao salvar no banco"
- Verifique conexão com internet
- Verifique se banco está online
- Tente novamente em alguns segundos

---

## 📞 Mensagens de Sistema

| Mensagem | Solução |
|----------|---------|
| ❌ Selecione um paciente válido | Busque e clique em um paciente da lista |
| ❌ Selecione um médico | Escolha um médico do dropdown |
| ❌ A data não pode ser no passado | Use uma data futura ou hoje |
| ❌ Formato de data inválido. Use DD/MM/YYYY | Digite no formato correto |
| ❌ Formato de hora inválido. Use HH:MM | Digite no formato 24h |
| ❌ Este horário já está reservado | Escolha outro horário |
| ✓ Consulta marcada com sucesso! | Parabéns! Seu agendamento foi feito |

---

## 🎓 Próximas Implementações (Future)

- [ ] Repetição de consultas (agendamento recorrente)
- [ ] Lembretes por email/SMS
- [ ] Integração com calendário Google
- [ ] Reagendamento automático
- [ ] Cancelamento automático de consultas
- [ ] Relatórios de ocupação

---

**Versão:** 1.0  
**Data:** 07/07/2026  
**Sistema:** OdontoPro Desktop  
**Status:** ✓ Pronto para Produção
