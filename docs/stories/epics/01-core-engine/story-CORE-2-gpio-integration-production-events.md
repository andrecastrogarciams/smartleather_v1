# CORE-2: GPIO Integration with Production Events

**Status:** InProgress
**Prioridade:** High
**Descrição:** Garantir que cada pulso da GPIO seja persistido no SQLite como um evento de produção.

## Critérios de Aceite
- [ ] Cada pulso recebido deve gerar um `production_event` com UUID v4.
- [ ] O timestamp deve ser capturado no momento exato do disparo (Python `datetime`).
- [ ] O evento deve ser vinculado à OP e ao Turno ativos.
- [ ] O banco de dados deve ser consultado em uma Thread separada para não travar a recepção de pulsos.

## Notas Técnicas
- Utilizar `src/database/db_manager.py` para persistência.
- Integrar com `src/hardware/gpio_manager.py`.

---
*Escrito pelo Scrum Master Agent (@River)*
