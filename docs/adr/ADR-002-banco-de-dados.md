# ADR-002: Escolha do banco de dados

## Status
**Em aberto** (pendente de decisão)

## Contexto
O sistema anterior usava SQLite (`inventario_ti.db`) com um único usuário de acesso. O novo sistema terá múltiplos logins simultâneos (cada pessoa da equipe com o próprio usuário), o que aumenta a necessidade de suportar acesso concorrente de escrita.

## Opções em avaliação
- **SQLite:** simples, zero configuração, mas com limitações de concorrência em escrita simultânea.
- **PostgreSQL / MySQL:** mais robusto para múltiplos acessos simultâneos, mas exige um servidor de banco rodando na VM.

## Decisão
Ainda não definida.

## Consequências (a depender da escolha)
Impacta diretamente a camada `app/db/database.py` do backend e a estratégia de migrações (ex: Alembic, caso a escolha seja PostgreSQL/MySQL).
