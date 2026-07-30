# ADR-001: Escolha da stack tecnológica (Frontend/Backend)

## Status
Aceita

## Contexto
O sistema anterior era construído inteiramente em Python com Streamlit, o que limitava a personalização visual, a responsividade e a experiência de uso. A equipe decidiu redesenhar as telas do zero e reconstruir o backend, mantendo as integrações externas já existentes (GLPI) e adicionando uma nova (DocuSign).

## Decisão
- **Frontend:** React (JavaScript)
- **Backend:** Python com FastAPI

## Justificativa
- Python foi mantido no backend por permitir reaproveitar lógica já validada de integração com a API do GLPI, e por ter SDK oficial para DocuSign.
- FastAPI foi escolhido em vez de Flask ou Django por: gerar documentação automática (Swagger/OpenAPI), suportar chamadas assíncronas (relevante porque o backend depende de respostas de APIs externas como GLPI e DocuSign) e ser mais leve que Django, já que o frontend é desacoplado em React (não precisa de admin nem ORM embutido do Django).
- React foi escolhido para o frontend por dar controle total sobre design e responsividade — a principal limitação do sistema anterior.

## Consequências
- Frontend e backend passam a ser dois serviços separados rodando de forma independente (diferente do Streamlit, que era um único processo monolítico) — exige orquestrar o deploy dos dois.
- É necessário definir a estratégia de autenticação entre frontend e backend (sessão ou token).
- Ganho de flexibilidade visual, de manutenção e de possibilidade de evoluir os dois lados de forma independente.
