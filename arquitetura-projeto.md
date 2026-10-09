# Arquitetura do Projeto — Sistema de Gestão de TI (v2)

> Este documento nasceu como o plano de pastas antes de existir código. As árvores abaixo continuam sendo o plano completo, mas agora cada linha está marcada com o que realmente existe — use a legenda para não confundir "já dá pra rodar" com "só está no papel".
>
> Legenda: `[pronto]` tem código funcional e, quando é backend, teste automatizado — `[stub]` o arquivo existe mas está vazio — `[não existe]` nem o arquivo foi criado ainda.

## Stack
- **Frontend:** React (JavaScript) + react-router-dom, servido por Vite — `[pronto]` (scaffold)
- **Backend:** Python + FastAPI — `[pronto]`
- **Banco de dados:** SQLite em desenvolvimento/testes, PostgreSQL via `docker-compose.yml` em ambiente compartilhado — `[pronto]`, ver [ADR-002](docs/adr/ADR-002-banco-de-dados.md)
- **Integrações externas:** API do GLPI, API do DocuSign — `[não existe]`, só os stubs de serviço
- **Scheduler:** job diário às 08h para sincronização automática com o GLPI — `[stub]` (`app/core/scheduler.py` vazio)

**Descartado:** o servidor Node.js cru e o uso de `data.json` como armazenamento — substituídos por banco de dados real acessado via FastAPI. Também notei inconsistência no `data.json` atual (nem todo registro tem as 5 chaves preenchidas); no banco novo, todo colaborador deve ter as 5 colunas sempre presentes, com `false` como padrão. Essa regra foi implementada nos dois módulos prontos (ver "matriz sempre completa" em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

---

## Estrutura de pastas — Backend (FastAPI)

```
backend/
├── requirements.txt                       [pronto]
├── .env.example                           [pronto]
├── pytest.ini                             [pronto] — não estava no plano original, necessário pro pytest achar o pacote app/
├── app/
│   ├── main.py                            [pronto] — instancia o FastAPI, CORS, inclui os routers prontos
│   ├── seeds.py                           [pronto] — não estava no plano original; carga inicial idempotente
│   ├── core/
│   │   ├── config.py                      [pronto] — variáveis de ambiente (.env) via pydantic-settings
│   │   ├── security.py                    [não existe] — autenticação, hash de senha, sessão/token
│   │   └── scheduler.py                   [stub] — job agendado (sincronização GLPI 08h)
│   ├── db/
│   │   ├── database.py                    [pronto] — engine, SessionLocal, get_db
│   │   └── base.py                        [pronto] — Base declarativa + TimestampMixin (created_at/updated_at)
│   ├── models/                            uma tabela por arquivo
│   │   ├── usuario.py                     [stub]
│   │   ├── colaborador.py                 [pronto]
│   │   ├── centro_custo.py                [pronto]
│   │   ├── item_estoque.py                [pronto]
│   │   ├── estoque_setor.py               [pronto] — não estava no plano original; ver docs/MODULO-ESTOQUE.md
│   │   ├── movimentacao.py                [stub]
│   │   ├── licenca.py                     [stub]
│   │   ├── equipamento_entregue.py        [stub] — o papel dele foi assumido por checklist.py (ChecklistItem)
│   │   ├── checklist.py                   [pronto] — não estava no plano original com esse nome
│   │   ├── tipo_periferico.py             [pronto] — não estava no plano original; catálogo de periféricos
│   │   ├── termo.py                       [stub]
│   │   ├── requisicao_compra.py           [stub]
│   │   └── inventario_colaborador.py      [não existe]
│   ├── schemas/                           validação Pydantic (entrada/saída da API)
│   │   ├── usuario.py                     [não existe]
│   │   ├── estoque.py                     [pronto]
│   │   ├── licenca.py                     [não existe]
│   │   ├── checklist.py                   [pronto]
│   │   ├── termo.py                       [não existe]
│   │   ├── compra.py                      [não existe]
│   │   └── inventario.py                  [não existe]
│   ├── routers/                           endpoints, um arquivo por módulo
│   │   ├── auth.py                        [stub]
│   │   ├── movimentacoes.py               [stub]
│   │   ├── estoque.py                     [pronto] — GET /itens, /setores, /{id}; PUT /{id}/{item}/{estado}
│   │   ├── licencas.py                    [stub]
│   │   ├── checklist.py                   [pronto] — GET /tipos, /setores, ""; PUT /{colaborador}/{tipo}
│   │   ├── termos.py                      [stub]
│   │   ├── compras.py                     [stub]
│   │   ├── glpi.py                        [stub]
│   │   ├── inventario.py                  [não existe]
│   │   └── admin.py                       [não existe]
│   ├── services/                          regras de negócio + integrações externas
│   │   ├── glpi_service.py                [stub]
│   │   ├── docusign_service.py            [stub]
│   │   ├── estoque_service.py             [pronto]
│   │   ├── checklist_service.py           [pronto] — não estava no plano original com esse nome
│   │   ├── licenca_service.py             [não existe]
│   │   └── inventario_service.py          [não existe]
│   └── utils/
│       └── permissions.py                 [não existe] — checagem de permissão por perfil
├── tests/                                 [pronto] — test_checklist.py (7 casos), test_estoque.py (7 casos)
├── .env                                   [não existe] — cada dev cria o seu a partir de .env.example, não vai pro git
└── alembic/                               [não existe] — migrações do banco
```

## Estrutura de pastas — Frontend (React)

```
frontend/
├── package.json                           [pronto]
├── vite.config.js                         [pronto] — não estava no plano original
├── index.html                             [pronto] — não estava no plano original
├── .env.example                           [pronto] — não estava no plano original
├── .env                                   [não existe] — opcional; sem ele, VITE_API_URL cai no default http://localhost:8000/api
├── src/
│   ├── main.jsx                           [pronto]
│   ├── App.jsx                            [pronto] — define as rotas direto (ver abaixo)
│   ├── routes/
│   │   └── AppRoutes.jsx                  [não existe] — as rotas ficaram dentro do próprio App.jsx, não foram extraídas
│   ├── pages/                             uma pasta por página do sitemap
│   │   ├── Login/                         [pronto] — tela pronta, sem chamada de API (não autentica de verdade)
│   │   ├── Dashboard/                     [pronto]
│   │   ├── Movimentacoes/                 [não existe] — rota /movimentacao/:departamento usa PlaceholderPage.jsx
│   │   ├── EstoqueAtual/                  [não existe] — virou EstoquePorSetor/ (ver decisão em docs/MODULO-ESTOQUE.md)
│   │   ├── EstoquePorSetor/               [pronto] — não estava no plano original
│   │   ├── Licencas/                      [não existe] — rota /compras usa PlaceholderPage.jsx
│   │   ├── Checklist/                     [pronto]
│   │   ├── Termos/                        [não existe] — rota /termos usa PlaceholderPage.jsx
│   │   ├── Compras/                       [não existe] — rota /compras usa PlaceholderPage.jsx
│   │   ├── VisaoGeralGLPI/                [não existe] — rota /integracoes/:sistema usa PlaceholderPage.jsx
│   │   ├── InventarioColaborador/         [não existe] — sem rota ainda
│   │   ├── Admin/                         [não existe] — sem rota ainda
│   │   └── PlaceholderPage.jsx            [pronto] — não estava no plano original; cobre todas as páginas acima ainda não construídas
│   ├── components/
│   │   ├── ui/                            [não existe] — botão, input, tabela, modal (cada página estiliza os próprios elementos por enquanto)
│   │   ├── layout/                        [pronto] — Sidebar.jsx + Layout.jsx (não estava especificado no plano original quais arquivos)
│   │   └── AlertaEstoque.jsx              [não existe]
│   ├── services/                          chamadas à API, um arquivo por módulo
│   │   ├── api.js                         [pronto] — fetch, não axios (o plano original cogitava os dois)
│   │   ├── estoqueService.js              [pronto]
│   │   ├── licencaService.js              [não existe]
│   │   ├── checklistService.js            [pronto]
│   │   ├── termoService.js                [não existe]
│   │   ├── compraService.js               [não existe]
│   │   └── glpiService.js                 [não existe]
│   ├── context/
│   │   └── AuthContext.jsx                [não existe] — usuário logado e permissões
│   ├── hooks/
│   │   └── usePermissions.js              [não existe]
│   └── utils/                             [não existe]
├── public/                                [não existe] — não precisou até agora
└── package-lock.json                      [pronto]
```

---

## Tabelas principais do banco

| Tabela | Descrição | Status |
|---|---|---|
| `usuarios` | Login do sistema, perfil, permissões (Master define) | Não implementada |
| `colaboradores` | Sincronizado do GLPI: nome, e-mail, centro de custo | Implementada — sincronização com GLPI ainda não existe, hoje só é possível cadastrar manualmente |
| `centros_custo` | Administrativo, CCO Fiscal, Comercial, etc. | Implementada — "CCO Fiscal" segue fora do seed, ver pendência abaixo |
| `itens_estoque` | Catálogo de tipos de equipamento (nome, categoria, alerta mínimo) | Implementada — modelo mudou de "quantidade única" para "catálogo + saldo por setor/estado", ver `estoque_setor` |
| `estoque_setor` | Saldo de um item, por setor, por estado de conservação (novo/usado/defeituoso) | Implementada — não estava neste documento originalmente |
| `movimentacoes` | Item, tipo (entrada/saída), quantidade, centro de custo, recebedor, status (pendente/confirmado) | Não implementada |
| `licencas_tipo` | Ex: Microsoft 365 Business Standard | Não implementada |
| `licencas_sublicenca` | Ex: standard01...standard18, capacidade = 10 vagas cada | Não implementada |
| `licenca_vinculo` | colaborador_id + sublicenca_id (licença é controle, sem estoque) | Não implementada |
| `tipos_periferico` | Catálogo de periféricos entregáveis (Mouse, Teclado...) | Implementada — não estava neste documento originalmente |
| `checklist_itens` | colaborador_id + tipo_periferico_id + entregue + data + marcado_por | Implementada — substitui `equipamentos_entregues` do plano original (colunas fixas viraram linhas) |
| `termos` | colaborador_id, tipo, status, id do envelope DocuSign, datas de envio/assinatura | Não implementada |
| `requisicoes_compra` | item, quantidade, fornecedor, status, data do pedido, previsão de chegada | Não implementada |
| `inventario_colaborador` | colaborador_id, notebook (serial), teclado (patrimônio), licença — lançamento manual do TI | Não implementada |

## Pontos ainda em aberto (não bloqueiam o andamento do desenvolvimento)

- Regra da fila de "Pendentes" em Movimentações (aprova ou só histórico?)
- Fluxo detalhado do DocuSign (tipos de termo, ordem de assinatura, o que fazer com status concluído/negado)
- Se a entrada automática em `requisicoes_compra` já vira alta em `itens_estoque`/`estoque_setor`
- Autenticação (nenhuma implementação ainda, nem no frontend nem no backend)
- Migrações de banco (Alembic) — ver [ADR-002](docs/adr/ADR-002-banco-de-dados.md)
- "CCO Fiscal", citado neste documento como setor, não está no seed de centros de custo (`app/seeds.py`) — não foi esclarecido se é setor próprio ou outro nome para Controladoria

Essas decisões podem ser fechadas em paralelo enquanto o desenvolvimento dos módulos restantes avança — foi assim que Checklist e Estoque por Setor avançaram antes de autenticação e GLPI estarem prontos.
