# CORE-1: State Manager Implementation

**Status:** InProgress
**Prioridade:** High
**Descrição:** Implementar a máquina de estados central do SmartLeather v1.

## Critérios de Aceite
- [ ] Implementar os estados: `FREE` (Livre), `PRODUCTION` (Produção), `DOWNTIME` (Parada).
- [ ] Garantir transições válidas:
  - `FREE` -> `PRODUCTION` (Abrir OP)
  - `PRODUCTION` -> `DOWNTIME` (Timeout ou Manual)
  - `DOWNTIME` -> `PRODUCTION` (Reiniciar OP)
  - `PRODUCTION` -> `FREE` (Finalizar OP)
- [ ] O sistema deve carregar o estado atual a partir do SQLite ao iniciar.
- [ ] Notificar a UI sobre mudanças de estado via Signals (PySide6).

## Notas Técnicas
- Utilizar `PySide6.QtCore.QObject` para emissão de sinais.
- Criar a classe em `src/core/state_manager.py`.

---
*Escrito pelo Scrum Master Agent (@River)*
