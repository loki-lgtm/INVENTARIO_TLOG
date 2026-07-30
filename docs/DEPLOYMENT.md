# Deploy

## Status atual
**Pendente.** Ainda não há pipeline de CI/CD definido, nem estratégia de deploy (Blue-Green, Canary, Rolling).

## Infraestrutura conhecida
- O sistema anterior (Streamlit) rodava em um servidor interno da rede da empresa (ex: `10.0.100.7`, porta 8501), acessível apenas dentro da rede local — sem processo supervisionado (systemd/PM2/Docker), o que foi a causa raiz do incidente que motivou esta reconstrução.
- Ainda não foi confirmado se o novo sistema continua em infraestrutura interna (VM própria) ou migra para nuvem.

## O que precisa ser decidido antes de preencher este documento
- Onde backend e frontend vão rodar (mesma VM? processos separados via Nginx/reverse proxy?)
- Se haverá pipeline de CI (ex: GitHub Actions) ou deploy manual
- Processo supervisionado para reiniciar os serviços automaticamente em caso de queda
- Estratégia de rollback
