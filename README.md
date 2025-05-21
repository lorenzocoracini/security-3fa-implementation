# Sistema de Autenticação com Três Fatores (3FA)

Este projeto implementa um sistema de autenticação com **três fatores** (3FA), utilizando autenticação via senha, token TOTP (QR code) e IP.

## Estrutura do Projeto

```
security-3fa-implementation/
├── client.py              # Aplicação cliente (usuário)
├── client_utils.py        # Funções auxiliares do cliente
├── server.py              # Aplicação servidor (API)
├── server_utils.py        # Funções auxiliares do servidor
├── requirements.txt       # Lista de dependências
└── data/                  # Diretório com dados (chaves, tokens, etc.)
```

## Requisitos

- **Python 3.11**
- pip (gerenciador de pacotes Python)

Verifique a versão instalada com:

```bash
python3.11 --version
```

> Se não tiver o Python 3.11, instale-o via [https://www.python.org/downloads/](https://www.python.org/downloads/)

## Instalação

### 1. Clone o projeto

```bash
git clone git@github.com:lorenzocoracini/security-3fa-implementation.git
cd security-3fa-implementation/
```

### 2. Crie um ambiente virtual

```bash
python3.11 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências de uma vez

```bash
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
```


## Executando o Projeto

### 1. Inicie o servidor

Em um terminal:

```bash
python3.11 server.py
```

O servidor ficará escutando por requisições na porta `8888`.

### 2. Execute o cliente

Em outro terminal:

```bash
python3.11 client.py
```

## Funcionalidades do Cliente

- **1. Register**: Cria um novo usuário e gera QR Code para ser escaneado em um App no celular para configuração TOTP.
- **2. Login**: Autentica com senha e código TOTP que deve ser consultado no App.
- **3. Send Message**: Envia mensagem cifrada ao servidor (criptografia baseada no token TOTP que pode deve ser pego no App).
- **4. Logout**: Encerra a sessão.
- **0. Exit**: Sai do programa.

## Autores

**Francisco Camerini, Lorenzo Coracini e Guilherme Cardoso**
