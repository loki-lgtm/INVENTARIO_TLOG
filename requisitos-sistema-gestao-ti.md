# Documento de Requisitos — Sistema de Gestão de TI (v2)

> Documento base para levantamento de requisitos, modelagem e reconstrução do sistema atualmente feito em Streamlit. Use este conteúdo como prompt em ferramentas de design (Figma AI, v0, Claude Design, etc.) ou como ponto de partida para o Product Backlog.

---

## 1. Contexto e Objetivo

Sistema web interno para centralizar a gestão de infraestrutura de TI de uma empresa, cobrindo:
- Controle de estoque de equipamentos (entradas e saídas)
- Controle de licenças de software
- Integração com o GLPI (sistema de inventário/help desk) via API, para sincronizar colaboradores e notebooks

**Motivo da reconstrução:** o sistema atual (Streamlit) é funcional, mas limitado em termos de personalização visual, responsividade e experiência de uso. O objetivo é redesenhar as telas do zero, mantendo (e evoluindo) as funcionalidades existentes.

**Stack observada em andamento:** migração para Next.js/React (deploy identificado na Vercel), com um protótipo de checklist já rodando localmente (localhost:3000).

---

## 2. Atores do Sistema

| Ator | Descrição | Permissões esperadas |
|---|---|---|
| **Suporte de TI** | Usuário operacional do dia a dia | Cadastrar itens, registrar retiradas, gerenciar licenças, importar dados do GLPI |
| **Administrador** | Responsável pela gestão do setor | Tudo que o Suporte faz + gestão de usuários/senhas + exclusão permanente de itens |
| *(Opcional a definir)* **Gestor/Consulta** | Perfil somente leitura | Visualizar estoque, licenças e visão geral, sem editar |

---

## 3. Módulos e Funcionalidades

### 3.1 Autenticação
- Login com usuário e senha
- Sessão protegida (rotas internas não acessíveis sem login)
- (Sugestão de melhoria) recuperação de senha e níveis de permissão por perfil

### 3.2  Movimentações (Entradas e Saídas)
**Cadastro de Itens (Entrada)**
- Campos: Nome do item, Quantidade, Alerta mínimo
- Ação: "Salvar Entrada"

**Registrar Retirada (Saída)**
- Campos: Item (seleção dos itens cadastrados), Quantidade, Centro de Custo, Recebedor
- Ação: "Baixa" — envia o item para uma fila de pendentes

**Pendentes**
- Lista de baixas aguardando confirmação/aprovação (fluxo a ser detalhado: quem aprova? existe prazo?)

### 3.3  Estoque Atual
- Tabela em tempo real: Item, Quantidade, Alerta mínimo
- Alerta visual (ex: cor vermelha) quando quantidade está abaixo do mínimo definido
- Exclusão permanente de item do sistema (seleção + botão "Remover do Sistema")

### 3.4  Licenças
- Cadastro de capacidade de licenças (quantidade de licenças disponíveis por software)
- Vínculo de licença com usuário do GLPI
- Gerenciamento de remoções (desvincular licença de um colaborador)

### 3.5  Visão Geral (GLPI)
- Tabela cruzada com: Colaborador, E-mail, Licença vinculada, Notebook, Serial Number
- Contador de total de registros
- Campo de busca (pesquisa em qualquer campo da tabela)
- Botão "Sincronizar Agora" (atualização manual sob demanda)

### 3.6  Importar GLPI
- Robô de varredura que consome a API do GLPI
- Botão "Iniciar Importação Completa"
- Feed de status/progresso da importação (ex: "Varrendo inventário do GLPI...")
- Atualiza a base local com e-mails, inventário de máquinas e faz o cruzamento de dados

### 3.7 (Novo, visto no protótipo) Checklist de Equipamentos por Funcionário
- Lista de colaboradores (Nome, E-mail) com checkboxes por tipo de equipamento: Mouse, Mousepad, Teclado, Apoio de pulso, Suporte de notebook
- Busca por nome ou e-mail
- Indicador de progresso ("X de Y completos")
- Marcação salva automaticamente

---

## 4. Integrações Externas

**API do GLPI**
- URL configurável (`GLPI_URL`)
- Autenticação via `USER_TOKEN` + `APP_TOKEN`
- Operações: consulta de usuários, consulta de inventário de máquinas, cruzamento de dados

**Banco de Dados**
- Atualmente SQLite (`inventario_ti.db`) — avaliar se mantém SQLite ou migra para um banco mais robusto (Postgres/MySQL) dependendo do volume e de necessidade de acesso concorrente

---

## 5. Requisitos Não-Funcionais

- **Segurança:** nenhuma credencial/token em código-fonte; uso de variáveis de ambiente/secrets
- **Responsividade:** telas devem funcionar bem em desktop (uso interno principal) e idealmente em tablet
- **Performance:** sincronização com GLPI não deve travar a interface (considerar loading assíncrono/feedback visual)
- **Auditoria (sugestão):** registrar quem fez cada movimentação e quando (log de ações)
- **Backup (sugestão):** rotina de backup do banco de dados

---

## 6. Pontos em Aberto (para decidir no levantamento)

- [ ] Existem múltiplos perfis de acesso ou só usuário único "suporte"?
- [ ] Fluxo de aprovação da fila de "Pendentes" — existe uma etapa de aprovação ou é só um histórico?
- [ ] Notificações (e-mail/Slack) quando estoque atinge o mínimo?
- [ ] Histórico de movimentações (relatório por período, por centro de custo)?
- [ ] O checklist de equipamentos (visto no protótipo) é um módulo novo dentro do mesmo sistema ou um app separado?
- [ ] Qual banco de dados final (mantém SQLite ou migra)?

---

## 7. Sugestão de Épicos para o Backlog (Scrum)

1. **Épico — Autenticação e Perfis**
2. **Épico — Gestão de Estoque** (Movimentações + Estoque Atual)
3. **Épico — Gestão de Licenças**
4. **Épico — Integração GLPI** (Importação + Visão Geral)
5. **Épico — Checklist de Equipamentos**
6. **Épico — Relatórios e Auditoria** (se aprovado como necessidade)

Cada épico pode virar um conjunto de User Stories no formato:
> Como [ator], quero [ação], para [benefício/motivo].



