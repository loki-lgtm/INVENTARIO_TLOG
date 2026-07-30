# Sistema de Gestão de TI (v2)

## Overview
Sistema web interno para centralizar a gestão de infraestrutura de TI: controle de estoque de equipamentos, controle de equipamentos, checklist de entrega de equipamentos por colaborador, termos de responsabilidade (via DocuSign), marcacao de requisições de compra e inventário por colaborador/departamento com datas de entrega — com integração direta à API do GLPI.
Emissão de relatorios e verificação e cobrança de equipamentos.

Este projeto é a reconstrução do sistema anterior (feito em Python/Streamlit). O objetivo é ter controle total sobre design, responsividade e arquitetura, mantendo as integrações já existentes e adicionando novas.

## Status do projeto
🚧 **Fase atual: levantamento de requisitos e definição de arquitetura.** Nenhuma linha de código de produção foi escrita ainda — este repositório está sendo preparado antes do início do desenvolvimento.

## Quick Start
> Pendente.  setup inicial do backend e do frontend estiver criado (comandos de instalação e execução local).

## Arquitetura
Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para o desenho de componentes, módulos e modelo de dados.

## Deploy
Ver [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — pipeline de CI/CD ainda não definido.

## Troubleshooting
> Pendente. Será alimentado conforme problemas reais de produção forem identificados. Ver [docs/RUNBOOK.md](docs/RUNBOOK.md) para o único incidente já registrado (sistema anterior).

## Documentação relacionada
- [Requisitos funcionais completos](requisitos-sistema-gestao-ti.md)
- [Árvore de pastas — backend e frontend](arquitetura-projeto.md)
- [Decisões técnicas (ADR)](docs/adr/)
- [Changelog](CHANGELOG.md)
