# Epic 01: Core Engine & State Management

**Status:** InProgress
**Descrição:** Implementação do núcleo operacional do SmartLeather, incluindo a máquina de estados, lógica de captura de pulsos e gestão de paradas.

## Backlog das Histórias

| ID | Story | Status | Descrição |
| :--- | :--- | :--- | :--- |
| CORE-1 | [State Manager Implementation](story-CORE-1-state-manager-implementation.md) | InProgress | Implementar a máquina de estados (Livre, Produção, Parada). |
| CORE-2 | [GPIO Integration with Production Events](story-CORE-2-gpio-integration-production-events.md) | InProgress | Vincular pulsos da GPIO ao registro de eventos no SQLite. |
| CORE-3 | [Automatic Downtime Logic (Timeout)](story-CORE-3-automatic-downtime-timeout.md) | Draft | Implementar o disparo automático de parada por inatividade. |
| CORE-4 | [Manual Downtime & Pulse Buffer](story-CORE-4-manual-downtime-pulse-buffer.md) | Draft | Gerenciar paradas manuais e bufferizar pulsos recebidos durante a parada. |
| CORE-5 | [OP Contingency Flow](story-CORE-5-op-contingency-flow.md) | Draft | Fluxo de abertura manual de OP quando a API estiver offline. |

---
*Gerenciado pelo Scrum Master Agent (@River)*
