# UI-4: Main Production Dashboard

**Status:** Draft
**Prioridade:** Highest
**Descrição:** A tela principal da operação onde o operador acompanha as métricas em tempo real e o estado da máquina.

## Critérios de Aceite
- [ ] Layout assimétrico conforme as imagens de layout (Sidebar escura à esquerda e painel de informações claro à direita).
- [ ] Indicador de Status da Máquina no topo (Verde/Azul para Produção, Vermelho/Amarelo para Parada).
- [ ] Card de Contagem de Peças (número gigante `display-lg`).
- [ ] Conectar os sinais do `StateManager` para atualizar os status visualmente em tempo real.
- [ ] Botão de "Registrar Parada" gigante na UI.

## Notas Técnicas
- Utilizar `QStackedWidget` no Main App para gerenciar as trocas de tela (Login -> Inicio OP -> Dashboard).
