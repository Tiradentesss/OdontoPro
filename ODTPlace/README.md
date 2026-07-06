# ODTPlace

## Como rodar localmente

### 1. Instale as dependências

No diretório do app:

```bash
cd ODTPlace
npm install
```

No diretório do backend:

```bash
cd ODTPlace/backend
npm install
```

### 2. Configure o ambiente local

Copie o arquivo de exemplo para um arquivo local real:

```bash
cp .env.example .env
```

Edite o .env com as suas credenciais locais do banco e a URL desejada.

### 3. Inicie o backend

```bash
cd ODTPlace/backend
npm start
```

### 4. Inicie o app

Em outro terminal:

```bash
cd ODTPlace
npm start
```

## O que versionar

### Deve ser commitado
- src/services/api.js
- backend/server.js
- .env.example
- README.md
- package.json e package-lock.json quando houver mudança real nas dependências

### Não deve ser commitado
- .env
- qualquer arquivo com senhas, tokens ou credenciais reais
- node_modules/
- arquivos gerados localmente como .expo/ e build outputs
