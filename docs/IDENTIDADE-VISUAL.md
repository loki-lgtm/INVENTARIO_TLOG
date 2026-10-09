# Identidade Visual — Grupo TLOG

Registro da identidade visual oficial recebida do cliente e de como ela foi aplicada no frontend. Serve de referência pra quem for criar uma tela nova e precisar saber quais tokens usar — e também documenta o que ainda está em aberto (a cor de destaque, principalmente), porque não foi uma decisão tomada aqui, foi uma lacuna herdada do material recebido.

## Origem

O cliente enviou um guia de marca (`TLOG Logo.html`, não versionado neste repositório — é material de referência, não código do produto) com o wordmark oficial (arquivo `tlog-logo-original.png`, também não incluído aqui) e um símbolo criado para o sistema: um "T" cuja barra superior termina em seta (representa a rota) e tem um ponto na base (representa a carga rastreada). O guia registra explicitamente: *"O logo enviado é só preto e branco... Se a TLOG tiver uma cor oficial, me passe o hex que eu troco."* — ou seja, a ausência de uma cor de destaque cromática é deliberada até segunda ordem, não um esquecimento.

Consultei também o site público (`grupotlog.com.br`) para confirmar o tom: identidade corporativa/industrial, predominantemente preto e branco, tipografia sem serifa, tagline *"Logística Personalizada para o Seu Negócio"*. Nada ali contradiz o guia de marca — reforça a leitura monocromática.

## Tokens

Definidos em `frontend/src/styles/brand.css`, carregados globalmente (importado em `main.jsx`), como propriedades customizadas em `:root`:

| Token | Valor | Uso |
|---|---|---|
| `--tlog-bg` | `#0a0a0b` | Fundo de superfícies escuras (Sidebar, painel de identidade do Login) |
| `--tlog-surface` / `--tlog-surface-2` | `#121214` / `#18181b` | Camadas sobre o fundo escuro (hover, cartões) |
| `--tlog-border` / `--tlog-border-2` | `#232326` / `#2e2e33` | Bordas e divisores, escuro e claro |
| `--tlog-text` | `#f4f4f5` | Texto sobre fundo escuro |
| `--tlog-dim` | `#a1a1aa` | Texto secundário sobre fundo escuro |
| `--tlog-faint` | `#6b6b74` | Texto terciário / legendas |
| `--tlog-accent` / `--tlog-accent-2` | `#b4b4bb` / `#8a8a93` | Prata — o único "destaque" que o material de marca define |
| `--tlog-ink` | `#0a0a0b` | Texto/ícone sobre fundo claro, botões primários em telas claras |
| `--tlog-paper` | `#f4f4f2` | Fundo de superfícies claras dentro de uma tela de marca (ex: painel de formulário do Login) |
| `--tlog-font` | `"Fira Sans", ...` | Tipografia de toda a aplicação |
| `--tlog-mono` | `"JetBrains Mono", ...` | Elementos curtos tipo etiqueta (iniciais de avatar, badge de menu) |

As fontes são carregadas via Google Fonts em `frontend/index.html` (pesos 300–800 da Fira Sans, 400–500 da JetBrains Mono).

## O símbolo

Implementado como componente React em `frontend/src/components/brand/TlogMark.jsx` (usa `useId()` pra não colidir o gradiente SVG quando repetido na mesma página) e, como arquivo estático equivalente, em `frontend/public/favicon.svg`. Os dois precisam continuar batendo visualmente — se o traço do símbolo mudar em um, replicar no outro.

## Onde foi aplicado, e onde não foi

A marca foi aplicada por inteiro no que chamo de "shell" da aplicação — as telas que são a cara do produto, não o conteúdo de trabalho:

- **Sidebar** (`components/layout/Sidebar.jsx`/`.css`) — paleta, símbolo e wordmark trocados; estrutura e comportamento (recolher, grupos expansíveis, item ativo) intactos.
- **Login** (`pages/Login/`) — redesenhado como dois painéis: identidade à esquerda (fundo escuro, símbolo + wordmark "GRUPO/TLOG", tagline), formulário à direita (fundo claro, mesma lógica de abas e estado que já existia — nenhuma mudança de comportamento, só de layout).
- **Dashboard** (`pages/Dashboard/`) — título trocado para "Grupo TLOG", símbolo adicionado ao cabeçalho, cor de destaque (hover dos cartões, foco) trocada de `--petroleo` (verde-azulado, não é da marca) para `--tlog-ink`.
- **PlaceholderPage** — só tokens de cor e fonte trocados, sem mudança de estrutura.
- **index.html** — título da aba, favicon e fontes.

**Checklist e Estoque por Setor foram deixados como estavam** — continuam com a paleta "petroleo" própria deles (`--petroleo: #0f6e63`) e o mesmo layout de grade densa, validado com quem usa a tela todo dia. A única mudança nesses dois é a fonte (`font-family` passou a herdar `--tlog-font`, que já é carregada globalmente pelo Sidebar — não soma custo de rede). A decisão foi deliberada: são telas de trabalho repetitivo, não vitrine da marca, e recolorir uma grade já testada é risco sem necessidade clara.

## Em aberto

- **Cor de destaque cromática.** Hoje é tudo prata/grafite. Se o cliente confirmar uma cor oficial (ver a ressalva do próprio guia de marca), ela entra como `--tlog-accent` e provavelmente substitui o uso pontual de `--tlog-ink` em botões primários — não deve virar a cor de fundo de nada, pelo tom monocromático do restante da marca.
- **Wordmark oficial (arquivo vetorial).** O guia de marca usa uma recriação em Fira Sans do "GRUPO/TLOG"; se o vetor oficial (SVG/AI) for enviado, ele pode substituir o texto estilizado em `Login.jsx` e no `sb-marca-texto` do Sidebar sem mudar a estrutura dos componentes.
- **Aplicar a marca nas telas ainda não construídas** (Movimentação, Compras, Termos, Relatórios, Integrações, Configurações) — hoje `PlaceholderPage` já herda os tokens certos, então qualquer tela nova nasce alinhada à marca se usar `var(--tlog-*)` em vez de cor fixa.
