# 🎬 Pixel Movies

Aplicação full-stack para busca e avaliação de filmes, utilizando a API pública do **TMDB** (The Movie Database).

## 📸 Funcionalidades

- **Busca de filmes** com scroll infinito e resultados paginados
- **Filtros** por gênero e ano de lançamento
- **Detalhes do filme** com sinopse, data de lançamento e elenco
- **Sistema de avaliação** (1-5 estrelas) com CRUD completo
- **Página "Filmes Avaliados"** com ordenação por nota/data
- **Autenticação** com JWT (registro, login, refresh token)
- **Cache** inteligente (Redis + in-memory fallback)
- **Circuit breaker** para proteção contra falhas do TMDB
- **Design responsivo** com tema dark premium
- **Dockerização** completa — execução com um único comando

---

## 🛠 Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React 18 + TypeScript, Vite, TanStack Query, Zustand, React Router v6 |
| Backend | Python 3.12, Flask, SQLAlchemy, Pydantic, Flask-JWT-Extended |
| Banco de dados | PostgreSQL 16 (Docker) / SQLite (dev local) |
| Cache | Redis 7 (Docker) / In-memory TTL cache (fallback) |
| Infraestrutura | Docker, Docker Compose, Nginx, Gunicorn |

---

## 🚀 Como Executar

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- Uma **chave de API do TMDB** (gratuita): https://www.themoviedb.org/settings/api

### Com Docker (recomendado — um único comando)

```bash
# 1. Clone o repositório
git clone <repo-url>
cd pixel

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e insira sua TMDB_API_KEY

# 3. Suba toda a aplicação
docker compose up --build
```

Acesse: **http://localhost:3000**

### Sem Docker (desenvolvimento local)

#### Backend

```bash
cd backend

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
# Crie um arquivo .env na raiz do projeto com TMDB_API_KEY

# Execute
python wsgi.py
```

Backend roda em: **http://localhost:5000**

#### Frontend

```bash
cd frontend

# Instale dependências
npm install

# Execute (dev server com proxy para backend)
npm run dev
```

Frontend roda em: **http://localhost:5173**

---

## 📂 Estrutura do Projeto

```
pixel/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory (Flask)
│   │   ├── config.py            # Configurações
│   │   ├── extensions.py        # SQLAlchemy, JWT, etc
│   │   ├── models/              # User, Rating
│   │   ├── routes/              # auth, movies, ratings
│   │   ├── services/            # auth, tmdb, rating
│   │   ├── schemas/             # Validação Pydantic
│   │   └── utils/               # cache, circuit breaker, errors
│   ├── tests/                   # Testes unitários
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client com interceptors
│   │   ├── components/          # MovieCard, MovieDetailsModal, RatingControl
│   │   ├── hooks/               # useDebounce, useInfiniteScroll
│   │   ├── pages/               # Home, RatedMovies, Login, Register
│   │   ├── store/               # Zustand (auth)
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── index.css            # Design system
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔌 Endpoints da API

### Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/register` | Criar conta | ❌ |
| POST | `/login` | Login | ❌ |
| POST | `/refresh` | Renovar token | 🔄 Refresh |
| GET | `/me` | Dados do usuário | ✅ |

### Filmes (`/api/v1/movies`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/search?query=&page=&genre=&year=` | Buscar filmes | ❌ |
| GET | `/:id` | Detalhes do filme | ❌ |
| GET | `/:id/credits` | Elenco | ❌ |
| GET | `/genres` | Lista de gêneros | ❌ |

### Avaliações (`/api/v1/ratings`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/` | Criar/atualizar avaliação | ✅ |
| GET | `/` | Listar avaliações do usuário | ✅ |
| GET | `/:movie_id` | Obter avaliação de um filme | ✅ |
| DELETE | `/:movie_id` | Remover avaliação | ✅ |

---

## 🏗 Decisões Técnicas

### Banco de Dados: PostgreSQL
- Constraints de unicidade (user_id, movie_id) garantem uma avaliação por filme por usuário
- Check constraint no score (1-5) no nível do banco
- Snapshot do filme (título + poster_path) na tabela de ratings para não depender 100% do TMDB

### Cache: Redis + In-Memory Fallback
- TTL por tipo: busca (5min), detalhes (1h), créditos (1h), gêneros (24h)
- Cache em memória com LRU eviction e limite de tamanho (1000 itens)
- Fallback automático se Redis não estiver disponível

### Circuit Breaker
- Abre após 5 falhas em 60s, bloqueia por 30s
- Half-open state permite testar recuperação
- Retorna erro amigável (503) quando aberto

### Autenticação: JWT
- Access token (15 min) + Refresh token (30 dias)
- Rate limiting em login (10/min) e registro (5/min)
- Refresh automático no frontend via interceptor

### Frontend: TanStack Query + Zustand
- React Query para toda comunicação com servidor (cache, retry, loading states)
- Zustand para estado de autenticação (persistido no localStorage)
- URL params sincronizados com filtros de busca

---

## 🧪 Testes

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm install
npm test
```

---

## 🔑 Como obter a chave da API do TMDB

1. Acesse https://www.themoviedb.org/signup e crie uma conta
2. Vá em **Configurações** → **API**
3. Solicite uma chave de API (tipo: Developer)
4. Copie a **API Key (v3 auth)** para o seu `.env`

---

## 📋 Checklist de Requisitos

- [x] Consumo da API do TMDB
- [x] Busca de filmes com pôster e título
- [x] Detalhes do filme (sinopse, data, elenco)
- [x] Avaliação CRUD (1-5 estrelas)
- [x] Página "Filmes Avaliados"
- [x] React + TypeScript (Frontend)
- [x] Flask + Python (Backend)
- [x] Banco de dados (PostgreSQL)
- [x] Tratamento de loading e erro
- [x] Executável com único comando
- [x] Scroll infinito
- [x] Filtro por gênero
- [x] Filtro por ano
- [x] Autenticação (JWT)
- [x] Cache (Redis + in-memory)
- [x] Dockerização completa
