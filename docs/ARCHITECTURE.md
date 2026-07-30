# Arquitetura da Aplicação

## Componentes

| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| Frontend | React (JavaScript) | Telas, componentes de UI, consumo da API via HTTP |
| Backend | Python + FastAPI | Rotas, regras de negócio, integrações externas, job agendado |
| Banco de dados | **Pendente** (ver [ADR-002](adr/ADR-002-banco-de-dados.md)) | Persistência de todas as entidades do sistema |
| GLPI (externo) | API REST | Fonte de colaboradores, e-mails e notebooks |
| DocuSign (externo) | API/SDK | Envio e assinatura de termos |

## Fluxo de dados (alto nível)
1. Frontend faz chamadas HTTP/REST para o backend.
2. Backend aplica regras de negócio e lê/grava no banco de dados.
3. Backend consome a API do GLPI: sincronização automática diária às 08h + botão de sincronização manual.
4. Backend consome a API do DocuSign: envia termo para assinatura e recebe callback de status (assinado/negado).

## Estrutura de pastas
A árvore completa de backend (FastAPI) e frontend (React) está em [arquitetura-projeto.md](../arquitetura-projeto.md).

## Módulos do sistema

1. **Autenticação e permissões** — múltiplos logins; perfis configurados pelo usuário Master
2. **Movimentações** — entrada e saída de itens de estoque
3. **Estoque atual** — somente notebook e teclado têm controle real de quantidade
4. **Licenças** — sub-licenças com capacidade fixa (ex: 10 vagas por sub-licença); é controle, não estoque
5. **Checklist de equipamentos** — por colaborador (Mouse, Mousepad, Teclado, Apoio de pulso, Suporte de notebook)
6. **Termos** — envio e assinatura via DocuSign
7. **Compras / Requisições** — acompanhamento de pedidos (OC) até a chegada
8. **Visão Geral (GLPI)** — tabela cruzada colaborador × licença × notebook × serial
9. **Inventário por colaborador e departamento** — lançamento manual do TI; cruzamento com estoque (notebook e teclado)
10. **Administração** — gestão de usuários e permissões (exclusivo do Master)

## Modelo de dados (tabelas principais)

| Tabela | Descrição |
|---|---|
| `usuarios` | Login do sistema, perfil, permissões |
| `colaboradores` | Sincronizado do GLPI: nome, e-mail, centro de custo |
| `centros_custo` | Administrativo, CCO Fiscal, Comercial, etc. |
| `itens_estoque` | Nome, quantidade, alerta mínimo (só notebook e teclado) |
| `movimentacoes` | Item, tipo (entrada/saída), quantidade, centro de custo, recebedor, status |
| `licencas_tipo` | Ex: Microsoft 365 Business Standard |
| `licencas_sublicenca` | Ex: standard01...standard18, capacidade = 10 |
| `licenca_vinculo` | colaborador_id + sublicenca_id |
| `equipamentos_entregues` | colaborador_id + flags por tipo de equipamento |
| `termos` | colaborador_id, tipo, status, id do envelope DocuSign, datas |
| `requisicoes_compra` | item, quantidade, fornecedor, status, previsão de chegada |
| `inventario_colaborador` | colaborador_id, notebook (serial), teclado (patrimônio), licença |

## Decisões em aberto que afetam a arquitetura
- Motor de banco de dados (ADR-002)
- Regra de aprovação da fila de "Pendentes" em Movimentações
- Detalhamento do fluxo DocuSign (tipos de termo, ordem de assinatura)
- Se a chegada de uma requisição de compra gera alta automática no estoque
