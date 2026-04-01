# CORE-4: Manual Downtime & Pulse Buffer

**Status:** InProgress
**Prioridade:** High
**Descrição:** Implementar a gestão de paradas manuais e o armazenamento de pulsos recebidos durante este período em um buffer temporário.

## Critérios de Aceite
- [ ] Permitir iniciar parada manual com um `reason_id` obrigatório.
- [ ] Durante a parada manual, pulsos da GPIO **não** devem gerar `production_events` imediatos.
- [ ] Pulsos em parada manual devem ser salvos na tabela `downtime_buffer`.
- [ ] Implementar função para "Contabilizar Buffer" (mover do buffer para `production_events`).
- [ ] Implementar função para "Ignorar Buffer" (limpar a tabela de buffer do evento atual).
- [ ] Garantir que o timestamp original do pulso seja preservado se for contabilizado.

## Notas Técnicas
- Integrar no `DowntimeManager` (abertura/fechamento) e `ProductionManager` (captura para buffer).
- Tabela de destino: `downtime_buffer`.

---
*Escrito pelo Scrum Master Agent (@River)*
