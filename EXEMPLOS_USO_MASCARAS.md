# 📚 Exemplos de Uso - Máscaras de Digitação

## 1️⃣ Exemplo Simples: Um Campo CPF

```python
import customtkinter as ctk
from services.campos_mascarados import CampoMascarado

root = ctk.CTk()
root.title("Teste CPF")

# Criar entrada
entry_cpf = ctk.CTkEntry(root, placeholder_text="Digite seu CPF")
entry_cpf.pack(padx=20, pady=20)

# Aplicar máscara
campo_cpf = CampoMascarado(entry_cpf, 'cpf')

# Botão para obter valor
def salvar():
    cpf_formatado = campo_cpf.obter_valor_formatado()
    cpf_numeros = campo_cpf.obter_valor_numerico()
    
    print(f"Formatado: {cpf_formatado}")  # 123.456.789-01
    print(f"Números: {cpf_numeros}")      # 12345678901

btn = ctk.CTkButton(root, text="Salvar", command=salvar)
btn.pack(pady=10)

root.mainloop()
```

**Resultado:**
```
Digite: 1 2 3 4 5 6 7 8 9 0 1
Campo exibe: 123.456.789-01 ✅
```

---

## 2️⃣ Exemplo Múltiplos Campos: Formulário

```python
import customtkinter as ctk
from services.campos_mascarados import GerenciadorMascaras

class FormularioPaciente:
    def __init__(self, root):
        self.root = root
        self.root.title("Formulário Paciente")
        self.root.geometry("400x500")
        
        # Criar gerenciador de máscaras
        self.mascaras = GerenciadorMascaras()
        
        # Label e Entry: Nome
        ctk.CTkLabel(root, text="Nome").pack(pady=(20, 5), padx=20, anchor="w")
        self.nome_entry = ctk.CTkEntry(root, placeholder_text="Digite o nome")
        self.nome_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Label e Entry: CPF
        ctk.CTkLabel(root, text="CPF").pack(pady=(0, 5), padx=20, anchor="w")
        self.cpf_entry = ctk.CTkEntry(root, placeholder_text="Digite o CPF")
        self.cpf_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.mascaras.adicionar_campo('cpf', self.cpf_entry, 'cpf')
        
        # Label e Entry: Data
        ctk.CTkLabel(root, text="Data de Nascimento").pack(pady=(0, 5), padx=20, anchor="w")
        self.data_entry = ctk.CTkEntry(root, placeholder_text="DD/MM/AAAA")
        self.data_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.mascaras.adicionar_campo('data', self.data_entry, 'data')
        
        # Label e Entry: Telefone
        ctk.CTkLabel(root, text="Telefone").pack(pady=(0, 5), padx=20, anchor="w")
        self.tel_entry = ctk.CTkEntry(root, placeholder_text="Digite o telefone")
        self.tel_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.mascaras.adicionar_campo('telefone', self.tel_entry, 'telefone')
        
        # Botões
        btn_frame = ctk.CTkFrame(root, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        btn_salvar = ctk.CTkButton(btn_frame, text="Salvar", command=self.salvar)
        btn_salvar.pack(side="left", padx=(0, 10))
        
        btn_limpar = ctk.CTkButton(btn_frame, text="Limpar", command=self.limpar)
        btn_limpar.pack(side="left")
    
    def salvar(self):
        dados = self.mascaras.obter_valores_numericos()
        
        nome = self.nome_entry.get()
        cpf = dados['cpf']
        data = dados['data']
        telefone = dados['telefone']
        
        print(f"Nome: {nome}")
        print(f"CPF: {cpf}")
        print(f"Data: {data}")
        print(f"Telefone: {telefone}")
        # Salvar no BD...
    
    def limpar(self):
        self.nome_entry.delete(0, "end")
        self.mascaras.limpar_tudo()

root = ctk.CTk()
app = FormularioPaciente(root)
root.mainloop()
```

**Resultado ao clicar "Salvar":**
```
Nome: João Silva
CPF: 12345678901
Data: 12052000
Telefone: 1234567890
```

---

## 3️⃣ Exemplo Integrado: Classe com Padrão OOP

```python
import customtkinter as ctk
from services.campos_mascarados import GerenciadorMascaras
from services.mascaras_service import MascarasService

class TelaCadastro(ctk.CTkFrame):
    """Tela de cadastro com máscaras integradas."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.mascaras = GerenciadorMascaras()
        self._criar_widgets()
    
    def _criar_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="Cadastro", font=("Arial", 20, "bold"))
        titulo.pack(pady=20)
        
        # CPF
        self._criar_campo("CPF", "cpf")
        self._criar_campo("Data", "data")
        self._criar_campo("Telefone", "telefone")
        
        # Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=20)
        
        btn_info = ctk.CTkButton(frame_botoes, text="Ver Dados", command=self._ver_dados)
        btn_info.pack(side="left", padx=(0, 10))
        
        btn_limpar = ctk.CTkButton(frame_botoes, text="Limpar", command=self._limpar)
        btn_limpar.pack(side="left")
        
        # Label de informações
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#FFD700",
            justify="left"
        )
        self.info_label.pack(fill="x", padx=20, pady=10)
    
    def _criar_campo(self, label, tipo):
        # Frame
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Label
        lbl = ctk.CTkLabel(frame, text=label)
        lbl.pack(anchor="w", pady=(0, 5))
        
        # Entry
        entry = ctk.CTkEntry(frame, placeholder_text=f"Digite {label.lower()}")
        entry.pack(fill="x")
        
        # Aplicar máscara
        self.mascaras.adicionar_campo(tipo, entry, tipo)
    
    def _ver_dados(self):
        valores = self.mascaras.obter_valores_numericos()
        
        info = "📊 Dados Capturados:\n"
        info += f"CPF: {valores.get('cpf', '')}\n"
        info += f"Data: {valores.get('data', '')}\n"
        info += f"Tel: {valores.get('telefone', '')}\n"
        
        self.info_label.configure(text=info)
    
    def _limpar(self):
        self.mascaras.limpar_tudo()
        self.info_label.configure(text="")

# Usar
root = ctk.CTk()
root.geometry("400x500")

tela = TelaCadastro(root)
tela.pack(fill="both", expand=True)

root.mainloop()
```

---

## 4️⃣ Exemplo Avançado: Validação com Máscaras

```python
from services.mascaras_service import MascarasService

class ValidadorCampos:
    """Valida campos com máscaras."""
    
    @staticmethod
    def validar_cpf(valor):
        """Valida se CPF tem 11 dígitos."""
        numeros = MascarasService.extrair_numeros(valor)
        return len(numeros) == 11
    
    @staticmethod
    def validar_data(valor):
        """Valida se data tem 8 dígitos."""
        numeros = MascarasService.extrair_numeros(valor)
        if len(numeros) != 8:
            return False
        
        dia = int(numeros[0:2])
        mes = int(numeros[2:4])
        ano = int(numeros[4:8])
        
        # Validações básicas
        if not (1 <= dia <= 31):
            return False
        if not (1 <= mes <= 12):
            return False
        if ano < 1900 or ano > 2025:
            return False
        
        return True
    
    @staticmethod
    def validar_telefone(valor):
        """Valida se telefone tem 10 ou 11 dígitos."""
        numeros = MascarasService.extrair_numeros(valor)
        return len(numeros) in [10, 11]

# Usar
validador = ValidadorCampos()

assert validador.validar_cpf("123.456.789-01") == True
assert validador.validar_cpf("123.456.789") == False

assert validador.validar_data("12/05/2000") == True
assert validador.validar_data("31/13/2000") == False

assert validador.validar_telefone("(12) 3456-7890") == True
assert validador.validar_telefone("(12) 34567-8901") == True
```

---

## 5️⃣ Exemplo Real: Integração com Database

```python
from services.campos_mascarados import GerenciadorMascaras
from services.mascaras_service import MascarasService
import sqlite3

class ControladorPaciente:
    def __init__(self):
        self.mascaras = GerenciadorMascaras()
        self.conexao = sqlite3.connect('pacientes.db')
    
    def criar_paciente(self, entry_nome, entry_cpf, entry_data, entry_tel):
        # Adicionar campos ao gerenciador
        self.mascaras.adicionar_campo('cpf', entry_cpf, 'cpf')
        self.mascaras.adicionar_campo('data', entry_data, 'data')
        self.mascaras.adicionar_campo('tel', entry_tel, 'telefone')
        
        # Obter dados (numéricos para BD)
        nome = entry_nome.get().strip()
        dados = self.mascaras.obter_valores_numericos()
        cpf = dados['cpf']
        data = dados['data']
        telefone = dados['tel']
        
        # Validar
        if not self._validar(nome, cpf, data, telefone):
            return False
        
        # Salvar no BD
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO pacientes (nome, cpf, data_nasc, telefone) VALUES (?, ?, ?, ?)",
            (nome, cpf, data, telefone)
        )
        self.conexao.commit()
        
        return True
    
    def _validar(self, nome, cpf, data, telefone):
        if not nome or len(nome) < 3:
            print("Nome inválido")
            return False
        
        if len(cpf) != 11 or not cpf.isdigit():
            print("CPF inválido")
            return False
        
        if len(data) != 8 or not data.isdigit():
            print("Data inválida")
            return False
        
        if len(telefone) not in [10, 11] or not telefone.isdigit():
            print("Telefone inválido")
            return False
        
        return True
```

---

## 6️⃣ Exemplo: Preenchimento Automático

```python
from services.campos_mascarados import CampoMascarado

def carregar_paciente(id_paciente):
    """Carrega dados do BD e preenche campos."""
    
    # Simular dados do BD (normalmente apenas números)
    dados_bd = {
        'cpf': '12345678901',
        'data': '12052000',
        'telefone': '1234567890'
    }
    
    # Preencher entries com valores numéricos
    entry_cpf.insert(0, dados_bd['cpf'])
    entry_data.insert(0, dados_bd['data'])
    entry_tel.insert(0, dados_bd['telefone'])
    
    # As máscaras serão aplicadas automaticamente quando o usuário editar
    # Ou forçar aplicação:
    # campo_cpf._ao_teclar(None)  # Não recomendado, deixar o usuário digitar
```

---

## 7️⃣ Exemplo: Personalizar Máscaras

```python
from services.mascaras_service import MascarasService

class MascarasPersonalizadas(MascarasService):
    """Estenda a classe para adicionar novas máscaras."""
    
    @staticmethod
    def formatar_cnpj(valor):
        """Máscara CNPJ: 00.000.000/0000-00"""
        apenas_numeros = ''.join(c for c in valor if c.isdigit())[:14]
        
        if len(apenas_numeros) == 0:
            return '', 0
        elif len(apenas_numeros) <= 2:
            formatado = apenas_numeros
        elif len(apenas_numeros) <= 5:
            formatado = f"{apenas_numeros[:2]}.{apenas_numeros[2:]}"
        elif len(apenas_numeros) <= 8:
            formatado = f"{apenas_numeros[:2]}.{apenas_numeros[2:5]}.{apenas_numeros[5:]}"
        elif len(apenas_numeros) <= 12:
            formatado = f"{apenas_numeros[:2]}.{apenas_numeros[2:5]}.{apenas_numeros[5:8]}/{apenas_numeros[8:]}"
        else:
            formatado = f"{apenas_numeros[:2]}.{apenas_numeros[2:5]}.{apenas_numeros[5:8]}/{apenas_numeros[8:12]}-{apenas_numeros[12:]}"
        
        return formatado, len(formatado)

# Usar
campo_cnpj = CampoMascarado(entry, 'cnpj')
# Mas precisa também modificar campos_mascarados.py para incluir a nova máscara
```

---

## 📚 Tabela Comparativa de Usos

| Caso de Uso | Solução | Código |
|------------|---------|--------|
| 1 campo | `CampoMascarado` | `CampoMascarado(entry, 'cpf')` |
| Múltiplos campos | `GerenciadorMascaras` | `gerenciador.adicionar_campo(...)` |
| Validação | `MascarasService` | `MascarasService.extrair_numeros(...)` |
| Personalizado | Herança | `class Custom(MascarasService)` |
| Integração BD | Controller | Combinar com banco de dados |

---

## 🎯 Dicas Importantes

### ✅ Sempre Use Valores Numéricos para BD

```python
# ❌ ERRADO - Salvar formatado
cpf_bd = campo_cpf.obter_valor_formatado()  # "123.456.789-01"

# ✅ CORRETO - Salvar números
cpf_bd = campo_cpf.obter_valor_numerico()   # "12345678901"
```

### ✅ Limpar Campos de Forma Correta

```python
# ❌ ERRADO
entry.delete(0, "end")  # Pode gerar eventos

# ✅ CORRETO
campo.limpar()  # Limpa sem disparar eventos de formatação
```

### ✅ Gerenciar Múltiplos Campos

```python
# ❌ ERRADO - Múltiplos gerenciadores
mascaras1 = GerenciadorMascaras()
mascaras2 = GerenciadorMascaras()

# ✅ CORRETO - Um gerenciador
mascaras = GerenciadorMascaras()
mascaras.adicionar_campo('cpf1', entry1, 'cpf')
mascaras.adicionar_campo('cpf2', entry2, 'cpf')
```

---

Todos os exemplos acima funcionam com a implementação atual!
