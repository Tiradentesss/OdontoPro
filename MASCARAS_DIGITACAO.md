# 🎭 Máscaras de Digitação - OdontoPro

## 📋 Visão Geral

Implementação de máscaras de digitação para campos de entrada no sistema OdontoPro usando **CustomTkinter puro**, sem dependências externas.

## ✨ Máscaras Implementadas

### 1️⃣ CPF
**Formato:** `000.000.000-00`

**Comportamento:**
```
1          → 1
12         → 12
123        → 123
1234       → 123.4
12345      → 123.45
123456     → 123.456
1234567    → 123.456.7
12345678   → 123.456.78
123456789  → 123.456.789
1234567890 → 123.456.789-0
12345678901 → 123.456.789-01
```

**Características:**
- ✅ Apenas números (0-9)
- ✅ Máximo 11 dígitos
- ✅ Separadores inseridos automaticamente
- ✅ Backspace funciona normalmente
- ✅ Colagem de números formatada automaticamente

### 2️⃣ DATA DE NASCIMENTO
**Formato:** `DD/MM/AAAA`

**Comportamento:**
```
1           → 1
12          → 12
123         → 12/3
1234        → 12/34
12345       → 12/34/5
123456      → 12/34/56
1234567     → 12/34/567
12345678    → 12/34/5678
```

**Características:**
- ✅ Apenas números (0-9)
- ✅ Máximo 8 dígitos
- ✅ Separadores inseridos automaticamente
- ✅ Backspace funciona normalmente
- ✅ Colagem de números formatada automaticamente

### 3️⃣ TELEFONE
**Formato Variável:**
- **10 dígitos (fixo):** `(00) 0000-0000`
- **11 dígitos (celular):** `(00) 00000-0000`

**Comportamento:**
```
1               → (1
12              → (12
123             → (12) 3
1234            → (12) 34
12345           → (12) 345
123456          → (12) 3456
1234567         → (12) 34567
12345678        → (12) 3456-78
1234567890      → (12) 3456-7890
12345678901     → (12) 34567-8901
```

**Características:**
- ✅ Apenas números (0-9)
- ✅ Máximo 11 dígitos
- ✅ Formato adapta automaticamente: 10 dígitos → fixo | 11 dígitos → celular
- ✅ Backspace funciona normalmente
- ✅ Colagem de números formatada automaticamente

---

## 🏗️ Arquitetura

### Estrutura de Arquivos

```
SistemaDesktop/
├── services/
│   ├── mascaras_service.py       # Funções de formatação
│   ├── campos_mascarados.py      # Classes para aplicar máscaras
│   └── __init__.py
└── views/
    └── cadastro.py               # Integração com a UI
```

### Componentes

#### 1. **MascarasService** (`mascaras_service.py`)
Classe estática com funções de formatação reutilizáveis:

```python
MascarasService.formatar_cpf(valor)        # CPF
MascarasService.formatar_data(valor)       # Data
MascarasService.formatar_telefone(valor)   # Telefone
MascarasService.extrair_numeros(valor)     # Remove formatação
```

#### 2. **CampoMascarado** (`campos_mascarados.py`)
Classe que aplica máscara a um CTkEntry individual:

```python
campo = CampoMascarado(entry, 'cpf')
campo.obter_valor_formatado()   # Com formatação
campo.obter_valor_numerico()    # Apenas números
campo.limpar()                  # Limpa o campo
```

#### 3. **GerenciadorMascaras** (`campos_mascarados.py`)
Gerenciador centralizado para múltiplos campos:

```python
gerenciador = GerenciadorMascaras()
gerenciador.adicionar_campo('cpf', entry_cpf, 'cpf')
gerenciador.adicionar_campo('tel', entry_tel, 'telefone')

valores = gerenciador.obter_valores()           # Formatados
numeros = gerenciador.obter_valores_numericos() # Apenas dígitos
gerenciador.limpar_tudo()                       # Limpa tudo
```

---

## 💻 Como Usar

### Opção 1: Uso Simples (Um Campo)

```python
from services.campos_mascarados import CampoMascarado

# No seu código...
campo_cpf = CampoMascarado(entry_cpf, 'cpf')
campo_tel = CampoMascarado(entry_tel, 'telefone')

# Para obter valores:
cpf_com_mascara = campo_cpf.obter_valor_formatado()   # "123.456.789-00"
cpf_numeros = campo_cpf.obter_valor_numerico()        # "12345678900"
```

### Opção 2: Uso com Gerenciador (Múltiplos Campos)

```python
from services.campos_mascarados import GerenciadorMascaras

# No __init__ da sua tela:
self.mascaras = GerenciadorMascaras()
self.mascaras.adicionar_campo('cpf', entry_cpf, 'cpf')
self.mascaras.adicionar_campo('data', entry_data, 'data')
self.mascaras.adicionar_campo('telefone', entry_tel, 'telefone')

# Ao salvar:
valores = self.mascaras.obter_valores_numericos()
cpf = valores['cpf']           # "12345678900"
data = valores['data']         # "12052000"
telefone = valores['telefone'] # "1234567890"
```

### Opção 3: No Projeto OdontoPro

As máscaras já estão integradas no arquivo `views/cadastro.py`:

```python
# Cadastro de Pacientes
self.mascaras_paciente.obter_valor_numerico()['cpf_paciente']
self.mascaras_paciente.obter_valor_numerico()['data_paciente']
self.mascaras_paciente.obter_valor_numerico()['telefone_paciente']

# Cadastro de Profissional
self.mascaras_profissional.obter_valor_numerico()['telefone_medico']
```

---

## 🔧 Detalhes Técnicos

### Como Funciona

1. **Captura de Evento:** Ao usuário digitar, o evento `<KeyRelease>` é capturado
2. **Extração de Números:** Remove tudo que não é dígito
3. **Formatação:** Aplica a máscara apropriada
4. **Atualização:** Insere o valor formatado no campo
5. **Cursor:** Repositiciona o cursor no fim do texto

### Evitar Loops Infinitos

A classe usa uma flag `atualizando` para evitar que a formatação acionada pela digitação gere novos eventos:

```python
if self.atualizando:
    return
try:
    self.atualizando = True
    # ... formatação ...
finally:
    self.atualizando = False
```

### Performance

- **Sem gravação em arquivo:** Operações apenas em memória
- **Sem requisições:** Toda lógica é local
- **Sem threading:** Execução síncrona, segura com Tkinter
- **Eficiente:** Apenas strings são processadas

---

## 📋 Casos de Uso

### Validação de Entrada

```python
# CPF mínimo
def validar_cpf(entry):
    valor = MascarasService.extrair_numeros(entry.get())
    return len(valor) == 11

# Data mínima
def validar_data(entry):
    valor = MascarasService.extrair_numeros(entry.get())
    return len(valor) == 8
```

### Envio para API

```python
# Enviar apenas números para o banco
valores_numericos = self.mascaras.obter_valores_numericos()
api.criar_paciente(
    cpf=valores_numericos['cpf_paciente'],
    telefone=valores_numericos['telefone_paciente']
)
```

### Carregamento de Dados

```python
# Se o banco retorna só números, a máscara é aplicada automaticamente
# ao digitar a primeira tecla
entrada.insert(0, "12345678901")  # Campo exibe "(12) 34567-8901"
```

---

## ✅ Testes e Validação

### Testar Manualmente

```bash
# 1. Abrir aplicação
python app.py

# 2. Na tela de Cadastro > Pacientes
# - Digitar no CPF: 12345678901
#   Esperado: 123.456.789-01
# - Digitar na Data: 12052000
#   Esperado: 12/05/2000
# - Digitar no Telefone: 1234567890
#   Esperado: (12) 3456-7890

# 3. Testar Backspace e colagem
# - Copiar: 12345678901
# - Colar no CPF
#   Esperado: 123.456.789-01
```

### Casos Extremos

| Caso | Entrada | Saída |
|------|---------|-------|
| Vazio | `` | `` |
| Letra | `abc` | `` (ignorado) |
| Símbolo | `123.456` | `123.456` (formatado) |
| Excesso | `123456789012` (12 dígitos em CPF) | `123.456.789-01` (máximo 11) |
| Backspace | `123.456.789-0` → delete → `123.456.789` | Funciona normalmente |

---

## 🚀 Implementação Futura

Fácil adicionar novas máscaras:

```python
@staticmethod
def formatar_cnpj(valor):
    """Máscara CNPJ: 00.000.000/0000-00"""
    apenas_numeros = ''.join(c for c in valor if c.isdigit())[:14]
    # ... aplicar formatação ...
    return formatado, cursor_pos
```

---

## 📝 Notas Importantes

### ✅ O Que Foi Mantido

- ✅ Layout exato da tela
- ✅ Cores, tamanhos e posicionamento
- ✅ Todas as funcionalidades existentes
- ✅ Conexão com banco de dados
- ✅ Validações e lógica de negócio

### ❌ O Que NÃO Usa

- ❌ Bibliotecas externas (tkintermask, pyinputplus)
- ❌ Expressões regulares complexas
- ❌ Threads ou async
- ❌ Modificação de arquivos
- ❌ Requisições HTTP

### 🔐 Segurança

- Sem injeção de SQL (use prepared statements no banco)
- Sem acesso ao sistema de arquivos
- Sem execução de código dinâmico
- Sem requisições não controladas

---

## 📞 Troubleshooting

### Problema: Máscara não aparece

**Solução:** Verifique se:
1. O `CampoMascarado` foi criado APÓS o CTkEntry
2. O tipo de máscara é válido ('cpf', 'data', 'telefone')
3. Não há erro de import

```python
# ✅ Correto
entry = ctk.CTkEntry(...)
campo = CampoMascarado(entry, 'cpf')

# ❌ Errado
campo = CampoMascarado(entry, 'cpf')  # entry ainda não existe
entry = ctk.CTkEntry(...)
```

### Problema: Loop de atualização

**Solução:** A flag `atualizando` evita isso automaticamente. Se ainda ocorrer:

```python
# Verificar se há múltiplos bind no mesmo evento
# Remover binds duplicados
```

### Problema: Cursor em lugar errado

**Solução:** A posição é calculada automaticamente. Se não funcionar:

```python
# Verificar se entry.icursor() é suportado
# (Deve ser, em CTkEntry)
```

---

## 📦 Dependências

- **Python:** 3.8+
- **CustomTkinter:** (já instalado no projeto)
- **Bibliotecas Padrão:** string, re (não usadas, apenas Python puro)

---

## 🎓 Exemplos Completos

### Exemplo 1: Tela Simples com Máscara

```python
import customtkinter as ctk
from services.campos_mascarados import CampoMascarado

root = ctk.CTk()
root.title("Teste Máscaras")

# Criar campo
entry_cpf = ctk.CTkEntry(root, placeholder_text="CPF")
entry_cpf.pack(padx=10, pady=10)

# Aplicar máscara
campo_cpf = CampoMascarado(entry_cpf, 'cpf')

# Botão para obter valor
def obter():
    print("Formatado:", campo_cpf.obter_valor_formatado())
    print("Números:", campo_cpf.obter_valor_numerico())

btn = ctk.CTkButton(root, text="Obter Valor", command=obter)
btn.pack(pady=10)

root.mainloop()
```

### Exemplo 2: Formulário Completo

```python
from services.campos_mascarados import GerenciadorMascaras

class Formulario:
    def __init__(self, root):
        self.mascaras = GerenciadorMascaras()
        
        # CPF
        self.entry_cpf = ctk.CTkEntry(root)
        self.entry_cpf.pack()
        self.mascaras.adicionar_campo('cpf', self.entry_cpf, 'cpf')
        
        # Data
        self.entry_data = ctk.CTkEntry(root)
        self.entry_data.pack()
        self.mascaras.adicionar_campo('data', self.entry_data, 'data')
        
        # Telefone
        self.entry_tel = ctk.CTkEntry(root)
        self.entry_tel.pack()
        self.mascaras.adicionar_campo('tel', self.entry_tel, 'telefone')
        
        # Botão Salvar
        btn = ctk.CTkButton(root, text="Salvar", command=self.salvar)
        btn.pack()
    
    def salvar(self):
        dados = self.mascaras.obter_valores_numericos()
        print("Salvando:", dados)
        # Enviar para API/banco
```

---

## 📄 Licença

Implementação interna do projeto OdontoPro. Não exportar para repositórios públicos sem autorização.
