# Módulo Estoque por Setor — Sistema de Gestão de TI (Tlog)

Segundo módulo com código de produção do projeto (depois do Checklist). Backend FastAPI + SQLAlchemy, frontend React. Construído em paralelo ao scaffold do frontend, a partir do protótipo visual do sistema.

## Como rodar

Ver [README.md](../README.md), seção "Como rodar" — os passos são os mesmos do projeto inteiro, esse módulo não tem setup próprio. Resumo:

```bash
cd backend
python -m app.seeds              # cria o catálogo de itens de estoque, entre outras coisas
uvicorn app.main:app --reload    # http://localhost:8000/docs

cd frontend
npm run dev                      # http://localhost:5173/estoque
```

## Endpoints

Referência completa com exemplos de request/response em [docs/API.md](API.md). Resumo:

| Método | Rota | Função |
|---|---|---|
| `GET` | `/api/estoque/itens` | Catálogo de tipos de equipamento ativos |
| `GET` | `/api/estoque/setores` | Total em estoque e total defeituoso por setor |
| `GET` | `/api/estoque/{centro_custo_id}` | Matriz item x estado de conservação de um setor |
| `PUT` | `/api/estoque/{centro_custo_id}/{item_estoque_id}/{estado}` | Grava a quantidade de um item — é o autosave da tela |

## Decisões tomadas neste módulo

**A unidade não é (setor, item) — é (setor, item, estado de conservação).** O pedido original era "cada setor tem seus equipamentos e como estão (novo, defeituoso)". Modelar como uma coluna de status no item de estoque forçaria escolher um único estado por combinação de setor e item, o que não reflete a realidade: o setor de TI pode ter, ao mesmo tempo, 10 mouses novos e 1 com defeito. Por isso `estoque_setor` tem uma `UniqueConstraint` em `(item_estoque_id, centro_custo_id, estado)` — três estados possíveis geram até três linhas para o mesmo par setor/item, cada uma com sua própria quantidade.

**Catálogo de item separado do saldo.** `ItemEstoque` é só o cadastro do tipo de equipamento (nome, categoria, alerta mínimo) — igual ao papel de `TipoPeriferico` no módulo de Checklist. `EstoqueSetor` é o saldo de fato. Separar os dois permite cadastrar um item novo sem precisar lançar saldo em nenhum setor, e permite que o alerta mínimo seja uma propriedade do item (independente de setor), não do saldo.

**A matriz é sempre completa, no mesmo espírito do Checklist.** `GET /api/estoque/{centro_custo_id}` devolve todo item ativo do catálogo com os três estados presentes, quantidade `0` quando não há lançamento — nunca falta uma chave. Setores sem nenhum lançamento aparecem em `GET /api/estoque/setores` com zeros, não desaparecem da lista.

**`estado` validado pelo tipo da rota, não por código de negócio.** O parâmetro de path é tipado como `Literal["novo", "usado", "defeituoso"]` na assinatura do endpoint — o FastAPI rejeita valores fora dessa lista com `422` antes de qualquer linha do `estoque_service.py` rodar. Evita duplicar a mesma validação em request e em banco.

**Catálogo inicial veio do protótipo de design do sistema, não de uma lista inventada.** Os 10 itens semeados em `app/seeds.py` (Mouse USB, Teclado ABNT2, Monitor 24 polegadas, Notebook Dell 14 polegadas, Headset USB, Cabo HDMI 1.8m, Mousepad, Suporte para notebook, Webcam Full HD, Estabilizador 300VA) e seus alertas mínimos vieram do mockup de tela de estoque desenhado antes deste módulo ser construído — é o dado mais próximo do que a operação real usa hoje.

**Autosave por célula, no blur, com desfazer em caso de erro.** Igual ao Checklist: o campo atualiza a tela na hora (otimista), salva quando o usuário sai do campo, e volta pro valor anterior se o `PUT` falhar — em vez de deixar a tela mentindo sobre um valor que não foi persistido.

## Pendências que este módulo deixa em aberto

- **Sem entrada inicial de saldo real.** O seed cria o catálogo de itens, mas nenhum saldo em `estoque_setor` — todo setor começa com tudo zerado. Alguém precisa lançar os valores reais manualmente pela tela (ou por um script de carga futuro) antes desta tela refletir o estoque físico de verdade.
- **Sem tela de cadastro de novos itens de catálogo.** `GET /api/estoque/itens` existe e está pronto, mas não há nenhuma tela ainda que crie um `ItemEstoque` novo — hoje isso só é possível direto pelo `/docs` do backend ou no banco.
- **Requisição de compra concluída não gera entrada automática de estoque.** Quando o módulo de Compras existir, decidir se a chegada de um pedido cria linhas em `estoque_setor` automaticamente (e em qual estado — presumivelmente "novo") ou se continua manual.
- **Sem histórico de movimentação de saldo.** `atualizar_saldo()` sobrescreve a quantidade da célula — não fica registro de "quem mudou de 10 para 12 e quando", diferente do Checklist, que guarda `marcado_por` e `data_entrega` por marcação. Se auditoria de estoque for necessária, esse é o primeiro ponto a revisar.
- **Alerta mínimo é do item, não por setor.** Hoje um setor pequeno e um grande usam o mesmo `alerta_minimo` de um item (é uma propriedade do catálogo). Se setores precisarem de limites diferentes, `alerta_minimo` precisa migrar para `estoque_setor` ou ganhar uma tabela de override por setor.
