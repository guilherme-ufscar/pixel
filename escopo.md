## 📌 Descrição do Desafio

Criar uma interface de busca onde os usuários possam pesquisar filmes utilizando a API pública do **The Movie Database (TMDB)**.

Documentação oficial da API:
https://developer.themoviedb.org/docs/getting-started

---

# 🛠 Stack Obrigatória

## Frontend
- React
- Typescript

## Backend
- Python
- Flask

## Banco de Dados
- Livre escolha do candidato

---

# 🎯 Objetivo

A aplicação deverá permitir:

## 1️⃣ Pesquisa de Filmes
Exibir os resultados da pesquisa mostrando:
- Pôster do filme
- Título do filme

---

## 2️⃣ Visualização de Detalhes

Ao clicar em um filme, o usuário deverá visualizar informações detalhadas:

- Elenco
- Sinopse
- Data de lançamento

---

## 3️⃣ Sistema de Avaliação

O sistema deverá permitir que o usuário avalie o filme com uma nota de 1 a 5.

### Requisitos da avaliação:

- Se o filme **não foi avaliado**:
  - O usuário poderá atribuir uma nota de 1 a 5.

- Se o filme **já foi avaliado**:
  - A nota deverá ser carregada automaticamente.
  - O usuário poderá:
    - Editar a nota.
    - Deletar/remover a nota.

---

## 4️⃣ Página "Filmes Avaliados"

A aplicação deverá conter uma página específica chamada:

### 🎬 Filmes Avaliados

Essa página deverá:

- Listar todos os filmes que o usuário já avaliou.
- Exibir:
  - Pôster
  - Título
  - Nota atribuída pelo usuário
- Permitir interação:
  - Ao clicar em um filme, abrir o modal/página com os detalhes.

---

# 🚀 Features Necessárias

## 🏠 Página Principal

A página principal deverá conter:

### 🔎 Barra de Pesquisa
- Realizar busca na API pública do TMDB.

### 📃 Listagem de Resultados
- Exibir:
  - Pôster
  - Título

### ⏳ Estados de Loading
- Indicação visual de carregamento enquanto busca dados.

### 🖱 Interação
- Ao clicar em um filme:
  - Abrir um modal ou página com os detalhes do filme.

---

## 🎥 Modal/Página do Filme

Deverá conter:

### 📚 Informações vindas da API pública
- Sinopse
- Data de lançamento
- Lista de elenco

### ⭐ Sistema de Avaliação
- Se não avaliado → permitir avaliar.
- Se já avaliado:
  - Carregar nota salva.
  - Permitir editar.
  - Permitir remover nota.

### 🔙 Navegação
- Botão de fechar modal ou voltar para a página principal.

---

## 🎬 Página "Filmes Avaliados"

Deverá conter:

### 📃 Listagem
- Filmes avaliados pelo usuário.

### 🖼 Exibição
- Pôster
- Título
- Nota atribuída

### 🖱 Interação
- Ao clicar em um filme:
  - Abrir modal/página com detalhes.

---

# 📊 O que Está Sendo Avaliado

Durante a análise do projeto, serão considerados:

- Consumo de APIs externas (TMDB)
- Criação de APIs (Backend em Flask)
- Entendimento de gerenciamento de estado no React
- Tratamento adequado de:
  - Estados de carregamento (loading)
  - Estados de erro
- Uso adequado de banco de dados

---

# 🌟 Pontos Extras (Bônus)

Os seguintes itens não são obrigatórios, mas agregam valor:

- Paginação ou scroll infinito
- Filtro por gênero
- Filtro por ano
- Autenticação
- Implementação de cache
- Dockerização da aplicação

---

# 📦 Instruções de Entrega

O projeto deve ser entregue em uma das seguintes formas:

- Link de um repositório público no Github
OU
- Arquivo compactado (.zip) contendo todo o código-fonte

---

## ⚙️ Requisitos de Execução

- A aplicação precisa ser executável com **um único comando**.
- O projeto deve conter um arquivo `README.md` com:
  - Instruções claras de como rodar localmente.

---

# ✅ Resumo Geral do Projeto

A aplicação deve:

1. Consumir a API do TMDB.
2. Permitir busca de filmes.
3. Exibir resultados com pôster e título.
4. Permitir visualizar detalhes do filme.
5. Permitir avaliação (CRUD de notas 1–5).
6. Listar filmes avaliados.
7. Utilizar:
   - React + Typescript (Frontend)
   - Flask + Python (Backend)
   - Banco de dados à escolha
8. Implementar tratamento de estados (loading e erro).
9. Ser executável com único comando.
10. Possuir README com instruções.