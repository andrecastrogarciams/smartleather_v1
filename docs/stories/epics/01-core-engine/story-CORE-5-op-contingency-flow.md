# CORE-5: OP Contingency Flow

**Status:** InProgress
**Prioridade:** Medium
**Descrição:** Implementar a capacidade de abrir uma Ordem de Produção manualmente quando a API estiver indisponível (Contingência).

## Critérios de Aceite
- [ ] Implementar método para abrir OP em contingência (`is_contingency = True`).
- [ ] Permitir que a produção inicie normalmente com uma OP de contingência.
- [ ] Salvar os dados mínimos obrigatórios (número da OP).
- [ ] Marcar o registro para futura sincronização/enriquecimento pela API.

## Notas Técnicas
- Alterar `src/core/state_manager.py` para aceitar abertura manual.
- Integrar no `db_manager` a inserção de OPs locais.

---
*Escrito pelo Scrum Master Agent (@River)*
