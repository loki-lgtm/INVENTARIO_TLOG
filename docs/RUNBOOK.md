# Runbook — Operação e Incidentes

> Este documento deve crescer conforme o sistema entrar em produção e novos incidentes forem identificados.

## Incidentes conhecidos (sistema anterior)

### 1. Conexão recusada ao acessar o sistema (Streamlit)
- **Sintoma:** `ERR_CONNECTION_REFUSED` ao acessar `10.0.100.7:8501`
- **Causa provável:** processo do Streamlit parado na VM (sem supervisor configurado para reiniciar automaticamente)
- **Ação tomada:** verificação manual do processo (`ps aux | grep streamlit`) e reinício manual
- **Lição para o novo sistema:** configurar um processo supervisionado (systemd, PM2 ou Docker com `restart: always`) desde o primeiro deploy, para evitar depender de reinício manual
