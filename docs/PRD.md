# PRD — SmartLeather v1

## 1. Visão Geral

### 1.1 Contexto e problema

O SmartLeather v1 é uma aplicação local para Raspberry Pi voltada ao controle de produção em setores industriais. O sistema deve permitir consultar uma Ordem de Produção (OP) em uma base externa via API, iniciar a produção por linha, contabilizar itens produzidos por sinal digital via GPIO, registrar paradas manuais e automáticas, operar offline por tempo indefinido e sincronizar os dados com um MySQL central assim que a conectividade for restabelecida. O foco da v1 é garantir captura confiável de eventos, alta disponibilidade local e perda zero de produção.

### 1.2 Solução proposta

A solução será composta por:

- Aplicação local no Raspberry Pi, desenvolvida em Python + PySide6, em tela cheia, com autostart no boot e reinício automático em caso de falha.
- Banco local SQLite, responsável por garantir operação offline, persistência transacional dos eventos e sincronização posterior.
- Integração com API de OP, usando chave por dispositivo.
- Sincronização em tempo real ao reconectar com um MySQL central on-premise.
- Configuração local por arquivo, definindo o setor e a linha atendidos por cada RPI.

### 1.3 Stakeholders principais

- Operadores de produção
- Responsáveis/Supervisores
- Administradores do sistema
- Equipe de TI / manutenção
- Gestores industriais
- Aplicação futura de dashboard/OEE, que consumirá os dados capturados pelo SmartLeather v1

## 2. Objetivos de Negócio

### 2.1 Objetivos principais
- Garantir registro confiável de produção e paradas por linha.
- Permitir operação offline-first, sem dependência contínua de rede.
- Eliminar perda de apontamentos em falhas de conectividade.
- Criar base de dados estruturada para cálculo posterior de disponibilidade e performance.
- Padronizar o fluxo operacional de abertura, execução, parada e encerramento de OP.

### 2.2 Metas da v1
- Operar sem internet/rede por tempo indefinido.
- Aceitar perda zero de produção no app local.
- Sincronizar automaticamente com o banco central assim que reconectar.
- Permitir controle inicial em aproximadamente 8 a 10 setores, com alguns chegando a 5 linhas.

### 2.3 Fora de escopo da v1
- Cálculo final de OEE e dashboards.
- Gestão central avançada dos RPIs.
- Política de limpeza e retenção no banco central.
- Auditoria central detalhada.
- Backup/restore avançado e disaster recovery central.

## 3. Público-Alvo e Perfis

### 3.1 Operador
**Permissões:**
- login com matrícula e senha;
- iniciar OP;
- apontar produção;
- registrar parada manual;
- encerrar/parar OP;
- solicitar finalização de OP.

### 3.2 Responsável / Supervisor
**Permissões:**
- confirmar a finalização de uma OP com matrícula e senha na mesma tela da operação.

### 3.3 Administrador
**Permissões:**
- configurar usuários;
- configurar tempos e parâmetros;
- configurar motivos e opções locais;
- testar conectividade/sincronização;
- administrar parâmetros do posto.

## 4. User Stories

### 4.1 Operação
- Como operador, quero buscar uma OP via API para iniciar a produção da minha linha.
- Como operador, quero conseguir informar uma OP manualmente em contingência quando a API estiver indisponível.
- Como operador, quero registrar produção por pulso digital para contabilizar os itens produzidos.
- Como operador, quero registrar paradas manuais com motivo obrigatório.
- Como operador, quero ser avisado quando houver pulsos recebidos durante uma parada manual, para decidir se devo contabilizar ou ignorar.
- Como operador, quero continuar usando o sistema mesmo sem rede.
- Como operador, quero encerrar a OP e deixá-la pendente da confirmação do responsável.

### 4.2 Supervisão
- Como responsável, quero confirmar a finalização de uma OP com minha matrícula e senha.
- Como responsável, quero impedir que a linha continue apontando enquanto a OP estiver pendente de confirmação.

### 4.3 Administração
- Como administrador, quero configurar timeout de parada automática.
- Como administrador, quero configurar o posto local e validar conectividade.
- Como administrador, quero manter usuários e permissões sincronizados localmente para operação offline.

## 5. Funcionalidades Core

### 5.1 Login e sessão
- Login por matrícula + senha.
- Sessão permanece ativa até logout.
- Autenticação deve funcionar offline com cópia local de credenciais e permissões.

### 5.2 Configuração do posto
- Cada RPI terá arquivo de configuração local com:
    - identificação do dispositivo;
    - setor;
    - linha;
    - parâmetros do posto.
- Ao abrir, o app já inicia associado ao setor e linha corretos.

### 5.3 Consulta e abertura de OP
- Consulta de OP por API.
- Dados retornados pela API:
    - número da OP;
    - código e descrição do produto;
    - código e descrição da derivação;
    - quantidade prevista.
- Em contingência, permitir digitação manual do número da OP e observação opcional.
- Quando a API voltar, a OP digitada manualmente deve ser validada/enriquecida automaticamente.

### 5.4 Controle por linha
- Em setores com múltiplas linhas, pode existir 1 OP ativa por linha.
- O controle operacional de produção e paradas é por:
    - setor;
    - linha;
    - turno.

### 5.5 Apontamento de produção
- Entrada de pulso via GPIO.
- Regra fixa: 1 pulso = 1 item produzido.
- O pulso pode vir de:
    - sensor;
    - botão;
    - CLP;
    - botoeira instalada no posto.
- Cada pulso deve ser registrado como evento individual com timestamp próprio.

### 5.6 Parada automática
- Se a OP estiver em produção e não houver pulso por tempo mínimo configurado, o app abre uma parada automática com motivo padrão “parada por tempo excedido”.
- A parada automática é encerrada:
    - ao receber novo pulso; ou
    - quando o operador encerrar a parada.
- Ao receber novo pulso após parada automática, o item deve voltar ao fluxo normal de produção.

### 5.7 Parada manual
- Motivo obrigatório.
- Encerramento sempre manual.
- Se houver pulso durante parada manual:
    - o pulso não entra automaticamente na produção;
    - os eventos ficam em buffer;
    - o operador é notificado com a mensagem:
      “Foi recebido X itens durante a Parada, contabilizar ou ignorar?”
    - caso escolha contabilizar, os eventos mantêm o timestamp original.

### 5.8 Troca de turno
- O turno é definido automaticamente por faixas de horário configuradas.
- Em troca de turno:
    - o operador atual pausa a operação com motivo próprio para troca de turno;
    - o operador seguinte, ao logar, é notificado da OP em aberto;
    - o operador seguinte deve continuar a OP em aberto.

### 5.9 Encerramento de OP
- O operador solicita o encerramento.
- A OP passa para status pendente de confirmação.
- Um responsável/supervisor deve confirmar com matrícula e senha na mesma tela.
- Enquanto estiver pendente de confirmação:
    - não pode haver novos apontamentos;
    - não pode iniciar outra OP na linha.

### 5.10 Monitoramento local/central
O sistema central deverá conseguir visualizar, no mínimo:
- status online/offline do RPI;
- última sincronização;
- fila pendente de eventos.

## 6. Estados e Regras de Negócio

### 6.1 Estados da linha
- Livre
- Em produção
- Parada

### 6.2 Estados da OP
- Livre
- Em produção
- Pendente de confirmação
- Finalizada

### 6.3 Regras críticas
- Uma linha não pode ter mais de uma OP ativa simultaneamente.
- Cada pulso válido representa exatamente um item.
- Em modo offline, o sistema deve continuar funcionando integralmente com base local.
- Eventos devem ser idempotentes para impedir duplicidade no banco central.
- Eventos sincronizados permanecem no SQLite local por 15 dias.

## 7. Integrações

### 7.1 API de Ordens de Produção
A API será desenvolvida separadamente e deverá:
- autenticar por chave por dispositivo;
- consultar dados da OP;
- retornar os dados mínimos operacionais descritos.

### 7.2 Banco central
- MySQL central on-premise.
- Recebe produção, paradas, dados consolidados e cadastros sincronizados.

### 7.3 Banco local
- SQLite por dispositivo.
- Responsável por persistência local, fila de sincronização, dados operacionais e autenticação offline.

### 7.4 Cadastros sincronizados do central para o RPI
- usuários;
- linhas;
- setores;
- motivos de parada;
- parâmetros de timeout;
- OPs previamente carregadas, quando aplicável.

## 8. Requisitos Não Funcionais

### 8.1 Disponibilidade e confiabilidade
- Operação local deve funcionar sem rede por tempo indefinido.
- A perda aceitável de produção é zero no contexto da aplicação local.
- O app deve abrir automaticamente no boot.
- Em falha do processo, deve haver reinício automático.

### 8.2 Persistência e consistência
- Todo pulso deve gerar evento persistido localmente.
- A sincronização deve ocorrer assim que reconectar.
- Deve haver mecanismo de idempotência para evitar duplicação por retry.
- Eventos sincronizados permanecem localmente por 15 dias configurados.

### 8.3 Performance
Como requisito inicial:
- o app deve suportar eventos com frequência equivalente a acionamentos humanos em pushbutton;
- o fluxo de captura não pode bloquear a UI;
- leitura de GPIO, persistência local e sincronização devem ser desacopladas logicamente.

**Observação:** métricas p50/p95/p99 ainda não foram definidas para a v1.

### 8.4 Segurança
- autenticação por matrícula e senha;
- perfis de acesso por papel;
- autenticação offline com cópia local de permissões;
- autenticação da API por chave por dispositivo.

**Observação:** política de criptografia, rotação de secrets e hardening detalhado ficam para evolução posterior.

### 8.5 Observabilidade mínima da v1
Mesmo fora do escopo de auditoria central, a v1 deve ter o mínimo operacional local:
- logs locais de erro da aplicação;
- logs de falha de sincronização;
- registro local de conectividade;
- indicador visual de status de rede/sincronização na tela principal.

*Isso é uma recomendação de implementação para sustentação da v1.*

## 9. Arquitetura da Solução

### 9.1 Padrão arquitetural
Arquitetura edge/offline-first, com processamento local e sincronização posterior para o central.

### 9.2 Stack
- Aplicação local: Python + PySide6
- Banco local: SQLite
- Banco central: MySQL
- Integração externa: API de OP
- Hardware: Raspberry Pi + GPIO

### 9.3 Componentes lógicos
- módulo de autenticação local;
- módulo de configuração do posto;
- módulo de consulta/contingência de OP;
- módulo de captura de pulsos GPIO;
- módulo de gestão de paradas;
- módulo de buffer de pulsos em parada manual;
- módulo de sincronização;
- módulo de monitoramento do estado do RPI.

### 9.4 Fluxo macro
1. RPI sobe automaticamente.
2. App carrega configuração do posto.
3. Operador faz login.
4. OP é carregada via API ou digitada em contingência.
5. Produção é registrada por eventos de pulso.
6. Paradas são gerenciadas conforme regra.
7. Encerramento passa por confirmação.
8. Eventos ficam no SQLite.
9. Ao reconectar, sincronizam com MySQL central.

## 10. Estratégia de Dados

### 10.1 Modelo de dados conceitual mínimo
Entidades mínimas:
- Dispositivo/RPI
- Setor
- Linha
- Usuário
- Perfil
- Turno
- OP
- Evento de produção
- Parada
- Motivo de parada
- Fila de sincronização
- Configuração local

### 10.2 Eventos
Cada evento de produção deve conter, no mínimo:
- UUID do evento;
- ID do dispositivo;
- timestamp;
- OP;
- setor;
- linha;
- turno;
- usuário logado;
- status de sincronização.

### 10.3 Retenção local
- eventos sincronizados ficam no SQLite por 15 dias;
- a gestão de retenção do banco central fica fora do escopo da aplicação v1.

## 11. Interface e Experiência do Usuário

### 11.1 Ambiente físico
- suporte a touchscreen e/ou teclado + mouse;
- execução em tela cheia.

### 11.2 Telas da v1
- Login
- Seleção/validação do posto configurado
- Busca/início de OP
- Tela de produção em tempo real
- Registro de parada manual
- Encerramento de OP com status pendente
- Tela administrativa local

### 11.3 Tela principal de produção (MVP)
Deve exibir:
- setor e linha;
- operador logado;
- OP atual;
- produto e derivação;
- quantidade produzida;
- quantidade prevista;
- status da linha;
- status da rede/sincronização;
- botão de parada;
- botão de finalizar OP.

## 12. Infraestrutura e Deployment

### 12.1 Ambiente central
- on-premise/local;
- infraestrutura existente.

### 12.2 Deploy v1
- deploy manual controlado;
- atualização por script local no RPI.

### 12.3 Inicialização
- autostart no boot do Raspberry;
- reinício automático do processo em caso de falha.

## 13. CI/CD e Operação

### 13.1 Estratégia da v1
- sem pipeline avançado obrigatório nesta fase;
- atualização manual via script;
- controle operacional local por posto.

### 13.2 Runbook mínimo recomendado
Mesmo fora do escopo formal, recomenda-se documentar:
- como configurar setor/linha no arquivo local;
- como validar GPIO;
- como validar conectividade com API e MySQL central;
- como verificar fila pendente;
- como reiniciar o serviço da aplicação.

## 14. Viabilidade Técnica

### 14.1 Avaliação
A solução é tecnicamente viável com o stack definido, porque:
- Raspberry Pi atende o cenário de edge local;
- PySide6 atende UI desktop fullscreen;
- SQLite atende persistência offline com simplicidade operacional;
- MySQL central atende consolidação;
- API dedicada resolve o acoplamento com ERP Oracle sem ligar o RPI diretamente ao Oracle.

### 14.2 Pontos de atenção técnicos
- robustez do módulo GPIO;
- concorrência entre UI, captura e sync;
- validação correta de duplicidade;
- reconciliação de OP em contingência;
- tratamento de travamento da aplicação;
- proteção contra corrupção de fila local em quedas abruptas de energia.

*Esses pontos são riscos técnicos de implementação, não impeditivos.*

## 15. Build vs Buy vs Integrate

### 15.1 Avaliação
Para a v1, a melhor abordagem é:
- Build da aplicação local SmartLeather;
- Integrate com a API de OP e MySQL central;
- sem adoção de produto comercial externo como núcleo da solução.

### 15.2 Justificativa
- o fluxo operacional é muito específico;
- há dependência de GPIO e comportamento offline-first;
- a integração com o ambiente fabril pede flexibilidade;
- ferramenta pronta tenderia a gerar lock-in e customização torta.

## 16. Riscos Técnicos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
| :--- | :--- | :--- | :--- |
| Duplicidade de eventos em reconexão | Média | Alto | UUID por evento + sincronização idempotente |
| Perda de eventos em falha de processo | Média | Alto | Persistir primeiro localmente; só depois considerar o evento aceito |
| OP digitada em contingência inconsistente | Média | Médio | Rotina automática de validação/enriquecimento ao retorno da API |
| Pulsos durante parada manual gerarem conflito | Média | Médio | Buffer + decisão explícita do operador |
| Travamento local em chão de fábrica | Média | Alto | Autostart + autorestart + script de operação simples |

## 17. Métricas de Sucesso

### 17.1 Métricas de negócio
- % de linhas/setores operando via SmartLeather
- % de OPs registradas com sucesso
- redução de apontamentos manuais externos
- disponibilidade de dados para cálculo futuro de performance/disponibilidade

### 17.2 Métricas técnicas
- % de eventos sincronizados com sucesso
- tamanho médio da fila pendente por dispositivo
- tempo médio entre reconexão e sincronização
- número de falhas de sincronização por dispositivo
- número de reinícios automáticos do app

### 17.3 Meta qualitativa
- sistema ser utilizável no posto com baixa fricção operacional;
- operador conseguir tocar o fluxo sem depender de suporte constante.

## 18. TCO
Fora do escopo detalhado da v1 neste PRD. A depender da próxima fase, pode ser detalhado com:
- custo por RPI;
- custo de manutenção;
- custo operacional do backend/API;
- esforço de suporte e atualização.

## 19. Glossário
- **RPI:** Raspberry Pi
- **OP:** Ordem de Produção
- **GPIO:** interface de entradas/saídas digitais do Raspberry Pi
- **SQLite:** banco local embarcado
- **MySQL central:** banco consolidado on-premise
- **Offline-first:** sistema projetado para operar normalmente sem rede
- **Idempotência:** capacidade de reprocessar sem duplicar efeitos
- **OEE:** Overall Equipment Effectiveness
- **Turno:** faixa horária operacional configurada

## 20. Dúvidas em Aberto / Pendências para evolução
Itens que podem virar backlog de próxima fase:
- definição formal de criptografia e proteção de credenciais;
- política de auditoria central;
- gestão centralizada de configuração dos RPIs;
- política de backup/restore;
- dashboards operacionais e cálculo de OEE;
- métricas formais de latência e SLO/SLA detalhados;
- estratégia de atualização remota dos dispositivos.

## 21. Recomendação final de escopo da v1
A v1 deve ser tratada como um produto operacional de captura confiável, não como plataforma completa de gestão industrial. O recorte certo é:
- capturar produção por pulso com segurança;
- registrar paradas;
- operar offline sem drama;
- sincronizar certo;
- travar fluxos críticos de forma previsível.

Esse recorte está enxuto, viável e tecnicamente coerente. Querer enfiar dashboard, gestão central total e analytics profundo já na v1 seria pedir para o projeto tropeçar na própria ambição.