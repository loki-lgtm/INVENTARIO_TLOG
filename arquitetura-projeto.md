# Arquitetura do Projeto — Sistema de Gestão de TI (v2)

## Stack
- **Frontend:** React (JavaScript)
- **Backend:** Python + FastAPI
- **Banco de dados:** 
- **Integrações externas:** API do GLPI, API do DocuSign
- **Scheduler:** job diário às 08h para sincronização automática com o GLPI

**Descartado:** o servidor Node.js cru e o uso de `data.json` como armazenamento — substituídos por banco de dados real acessado via FastAPI. Também notei inconsistência no `data.json` atual (nem todo registro tem as 5 chaves preenchidas); no banco novo, todo colaborador deve ter as 5 colunas sempre presentes, com `false` como padrão.

---

## Estrutura de pastas — Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                    # instancia o FastAPI, inclui os routers
│   ├── core/
│   │   ├── config.py              # variáveis de ambiente (.env)
│   │   ├── security.py            # autenticação, hash de senha, sessão/token
│   │   └── scheduler.py           # job agendado (sincronização GLPI 08h)
│   ├── db/
│   │   ├── database.py            # conexão com o banco
│   │   └── base.py                # base do ORM (SQLAlchemy)
│   ├── models/                    # modelos ORM (uma tabela por arquivo)
│   │   ├── usuario.py
│   │   ├── colaborador.py
│   │   ├── centro_custo.py
│   │   ├── item_estoque.py
│   │   ├── movimentacao.py
│   │   ├── licenca.py
│   │   ├── equipamento_entregue.py
│   │   ├── termo.py
│   │   ├── requisicao_compra.py
│   │   └── inventario_colaborador.py
│   ├── schemas/                   # validação Pydantic (entrada/saída da API)
│   │   ├── usuario.py
│   │   ├── estoque.py
│   │   ├── licenca.py
│   │   ├── checklist.py
│   │   ├── termo.py
│   │   ├── compra.py
│   │   └── inventario.py
│   ├── routers/                   # endpoints, um arquivo por módulo
│   │   ├── auth.py
│   │   ├── movimentacoes.py
│   │   ├── estoque.py
│   │   ├── licencas.py
│   │   ├── checklist.py
│   │   ├── termos.py
│   │   ├── compras.py
│   │   ├── glpi.py
│   │   ├── inventario.py          # visão colaborador/departamento
│   │   └── admin.py               # permissões e usuários (Master)
│   ├── services/                  # regras de negócio + integrações externas
│   │   ├── glpi_service.py
│   │   ├── docusign_service.py
│   │   ├── estoque_service.py
│   │   ├── licenca_service.py
│   │   └── inventario_service.py
│   └── utils/
│       └── permissions.py         # checagem de permissão por perfil
├── tests/
├── .env
├── requirements.txt
└── alembic/                       # migrações do banco (se usar SQLAlchemy)
```

## Estrutura de pastas — Frontend (React)

```
frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── routes/
│   │   └── AppRoutes.jsx          # define as rotas de cada página
│   ├── pages/                     # uma pasta por página do sitemap
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   ├── Movimentacoes/
│   │   ├── EstoqueAtual/
│   │   ├── Licencas/
│   │   ├── Checklist/
│   │   ├── Termos/
│   │   ├── Compras/
│   │   ├── VisaoGeralGLPI/
│   │   ├── InventarioColaborador/
│   │   └── Admin/
│   ├── components/
│   │   ├── ui/                    # botão, input, tabela, modal
│   │   ├── layout/                # sidebar, topbar, container
│   │   └── AlertaEstoque.jsx
│   ├── services/                  # chamadas à API, um arquivo por módulo
│   │   ├── api.js                 # instância axios/fetch base
│   │   ├── estoqueService.js
│   │   ├── licencaService.js
│   │   ├── checklistService.js
│   │   ├── termoService.js
│   │   ├── compraService.js
│   │   └── glpiService.js
│   ├── context/
│   │   └── AuthContext.jsx        # usuário logado e permissões
│   ├── hooks/
│   │   └── usePermissions.js
│   └── utils/
├── public/
├── package.json
└── .env
```

---

## Tabelas principais do banco (inicio)

| Tabela | Descrição |
|---|---|
| `usuarios` | Login do sistema, perfil, permissões (Master define) |
| `colaboradores` | Sincronizado do GLPI: nome, e-mail, centro de custo |
| `centros_custo` | Administrativo, CCO Fiscal, Comercial, etc. |
| `itens_estoque` | Nome, quantidade, alerta mínimo — **somente notebook e teclado têm controle real de estoque** |
| `movimentacoes` | Item, tipo (entrada/saída), quantidade, centro de custo, recebedor, status (pendente/confirmado) |
| `licencas_tipo` | Ex: Microsoft 365 Business Standard |
| `licencas_sublicenca` | Ex: standard01...standard18, capacidade = 10 vagas cada |
| `licenca_vinculo` | colaborador_id + sublicenca_id (licença é controle, sem estoque) |
| `equipamentos_entregues` | colaborador_id, mouse, mousepad, teclado, pulso, notebook — substitui o `data.json` |
| `termos` | colaborador_id, tipo, status, id do envelope DocuSign, datas de envio/assinatura |
| `requisicoes_compra` | item, quantidade, fornecedor, status, data do pedido, previsão de chegada |
| `inventario_colaborador` | colaborador_id, notebook (serial), teclado (patrimônio), licença — lançamento manual do TI |

---

## Pontos ainda em aberto (não bloqueiam o início do desenvolvimento)

- Regra da fila de "Pendentes" em Movimentações (aprova ou só histórico?)
- Fluxo detalhado do DocuSign (tipos de termo, ordem de assinatura, o que fazer com status concluído/negado)
- Se a entrada automática em `requisicoes_compra` já vira alta em `itens_estoque`
- Motor de banco de dados definitivo (SQLite vs. PostgreSQL/MySQL)
- Regras de alerta automático por departamento (desproporção de equipamentos)

Essas decisões podem ser fechadas em paralelo enquanto o desenvolvimento das pastas e modelos avança.
