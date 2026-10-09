# Changelog

## [Não lançado]

### Adicionado
- **Identidade visual oficial do Grupo TLOG** aplicada ao frontend: paleta quase monocromática (preto/prata, ver [docs/IDENTIDADE-VISUAL.md](docs/IDENTIDADE-VISUAL.md)), símbolo da marca (`components/brand/TlogMark.jsx` + `public/favicon.svg`) e tipografia Fira Sans/JetBrains Mono (`src/styles/brand.css`, carregada globalmente). Aplicada por inteiro em Sidebar, Login (redesenhado em dois painéis) e Dashboard; Checklist e Estoque por Setor mantêm a paleta e o layout que já tinham, só a fonte foi unificada.
- Módulo **Checklist de periféricos** completo: backend (modelos `ChecklistItem`, `TipoPeriferico`, `CentroCusto`, `Colaborador`; schemas; service; router em `/api/checklist`) e frontend (`pages/Checklist`). 7 testes automatizados.
- Módulo **Estoque por setor** completo: backend (modelos `ItemEstoque`, `EstoqueSetor`; schemas; service; router em `/api/estoque`) e frontend (`pages/EstoquePorSetor`). Cada item de estoque é controlado por setor e por estado de conservação (novo, usado, defeituoso) — uma mesma peça pode ter unidades boas e defeituosas ao mesmo tempo, em setores diferentes. 7 testes automatizados.
- Scaffold completo do frontend (estava só planejado): Vite + React 18 + react-router-dom, `Sidebar` de navegação recolhível, tela de `Login` (sem autenticação real ainda), `Dashboard`, página placeholder genérica para os módulos ainda não construídos.
- `backend/tests/`, `backend/pytest.ini`, `backend/app/seeds.py` — carga inicial idempotente de periféricos, setores e catálogo de itens de estoque.
- `docker-compose.yml` na raiz — sobe um Postgres local para desenvolvimento (banco de dados definido, ver ADR-002 atualizada).
- `.gitignore` na raiz (não existia) — cobre `.venv`, `node_modules`, `__pycache__`, `*.db`, `.env`, `dist/`.
- [docs/MODULO-CHECKLIST.md](docs/MODULO-CHECKLIST.md) e [docs/MODULO-ESTOQUE.md](docs/MODULO-ESTOQUE.md) — decisões de modelagem e pendências de cada módulo.

### Corrigido
- CORS não estava configurado no backend: qualquer chamada do frontend (Vite, porta 5173) para a API era bloqueada pelo navegador, mesmo com os dois servidores rodando corretamente. Adicionado `CORSMiddleware` em `app/main.py`, liberando as origens de desenvolvimento (`backend/app/core/config.py`, `cors_origins`).

### Alterado
- Banco de dados: decisão tomada (ver ADR-002) — SQLite para desenvolvimento local (zero configuração, é o que os testes usam), PostgreSQL para um ambiente compartilhado/produção, via `docker-compose.yml`. Configurável por `DATABASE_URL` em `backend/.env`.
- `README.md`, `docs/ARCHITECTURE.md`, `docs/API.md` e `arquitetura-projeto.md` reescritos para refletir o que existe de fato (o que estava documentado era só o plano anterior ao código). `arquitetura-projeto.md` agora marca cada linha da árvore como pronta, stub ou inexistente, em vez de listar só a intenção original.

### Pendente
- Autenticação (login real, sessão/token, proteção de rotas).
- Regra de aprovação da fila de "Pendentes" em Movimentações.
- Detalhamento do fluxo DocuSign (tipos de termo, ordem de assinatura, tratamento de status).
- Regra de entrada automática no estoque a partir de requisições de compra concluídas.
- Integração real com GLPI (sincronização de colaboradores) — sem ela, o Checklist não tem colaboradores pra listar.
- Migrações de banco (Alembic) — hoje qualquer mudança de modelo exige recriar o banco local.
- Pipeline de CI/CD e estratégia de deploy.
- Módulos ainda sem nenhum código: Movimentações, Licenças, Termos, Compras, Visão Geral/Importação GLPI, Inventário por colaborador, Administração.
