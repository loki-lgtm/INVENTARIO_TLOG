# ADR-002: Escolha do banco de dados

## Status
Aceita (parcial — motor de produção decidido; migrações ainda em aberto)

## Contexto
O sistema anterior usava SQLite (`inventario_ti.db`) com um único usuário de acesso. O novo sistema terá múltiplos logins simultâneos (cada pessoa da equipe com o próprio usuário), o que aumenta a necessidade de suportar acesso concorrente de escrita.

## Opções avaliadas
- **SQLite:** simples, zero configuração, mas com limitações de concorrência em escrita simultânea.
- **PostgreSQL / MySQL:** mais robusto para múltiplos acessos simultâneos, mas exige um servidor de banco rodando na VM.

## Decisão
Os dois motores convivem, para propósitos diferentes:
- **SQLite** é o padrão em desenvolvimento local (`sqlite:///./app.db`, sem nenhuma configuração — é o valor default em `app/core/config.py`) e o único motor usado pelos testes automatizados (SQLite em memória, ver `backend/tests/`).
- **PostgreSQL** é o motor para um ambiente compartilhado/produção, subido localmente via `docker-compose.yml` (serviço `db`) e configurado trocando `DATABASE_URL` em `backend/.env` (modelo em `backend/.env.example`).

A camada `app/db/database.py` lê `DATABASE_URL` das configurações e não faz nenhuma suposição sobre o motor — a troca é só de connection string, sem mudança de código, porque o projeto usa SQLAlchemy Core/ORM sem funcionalidades específicas de um banco.

## O que ainda não foi validado
O caminho do PostgreSQL/docker-compose foi escrito mas ainda não foi exercitado de fato (nem em teste automatizado, nem manualmente) — só o SQLite foi testado até agora. Antes de depender do Postgres em qualquer ambiente compartilhado, validar a conexão e rodar `python -m app.seeds` contra ele.

## Consequências
- Migrações (Alembic) ainda não existem. Hoje, qualquer mudança de modelo exige recriar o banco (`Base.metadata.create_all` roda só dentro de `app/seeds.py`, chamado manualmente) — aceitável enquanto o schema muda rápido e não há dado real em produção, mas precisa ser resolvido antes de um primeiro deploy real.
- `psycopg2-binary` foi adicionado a `requirements.txt` como driver do Postgres, mesmo o SQLite sendo o caminho testado — para não bloquear quem for validar o Postgres primeiro.
