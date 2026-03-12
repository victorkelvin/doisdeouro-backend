# 🥋 Dois de Ouro — Backend API

API REST para gerenciamento de academia de Jiu-Jitsu, construída com **Django** e **Django REST Framework**. O sistema permite o controle completo de alunos, turmas, graduações, aulas e frequência, além da geração de relatórios e exportação em Excel.

---

## 📋 Índice

- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Executando o Projeto](#-executando-o-projeto)
- [Endpoints da API](#-endpoints-da-api)
- [Autenticação](#-autenticação)
- [Apps e Módulos](#-apps-e-módulos)
- [Deploy](#-deploy)

---

## 🚀 Tecnologias

| Tecnologia | Versão | Descrição |
|---|---|---|
| Python | 3.x | Linguagem principal |
| Django | 4.2.7 | Framework web |
| Django REST Framework | 3.14.0 | Construção da API REST |
| PostgreSQL | — | Banco de dados relacional |
| SimpleJWT | 5.3.0 | Autenticação via JSON Web Tokens |
| Pandas | 2.2.3 | Manipulação de dados para relatórios |
| XlsxWriter / openpyxl | — | Exportação de relatórios em Excel |
| Pillow | 10.1.0 | Upload e tratamento de imagens |
| Gunicorn | 23.0.0 | Servidor WSGI para produção |
| django-cors-headers | 4.2.0 | Gerenciamento de CORS |
| django-filter | 23.3 | Filtros avançados nos endpoints |

---

## 🏗 Arquitetura

O projeto segue a estrutura padrão do Django, organizado em **3 apps** dentro do diretório `apps/`:

```
doisdeouro-backend/
├── core/                   # Configurações do projeto Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── contas/             # Autenticação e gerenciamento de instrutores
│   ├── academia/           # Alunos, turmas, graduações e convites
│   └── atendimento/        # Aulas, frequência e relatórios
├── media/                  # Uploads (fotos de alunos/instrutores)
├── manage.py
├── requirements.txt
└── procfile
```

---

## ✅ Pré-requisitos

- **Python 3.10+**
- **PostgreSQL**
- **pip** (gerenciador de pacotes Python)
- (Opcional) **virtualenv** ou **venv** para ambiente virtual

---

## ⚙ Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/doisdeouro-backend.git
cd doisdeouro-backend
```

2. **Crie e ative o ambiente virtual:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente** (veja a seção abaixo).

5. **Execute as migrações:**

```bash
python manage.py migrate
```

6. **Crie um superusuário (instrutor admin):**

```bash
python manage.py createsuperuser
```

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Django
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados (PostgreSQL)
DB_NAME=doisdeouro
DB_USER=postgres
DB_PASSWORD=sua-senha
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## ▶ Executando o Projeto

**Servidor de desenvolvimento:**

```bash
python manage.py runserver
```

A API estará disponível em `http://localhost:8000/`.

**Painel administrativo:** `http://localhost:8000/admin/`

---

## 📡 Endpoints da API

### Autenticação

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/token/` | Obter par de tokens (access + refresh) |
| `POST` | `/api/token/refresh/` | Renovar access token |

### Contas — `/api/contas/`

| Método | Endpoint | Descrição | Permissão |
|---|---|---|---|
| `GET` | `/api/contas/instrutores/` | Listar instrutores | Autenticado |
| `GET` | `/api/contas/instrutores/{id}/` | Detalhar instrutor | Autenticado |
| `POST` | `/api/contas/instrutores/` | Criar instrutor | Admin |
| `PUT/PATCH` | `/api/contas/instrutores/{id}/` | Atualizar instrutor | Admin |
| `DELETE` | `/api/contas/instrutores/{id}/` | Remover instrutor | Admin |

### Academia — `/api/academia/`

| Método | Endpoint | Descrição | Permissão |
|---|---|---|---|
| `GET` | `/api/academia/alunos/` | Listar alunos | Autenticado |
| `GET` | `/api/academia/alunos/{id}/` | Detalhar aluno | Autenticado |
| `POST` | `/api/academia/alunos/` | Criar aluno | Autenticado ou Token de convite |
| `PUT/PATCH` | `/api/academia/alunos/{id}/` | Atualizar aluno | Autenticado |
| `DELETE` | `/api/academia/alunos/{id}/` | Remover aluno | Autenticado |
| `POST` | `/api/academia/alunos/generate_invitation/` | Gerar convite temporário | Autenticado |
| `GET` | `/api/academia/alunos/validate_invitation/?token=...` | Validar token de convite | Público |
| `GET` | `/api/academia/graduacoes/` | Listar graduações (faixas) | Público |
| `GET` | `/api/academia/turmas/` | Listar turmas | Público |

### Atendimento — `/api/atendimento/`

| Método | Endpoint | Descrição | Permissão |
|---|---|---|---|
| `GET` | `/api/atendimento/aulas/` | Listar aulas | Autenticado |
| `GET` | `/api/atendimento/aulas/{id}/` | Detalhar aula | Autenticado |
| `POST` | `/api/atendimento/aulas/` | Registrar aula | Admin |
| `PUT/PATCH` | `/api/atendimento/aulas/{id}/` | Atualizar aula | Admin |
| `DELETE` | `/api/atendimento/aulas/{id}/` | Remover aula | Admin |
| `POST` | `/api/atendimento/aulas/export-xls/` | Exportar aula em Excel | Autenticado |

### Relatórios — `/api/atendimento/relatorios/`

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/atendimento/relatorios/?tipo=presenca` | Relatório de presença |
| `GET` | `/api/atendimento/relatorios/?tipo=aulas` | Relatório de aulas |
| `GET` | `/api/atendimento/relatorios/?tipo=instrutores` | Relatório de instrutores |
| `GET` | `/api/atendimento/relatorios/?tipo=turmas` | Relatório de turmas |

**Parâmetros de filtro dos relatórios:**

| Parâmetro | Descrição |
|---|---|
| `data_inicio` | Data inicial (formato: `YYYY-MM-DD`) |
| `data_fim` | Data final (formato: `YYYY-MM-DD`) |
| `turmas` | IDs das turmas (pode repetir para múltiplas) |
| `alunos` | IDs dos alunos |
| `instrutores` | IDs dos instrutores |

---

## 🔑 Autenticação

O projeto utiliza **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.

**Fluxo de autenticação:**

1. Envie `POST /api/token/` com `username` e `password` no body.
2. Receba o `access` token (válido por **2 horas**) e o `refresh` token (válido por **1 dia**).
3. Inclua o token em todas as requisições protegidas:

```
Authorization: Bearer <access_token>
```

4. Quando o access token expirar, use `POST /api/token/refresh/` com o `refresh` token para obter um novo access token.

### Sistema de Convites

Para permitir que alunos se cadastrem sem autenticação, o sistema oferece **tokens de convite temporários**:

- Um instrutor autenticado gera um convite via `POST /api/academia/alunos/generate_invitation/`.
- O convite possui validade configurável (padrão: 24 horas) e pode ser reutilizado.
- O aluno se cadastra via `POST /api/academia/alunos/?token=<token>` sem necessidade de login.

---

## 📦 Apps e Módulos

### `contas`
Gerenciamento de **instrutores** (usuários do sistema). Utiliza um modelo de usuário customizado (`Instrutor`) que estende `AbstractBaseUser`, com campos como nome, graduação, contato e foto.

### `academia`
Módulo central da academia:
- **Aluno** — cadastro completo com nome, data de nascimento, turma, graduação (faixa), graus, responsável e foto.
- **Turma** — nome, dias da semana e horário.
- **Graduação** — tabela de referência com todas as faixas do Jiu-Jitsu (Branca → Vermelha).
- **DiaSemana** — tabela de referência para dias da semana.
- **AlunoInvitation** — sistema de convites temporários para autocadastro de alunos.

### `atendimento`
Controle de aulas e frequência:
- **Aula** — registro de aulas com data, horário, turma, instrutores e alunos presentes.
- **Relatórios** — geração de relatórios de presença, aulas, instrutores e turmas com filtros por data e entidades.
- **Exportação Excel** — exportação de dados de aulas em formato `.xls`.

---

## 🌐 Deploy

O projeto está preparado para deploy no **Railway** com:

- `procfile` configurado com Gunicorn
- Suporte a `DATABASE_URL` via `dj-database-url`
- Volume persistente para arquivos de mídia (`RAILWAY_VOLUME_MOUNT_PATH`)
- Variáveis de ambiente para configuração dinâmica

```
web: python manage.py migrate && gunicorn core.wsgi
```

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT** — veja o arquivo [LICENSE](LICENSE) para detalhes.
