# Arquitetura da Aplicação

## Componentes

| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| Frontend | React 18 + react-router-dom (Vite) | Telas, componentes de UI, consumo da API via `fetch` |
| Backend | Python + FastAPI | Rotas, regras de negócio, integrações externas, job agendado |
| Banco de dados | SQLite (desenvolvimento e testes) / PostgreSQL (ambiente compartilhado, via `docker-compose.yml`) — ver [ADR-002](adr/ADR-002-banco-de-dados.md) | Persistência de todas as entidades do sistema |
| GLPI (externo) | API REST | Fonte de colaboradores, e-mails e notebooks — **ainda não integrado**, só o stub `glpi_service.py` existe |
| DocuSign (externo) | API/SDK | Envio e assinatura de termos — **ainda não integrado**, só o stub `docusign_service.py` existe |

## Fluxo de dados (alto nível)

1. Frontend faz chamadas HTTP/REST para o backend (`fetch`, sem axios), sempre por `src/services/*.js`.
2. Backend aplica regras de negócio em `app/services/*.py` e lê/grava no banco via SQLAlchemy (`app/models/*.py`).
3. (Planejado, não implementado) Backend consome a API do GLPI: sincronização automática diária às 08h (`app/core/scheduler.py`, hoje vazio) + botão de sincronização manual.
4. (Planejado, não implementado) Backend consome a API do DocuSign: envia termo para assinatura e recebe callback de status (assinado/negado).

## Estrutura de pastas

A árvore completa de backend e frontend, com o que já existe marcado, está em [arquitetura-projeto.md](../arquitetura-projeto.md).

## Status de implementação por módulo

| Módulo | Backend | Frontend | Observação |
|---|---|---|---|
| Checklist de periféricos | Implementado | Implementado | Ver [docs/MODULO-CHECKLIST.md](MODULO-CHECKLIST.md) |
| Estoque por setor | Implementado | Implementado | Ver [docs/MODULO-ESTOQUE.md](MODULO-ESTOQUE.md) |
| Autenticação e permissões | Não iniciado | Tela estática (`Login.jsx`), sem chamada de API | Login não valida nada; nenhuma rota é protegida |
| Movimentações (entrada/saída) | Não iniciado | Placeholder por departamento | — |
| Licenças | Não iniciado | Placeholder | — |
| Termos (DocuSign) | Não iniciado | Placeholder | — |
| Compras / Requisições | Não iniciado | Placeholder | — |
| Visão Geral / Importação GLPI | Não iniciado | Placeholder | — |
| Inventário por colaborador/departamento | Não iniciado | Não existe rota ainda | — |
| Administração (usuários/permissões) | Não iniciado | Não existe rota ainda | — |

## Mapa de funções e conexões de API (módulos implementados)

Cada módulo segue a mesma cadeia de chamadas, de ponta a ponta. É o padrão a repetir nos próximos módulos.

```
Componente React (pages/<Modulo>/<Modulo>.jsx)
        |  chama funções de
        v
Serviço do frontend (services/<modulo>Service.js)
        |  faz fetch() via services/api.js (base VITE_API_URL, default http://localhost:8000/api)
        v
Router do FastAPI (app/routers/<modulo>.py)
        |  delega regra de negócio para
        v
Service do backend (app/services/<modulo>_service.py)
        |  lê/grava via SQLAlchemy
        v
Modelos (app/models/*.py)  <-->  Banco de dados
```

### Checklist de periféricos

| Tela / função no frontend | Chama (`checklistService.js`) | Endpoint | Função no backend (`checklist_service.py`) | Toca as tabelas |
|---|---|---|---|---|
| Carrega a lista de setores da nav lateral | `listarSetores()` | `GET /api/checklist/setores` | `resumo_por_setor()` | `centros_custo`, `checklist_itens`, `tipos_periferico` |
| Carrega a matriz colaborador x periférico | `listar({centroCustoId, busca, apenasPendentes})` | `GET /api/checklist` | `listar_checklist()` | `colaboradores`, `tipos_periferico`, `checklist_itens` |
| Marca/desmarca um periférico (autosave do checkbox) | `marcar(colaboradorId, tipoId, {entregue, marcadoPor})` | `PUT /api/checklist/{colaborador_id}/{tipo_periferico_id}` | `marcar_item()` | `checklist_itens` (upsert) |

Princípio de design do módulo: a matriz devolvida por `GET /api/checklist` é sempre completa — todo colaborador ativo aparece com todos os periféricos ativos, mesmo sem nenhuma marcação (quantidade/estado default). Ver detalhes e decisões em [docs/MODULO-CHECKLIST.md](MODULO-CHECKLIST.md).

### Estoque por setor

| Tela / função no frontend | Chama (`estoqueService.js`) | Endpoint | Função no backend (`estoque_service.py`) | Toca as tabelas |
|---|---|---|---|---|
| Carrega a lista de setores da nav lateral | `listarSetores()` | `GET /api/estoque/setores` | `resumo_por_setor()` | `centros_custo`, `estoque_setor` |
| Carrega o catálogo de itens (não usado hoje na tela, disponível pra futura tela de cadastro) | `listarItens()` | `GET /api/estoque/itens` | `listar_itens()` | `itens_estoque` |
| Carrega a matriz item x estado de um setor | `buscarPorSetor(centroCustoId)` | `GET /api/estoque/{centro_custo_id}` | `estoque_do_setor()` | `itens_estoque`, `estoque_setor` |
| Salva a quantidade de uma célula (autosave no blur) | `atualizarSaldo(centroCustoId, itemEstoqueId, estado, {quantidade})` | `PUT /api/estoque/{centro_custo_id}/{item_estoque_id}/{estado}` | `atualizar_saldo()` | `estoque_setor` (upsert) |

Princípio de design do módulo: o saldo não é por (setor, item) — é por (setor, item, estado de conservação). Um mesmo item pode ter unidades novas e defeituosas ao mesmo tempo no mesmo setor, cada uma em sua própria linha de `estoque_setor`. Ver detalhes e decisões em [docs/MODULO-ESTOQUE.md](MODULO-ESTOQUE.md).

### Por que "sempre completo" em vez de "só o que existe"

Os dois módulos compartilham a mesma regra: a API nunca omite uma combinação válida (colaborador x periférico, ou item x estado) só porque não há registro no banco — ela devolve zero/falso explícito. Isso corrige o defeito do `data.json` do sistema anterior, em que um registro podia não ter todas as chaves preenchidas, e o frontend não tinha como distinguir "false" de "não sei". Ver a íntegra da decisão em [docs/MODULO-CHECKLIST.md](MODULO-CHECKLIST.md).

## CORS

O backend só aceita chamadas do frontend vindas das origens em `settings.cors_origins` (`app/core/config.py`), hoje `http://localhost:5173` e `http://127.0.0.1:5173` — as duas formas como o Vite normalmente sobe em dev. Configurado em `app/main.py` via `CORSMiddleware`. Qualquer origem fora dessa lista tem as chamadas bloqueadas pelo navegador (não pelo backend — a resposta HTTP existe, só não vem com o cabeçalho `Access-Control-Allow-Origin`, e o navegador descarta).

## Modelo de dados

### Tabelas implementadas

| Tabela | Modelo | Descrição |
|---|---|---|
| `colaboradores` | `Colaborador` | nome, email, cargo, `centro_custo_id`, ativo |
| `centros_custo` | `CentroCusto` | nome, ativo, `gestor_id` (aponta para um colaborador) |
| `tipos_periferico` | `TipoPeriferico` | catálogo de periféricos entregáveis (nome, slug, ordem, ativo) |
| `checklist_itens` | `ChecklistItem` | entrega de um periférico a um colaborador: entregue, data, `marcado_por` |
| `itens_estoque` | `ItemEstoque` | catálogo de tipos de equipamento (nome, categoria, alerta mínimo, ativo) |
| `estoque_setor` | `EstoqueSetor` | saldo de um item, em um setor, em um estado de conservação (novo/usado/defeituoso) |

### Tabelas ainda não implementadas (só na documentação de requisitos)

| Tabela | Descrição |
|---|---|
| `usuarios` | Login do sistema, perfil, permissões |
| `movimentacoes` | Item, tipo (entrada/saída), quantidade, centro de custo, recebedor, status |
| `licencas_tipo` / `licencas_sublicenca` / `licenca_vinculo` | Controle de licenças de software |
| `termos` | colaborador_id, tipo, status, id do envelope DocuSign, datas |
| `requisicoes_compra` | item, quantidade, fornecedor, status, previsão de chegada |
| `inventario_colaborador` | colaborador_id, notebook (serial), teclado (patrimônio), licença |

## Decisões em aberto que afetam a arquitetura

- Regra de aprovação da fila de "Pendentes" em Movimentações
- Detalhamento do fluxo DocuSign (tipos de termo, ordem de assinatura)
- Se a chegada de uma requisição de compra gera alta automática no estoque (e em qual estado de conservação ela entra — "novo" por padrão, presumivelmente)
- Estratégia de autenticação entre frontend e backend (sessão ou token) — nada implementado ainda, incluindo no lado do backend (não há middleware de auth em nenhum router hoje)
- Migrações de banco (Alembic) — ver [ADR-002](adr/ADR-002-banco-de-dados.md)
