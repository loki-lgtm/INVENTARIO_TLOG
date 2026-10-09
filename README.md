# Sistema de Gestão de TI (v2)

## Visão geral

Sistema web interno para centralizar a gestão de infraestrutura de TI: controle de estoque de equipamentos por setor, checklist de entrega de periféricos por colaborador, termos de responsabilidade (via DocuSign), requisições de compra e inventário por colaborador/departamento — com integração direta à API do GLPI.

Este projeto é a reconstrução do sistema anterior (feito em Python/Streamlit). O objetivo é ter controle total sobre design, responsividade e arquitetura, mantendo as integrações já existentes e adicionando novas.

## Status do projeto

Saiu da fase de levantamento de requisitos. Existem hoje dois módulos completos e testados (backend + frontend) e um scaffold funcional do frontend em volta deles. O restante do sistema (autenticação, movimentações, licenças, termos, compras, GLPI, DocuSign) ainda está apenas modelado na documentação, sem código.

| Módulo | Backend | Frontend | Testes |
|---|---|---|---|
| Checklist de periféricos | Pronto | Pronto | 7 testes, `backend/tests/test_checklist.py` |
| Estoque por setor | Pronto | Pronto | 7 testes, `backend/tests/test_estoque.py` |
| Autenticação | Não iniciado | Tela estática (`Login.jsx`), sem chamada de API | — |
| Movimentações, Compras, Relatórios, Termos, Integrações (GLPI/DocuSign), Configurações | Não iniciado | Tela placeholder genérica | — |

Detalhe de cada módulo pronto: [docs/MODULO-CHECKLIST.md](docs/MODULO-CHECKLIST.md) e [docs/MODULO-ESTOQUE.md](docs/MODULO-ESTOQUE.md). Mapa completo de como o frontend fala com o backend: [docs/API.md](docs/API.md) e [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Como rodar (ambiente local)

Pré-requisitos: Python 3.11+ e Node 18+ instalados. Não é preciso Docker/PostgreSQL para rodar localmente — o backend usa SQLite por padrão quando não existe `backend/.env`.

### 1. Backend

```
cd backend
python -m venv .venv
.venv\Scripts\activate          # PowerShell. No git-bash: source .venv/Scripts/activate
pip install -r requirements.txt
python -m app.seeds             # cria as tabelas em backend/app.db e carrega os dados iniciais
uvicorn app.main:app --reload --port 8000
```

O backend sobe em `http://localhost:8000`. A documentação interativa (Swagger) fica em `http://localhost:8000/docs` — dá para testar qualquer endpoint por ali, sem precisar do frontend no ar.

`python -m app.seeds` é obrigatório antes do primeiro `uvicorn`: o `main.py` não cria as tabelas sozinho (não há `Base.metadata.create_all` no startup, de propósito — ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)). Sem rodar o seed, qualquer chamada à API quebra com erro de tabela inexistente. É seguro rodar de novo a qualquer momento: o seed só insere o que ainda não existe (idempotente).

### 2. Frontend

Em um segundo terminal, com o backend já no ar:

```
cd frontend
npm install
npm run dev
```

Abre em `http://localhost:5173`.

### 3. Banco de dados real (PostgreSQL), opcional

Para rodar contra Postgres em vez do SQLite local (mais parecido com um ambiente compartilhado/produção):

```
docker compose up -d db
```

Depois copie `backend/.env.example` para `backend/.env` — ele já aponta para o Postgres do `docker-compose.yml` (`postgresql+psycopg2://tlog:tlog@localhost:5432/inventario_tlog`). Rode `python -m app.seeds` de novo depois de trocar de banco: o SQLite e o Postgres são bancos separados, cada um com seu próprio schema.

Atenção: até hoje só o caminho do SQLite foi de fato exercitado (é o que os testes automatizados usam e o que foi testado manualmente no navegador). O caminho do Postgres/docker-compose ainda não foi validado na prática — se aparecer algum erro de conexão ou de driver (`psycopg2`) ao usar essa opção, é o primeiro lugar a olhar.

## Como testar

**Backend (automatizado):**

```
cd backend
pytest tests/ -q
```

14 testes hoje (7 de checklist, 7 de estoque), todos em SQLite em memória — não dependem de `app.db` nem de Postgres.

**Frontend (manual, não há testes automatizados ainda):** com os dois servidores no ar, abra `http://localhost:5173` e confira:
- A Sidebar abre e recolhe; os itens do menu levam às rotas certas.
- **Checklist** — se o seed não criou nenhum colaborador (ele não cria; ver "Falhas conhecidas" abaixo), a tabela aparece vazia com a mensagem "Nenhum colaborador cadastrado". Isso é esperado, não é erro.
- **Estoque** — a nav lateral mostra os 7 setores do seed; ao selecionar um, a tabela mostra os 10 itens do catálogo, todos com quantidade 0 em Novo/Usado/Defeituoso. Digite um número em qualquer célula e saia do campo (blur): o valor deve ser salvo (confirme recarregando a página) e o total da linha atualizar.
- Os demais itens do menu (Movimentação, Compras, Relatórios, Termos, Integrações, Configurações) mostram a tela "em construção" — é o estado esperado, não uma falha.

## Falhas conhecidas e limitações atuais

- **Checklist aparece vazio.** O seed (`app/seeds.py`) cria os 7 periféricos, os 7 setores e os 10 itens de estoque, mas nenhum colaborador — colaboradores viriam da sincronização com o GLPI, que ainda não existe. Para ver o Checklist com dados, é preciso inserir colaboradores manualmente (via `/docs` no backend, ou direto no banco).
- **CORS.** O backend só libera as origens `http://localhost:5173` e `http://127.0.0.1:5173` (ver `backend/app/core/config.py`, `cors_origins`). Se o Vite subir em outra porta (acontece quando a 5173 já está ocupada) ou você acessar por outro host, as chamadas do frontend para a API falham silenciosamente no navegador com erro de CORS — abra o console do navegador para confirmar, e adicione a origem nova na lista.
- **Sem autenticação.** `Login.jsx` é só uma tela — não valida usuário/senha, não gera sessão nem token, e nenhuma rota do frontend ou do backend está protegida. Qualquer pessoa com acesso à rede acessa tudo.
- **Sem migrações de banco.** Não há Alembic configurado. Mudar um modelo hoje exige apagar `backend/app.db` e rodar `python -m app.seeds` de novo (perde dados locais) — não há caminho de migração incremental ainda.
- **`node_modules` e `.venv` não estão no repositório** (cobertos pelo `.gitignore`, junto com `*.db`, `.env` e `dist/`) — depois de clonar o repositório em outra máquina, é preciso rodar `pip install` e `npm install` de novo antes de qualquer coisa funcionar.
- **GLPI e DocuSign não estão integrados.** Os arquivos `backend/app/services/glpi_service.py` e `docusign_service.py` existem como stubs vazios; as variáveis de ambiente já estão previstas em `.env.example`, mas nenhuma chamada real foi implementada.

## Arquitetura

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para o desenho de componentes, o status de cada módulo e o mapa de como cada tela do frontend conversa com o backend (função a função). Ver [docs/API.md](docs/API.md) para a referência de cada endpoint já implementado.

## Deploy

Ver [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — pipeline de CI/CD ainda não definido. O `docker-compose.yml` na raiz hoje só sobe o banco Postgres para desenvolvimento local, não é uma estratégia de deploy.

## Troubleshooting

Ver [docs/RUNBOOK.md](docs/RUNBOOK.md) para o único incidente já registrado (sistema anterior). Para problemas do ambiente local de desenvolvimento, ver "Falhas conhecidas" acima.

## Documentação relacionada

- [Requisitos funcionais completos](requisitos-sistema-gestao-ti.md)
- [Árvore de pastas — backend e frontend, planejada vs. o que já existe](arquitetura-projeto.md)
- [Módulo Checklist — decisões e pendências](docs/MODULO-CHECKLIST.md)
- [Módulo Estoque por Setor — decisões e pendências](docs/MODULO-ESTOQUE.md)
- [Identidade visual — tokens de marca e onde cada um é usado](docs/IDENTIDADE-VISUAL.md)
- [Decisões técnicas (ADR)](docs/adr/)
- [Changelog](CHANGELOG.md)
