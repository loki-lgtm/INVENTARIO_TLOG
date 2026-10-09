# Módulo Checklist de Periféricos — Sistema de Gestão de TI (Tlog)

Primeiro módulo com código de produção do projeto. Backend FastAPI + PostgreSQL,
frontend React.

## Como rodar

```bash
# 1. Banco
docker compose up -d db

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seeds              # cria tabelas + carga inicial
uvicorn app.main:app --reload    # http://localhost:8000/docs

# 3. Testes
pytest tests/ -q
```

O frontend espera `VITE_API_URL=http://localhost:8000/api`.

## Endpoints

| Método | Rota | Função |
|---|---|---|
| `GET` | `/api/checklist/tipos` | Periféricos ativos, na ordem do termo |
| `GET` | `/api/checklist/setores` | Progresso por setor (base do relatório) |
| `GET` | `/api/checklist` | Matriz colaborador x periférico |
| `PUT` | `/api/checklist/{colaborador_id}/{tipo_periferico_id}` | Marca/desmarca — é o autosave |

Filtros do `GET /api/checklist`: `centro_custo_id`, `busca`, `apenas_pendentes`,
`pagina`, `tamanho_pagina`.

## Decisões tomadas neste módulo

**Periféricos são dados, não colunas.** O termo de responsabilidade da Tlog lista
sete itens (Mouse, Mousepad, Teclado, Apoio de pulso, Suporte de notebook, Fone de
ouvido, Hub USB); os documentos do projeto listavam cinco. A lista mudou antes de
existir código. Como tabela `tipos_periferico`, incluir um item é inserir uma linha
— sem migração, sem mexer em schema, rota ou tela. `ativo=False` aposenta um
periférico preservando o histórico de quem já recebeu.

**A matriz é sempre completa.** Todo colaborador ativo volta da API com todos os
periféricos ativos; item sem linha no banco vale `false`. Corrige na origem o
defeito apontado do `data.json`, em que nem todo registro tinha as chaves.

**`marcado_por` e `created_at` desde a primeira migração.** Sem eles, o checklist
diz o que foi entregue mas não quem afirmou isso, e o histórico é irrecuperável
depois. São baratos agora e impossíveis de reconstruir retroativamente.

**Desmarcar limpa a `data_entrega`.** Uma entrega desfeita não tem data.

**Engine do banco criada sob demanda.** Importar a aplicação (testes, OpenAPI,
Alembic) não exige Postgres no ar.

**`centros_custo.gestor_id`.** O termo tem assinatura de gestor: para montar o
envelope do DocuSign o sistema precisa saber quem é o gestor do colaborador. Como
efeito colateral, atende o "modal lateral de gestores por departamento" do
Dashboard, que até aqui não tinha origem de dados.

## Pendências que este módulo deixa em aberto

- **Lista de centros de custo não confirmada.** O seed usa os sete do `MAPA.md`.
  "CCO Fiscal", citado em `arquitetura-projeto.md`, ficou de fora até saber se é
  setor próprio ou outro nome para Controladoria.
- **Autenticação.** `OPERADOR_ATUAL` está fixo no frontend até o `AuthContext`
  existir. É o único ponto a trocar.
- **Snipe IT x GLPI.** A cláusula 11 do termo cita o Snipe IT como sistema de
  controle patrimonial; todo o projeto está desenhado sobre a API do GLPI.
- **Devolução.** É a página 3 do mesmo documento, não um termo separado — muda a
  modelagem de `tipos de termo`.
- **Três assinantes.** Recebedor, gestor e setor de TI exigem `termos` +
  `termo_assinaturas`, não um `status` único.
- **Inconformidade na vistoria.** O texto do termo permite ressalva; falta definir
  se vira recusa do envelope ou observação assinada.
- **Scaffold do frontend.** Só o módulo Checklist (`Checklist.jsx`/`.css` +
  `checklistService.js`) existe hoje. Ainda faltam `package.json`, `vite.config`,
  `index.html`, `main.jsx` e `App.jsx` com as rotas para o frontend rodar de fato.
