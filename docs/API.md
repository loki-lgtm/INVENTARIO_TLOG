# API — Endpoints

> Este documento será preenchido conforme os endpoints forem implementados. O FastAPI gera documentação automática (Swagger/OpenAPI) em `/docs` — use-a como fonte de verdade complementar durante o desenvolvimento; este arquivo serve como referência estável para quem não tem o backend rodando localmente.

## Routers previstos

| Router | Prefixo sugerido | Módulo relacionado |
|---|---|---|
| `auth.py` | `/auth` | Autenticação e sessão |
| `movimentacoes.py` | `/movimentacoes` | Entrada/saída de estoque |
| `estoque.py` | `/estoque` | Estoque atual |
| `licencas.py` | `/licencas` | Licenças e sub-licenças |
| `checklist.py` | `/checklist` | Checklist de equipamentos |
| `termos.py` | `/termos` | Termos via DocuSign |
| `compras.py` | `/compras` | Requisições de compra |
| `glpi.py` | `/glpi` | Sincronização e visão geral GLPI |
| `inventario.py` | `/inventario` | Inventário por colaborador/departamento |
| `admin.py` | `/admin` | Usuários e permissões (Master) |

## Formato de cada endpoint (a preencher conforme implementado)

```
### [MÉTODO] /caminho

**Descrição:**
**Permissão necessária:**
**Parâmetros de entrada:**
**Resposta (200):**
**Possíveis erros:**
```
