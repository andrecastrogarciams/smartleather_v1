# UI-1: Base Theme & Components

**Status:** Ready
**Prioridade:** High
**Descrição:** Traduzir as regras do "Organic Brutalism" (do `DESIGN.md`) para um arquivo QSS global no PySide6 e criar os widgets base customizados para reuso.

## Critérios de Aceite
- [ ] Criar arquivo `src/ui/assets/style.qss` definindo a paleta de cores (Blue `#002a4d`, backgrounds `#f4faff`, etc.).
- [ ] Aplicar "No-Line Rule": usar variações de background em vez de bordas sólidas.
- [ ] Criar classe `PrimaryButton` herdando de `QPushButton` com padding amplo e estado de focus tátil.
- [ ] Criar classe `ProductionCard` (Widget) baseada na regra de "Layering Principle".
- [ ] Configurar a fonte global "Inter" no aplicativo, garantindo tamanhos grandes (`body-lg`, `display-lg`).

## Notas Técnicas
- Carregar o `.qss` no `src/main.py`.
- Evitar sombras nativas difíceis do Qt; se necessário, usar simulação via `QGraphicsDropShadowEffect` bem sutil.

---
*Escrito pelo Scrum Master Agent (@River)*
