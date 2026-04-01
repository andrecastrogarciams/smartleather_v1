# UI-2: Login Screen

**Status:** Draft
**Prioridade:** Medium
**Descrição:** Implementar a interface inicial para autenticação de operadores.

## Critérios de Aceite
- [ ] Layout centralizado com inputs grandes ("Industrial Style" - `surface_container_high`).
- [ ] Campo de Matrícula (apenas números).
- [ ] Campo de Senha (ofuscado).
- [ ] Feedback visual de erro "Intervention State" (vermelho com glow, conforme doc).
- [ ] Teclado virtual on-screen acoplado aos inputs (se estiver em RPI touchscreen sem teclado físico).

## Notas Técnicas
- Integrar com `db.fetch_one` na tabela `users` (offline auth).
