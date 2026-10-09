# API — Endpoints

> O FastAPI gera documentação automática (Swagger/OpenAPI) em `http://localhost:8000/docs` — use-a como fonte de verdade complementar com o backend rodando localmente (é a forma mais rápida de testar um endpoint na mão). Este arquivo serve de referência estável pra quem não tem o backend no ar, e explica o "porquê" por trás de cada rota, que o Swagger não mostra.

Todas as rotas abaixo estão montadas sob o prefixo `/api` (definido em `app/main.py`), além do prefixo do próprio router. Nenhuma rota exige autenticação hoje — isso é uma lacuna conhecida, não uma decisão de design (ver [README.md](../README.md), seção "Falhas conhecidas").

## Routers implementados

### `checklist.py` — prefixo `/api/checklist`

Entrega de periféricos por colaborador. Modelagem completa em [docs/MODULO-CHECKLIST.md](MODULO-CHECKLIST.md).

#### `GET /api/checklist/tipos`

Lista os tipos de periférico ativos, na ordem em que aparecem no termo de responsabilidade.

**Resposta 200:**
```json
[
  { "id": 1, "nome": "Mouse", "slug": "mouse", "ordem": 1, "ativo": true, "observacao": null }
]
```

#### `GET /api/checklist/setores`

Progresso de entrega por setor — usado pela nav lateral da tela de Checklist.

**Resposta 200:**
```json
[
  {
    "id": 1, "nome": "TI",
    "total_colaboradores": 4, "colaboradores_completos": 1,
    "itens_entregues": 12, "itens_previstos": 28,
    "percentual": 42.9
  }
]
```

#### `GET /api/checklist`

Matriz colaborador x periférico. Sempre completa: todo colaborador ativo do filtro aparece com todos os periféricos ativos, mesmo sem nenhuma marcação (`entregue: false`).

**Parâmetros de query (todos opcionais):**
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `centro_custo_id` | int | Filtra por setor |
| `busca` | string (até 180 caracteres) | Busca em nome ou e-mail do colaborador |
| `apenas_pendentes` | bool | Só colaboradores com algum item ainda não entregue |
| `pagina` | int, padrão 1 | Paginação |
| `tamanho_pagina` | int, padrão 50, máx. 200 | Paginação |

**Resposta 200:**
```json
{
  "tipos": [{ "id": 1, "nome": "Mouse", "slug": "mouse", "ordem": 1, "ativo": true, "observacao": null }],
  "colaboradores": [
    {
      "id": 10, "nome": "Ana Ribeiro", "email": "ana.ribeiro@tlog.com.br", "cargo": "Analista",
      "centro_custo": { "id": 1, "nome": "TI" },
      "itens": [{ "tipo_periferico_id": 1, "entregue": false, "data_entrega": null, "marcado_por": null }],
      "entregues": 0, "total": 7, "completo": false
    }
  ],
  "total": 1, "pagina": 1, "tamanho_pagina": 50
}
```

#### `PUT /api/checklist/{colaborador_id}/{tipo_periferico_id}`

Marca ou desmarca a entrega de um periférico. Idempotente — chamar duas vezes com o mesmo corpo não muda o resultado. É o endpoint por trás do autosave do checkbox na tela.

**Corpo da requisição:**
```json
{ "entregue": true, "marcado_por": "suporte.ti@tlog.com.br", "observacao": null }
```
`marcado_por` e `observacao` são opcionais. Desmarcar (`entregue: false`) sempre limpa `data_entrega` — uma entrega desfeita não tem data.

**Resposta 200:**
```json
{
  "colaborador_id": 10, "tipo_periferico_id": 1, "entregue": true,
  "data_entrega": "2026-09-13T12:00:00Z", "marcado_por": "suporte.ti@tlog.com.br",
  "entregues": 1, "total": 7, "completo": false
}
```

**Erros:** `404` se `colaborador_id` ou `tipo_periferico_id` não existir, ou se o tipo de periférico estiver inativo.

---

### `estoque.py` — prefixo `/api/estoque`

Saldo de equipamentos por setor e por estado de conservação. Modelagem completa em [docs/MODULO-ESTOQUE.md](MODULO-ESTOQUE.md).

#### `GET /api/estoque/itens`

Catálogo de tipos de equipamento ativos (não é o saldo — é só o cadastro: nome, categoria, alerta mínimo).

**Resposta 200:**
```json
[{ "id": 1, "nome": "Mouse USB", "categoria": "Periferico", "alerta_minimo": 15, "ativo": true }]
```

#### `GET /api/estoque/setores`

Total em estoque e total defeituoso por setor — usado pela nav lateral da tela de Estoque.

**Resposta 200:**
```json
[{ "id": 1, "nome": "TI", "total_itens": 34, "total_defeituosos": 2 }]
```

#### `GET /api/estoque/{centro_custo_id}`

Matriz item x estado de conservação de um setor. Sempre completa: todo item ativo do catálogo aparece com os três estados (`novo`, `usado`, `defeituoso`), quantidade `0` quando não há lançamento.

**Resposta 200:**
```json
{
  "centro_custo_id": 1, "centro_custo_nome": "TI",
  "itens": [
    {
      "item_estoque_id": 1, "nome": "Mouse USB", "categoria": "Periferico", "alerta_minimo": 15,
      "saldos": [
        { "estado": "novo", "quantidade": 10 },
        { "estado": "usado", "quantidade": 3 },
        { "estado": "defeituoso", "quantidade": 1 }
      ],
      "total": 14, "abaixo_do_minimo": true
    }
  ]
}
```

**Erros:** `404` se `centro_custo_id` não existir.

#### `PUT /api/estoque/{centro_custo_id}/{item_estoque_id}/{estado}`

Grava/atualiza a quantidade de um item, em um setor, em um estado de conservação. `estado` faz parte do caminho da URL e só aceita `novo`, `usado` ou `defeituoso` — o FastAPI valida isso automaticamente antes de chegar no código de negócio.

**Corpo da requisição:**
```json
{ "quantidade": 12, "observacao": null }
```
`quantidade` não pode ser negativa. `observacao` é opcional.

**Resposta 200:**
```json
{ "estado": "novo", "quantidade": 12 }
```

**Erros:** `404` se `centro_custo_id` ou `item_estoque_id` não existir. `422` se `estado` não for um dos três valores válidos (validação automática do FastAPI, não é um erro de negócio).

## Routers planejados (sem código ainda)

| Router | Prefixo previsto | Módulo relacionado |
|---|---|---|
| `auth.py` | `/auth` | Autenticação e sessão |
| `movimentacoes.py` | `/movimentacoes` | Entrada/saída de estoque, fila de pendentes |
| `licencas.py` | `/licencas` | Licenças e sub-licenças |
| `termos.py` | `/termos` | Termos via DocuSign |
| `compras.py` | `/compras` | Requisições de compra |
| `glpi.py` | `/glpi` | Sincronização e visão geral GLPI |
| `inventario.py` | `/inventario` | Inventário por colaborador/departamento |
| `admin.py` | `/admin` | Usuários e permissões (Master) |

Ao implementar um novo router, seguir o padrão dos dois já prontos: um arquivo de schema Pydantic por módulo em `app/schemas/`, a regra de negócio isolada em `app/services/<modulo>_service.py` (o router só valida entrada e converte `ValueError` em `HTTPException`), e um arquivo de teste equivalente em `backend/tests/`.
