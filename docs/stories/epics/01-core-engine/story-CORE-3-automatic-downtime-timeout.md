# CORE-3: Automatic Downtime Logic (Timeout)

**Status:** InProgress
**Prioridade:** High
**Descrição:** Implementar o disparo automático de parada por inatividade quando não houver pulsos por um tempo configurado.

## Critérios de Aceite
- [ ] Monitorar o intervalo entre pulsos de produção.
- [ ] Se o tempo exceder `DOWNTIME_TIMEOUT` (do .env), alterar estado para `DOWNTIME`.
- [ ] Registrar o evento de parada no SQLite com o motivo "Parada Automática".
- [ ] Reiniciar o timer em cada pulso recebido.
- [ ] Parar o monitoramento se a linha for finalizada (`FREE`).

## Notas Técnicas
- Utilizar `PySide6.QtCore.QTimer`.
- Criar em `src/core/downtime_manager.py`.

---
*Escrito pelo Scrum Master Agent (@River)*
