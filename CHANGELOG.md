# Changelog

## [Não lançado]

### Em andamento
- Levantamento de requisitos funcionais concluído para os módulos: Movimentações, Estoque, Licenças, Checklist de Equipamentos, Termos, Compras, Visão Geral (GLPI) e Inventário por colaborador/departamento.
- Estrutura de pastas definida para backend (FastAPI) e frontend (React).
- Diagrama de casos de uso e diagrama de componentes gerados durante o levantamento de requisitos.
- ADR-001 registrada: escolha de stack (React + Python/FastAPI).
- ADR-002 criada e marcada como pendente: escolha do banco de dados.

### Pendente
- Definição do banco de dados (ver ADR-002).
- Regra de aprovação da fila de "Pendentes" em Movimentações.
- Detalhamento do fluxo DocuSign (tipos de termo, ordem de assinatura, tratamento de status).
- Regra de entrada automática no estoque a partir de requisições de compra concluídas.
- Pipeline de CI/CD e estratégia de deploy.
- Implementação do código-fonte (nenhuma linha escrita ainda).
