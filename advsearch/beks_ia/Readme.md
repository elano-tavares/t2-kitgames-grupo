# Relatório — Trabalho 2: Busca com Adversário (`beks_ia`)

## Integrantes
* Elano Tavares do Nascimento (Cartão: 00588513, Turma: B)
* Bruna Rosa Bragança de Lima (Cartão: 00588681, Turma: B)
* Karina Ribeiro Martins (Cartão: 00590451, Turma: B)
* Stefano Dahmer (Cartão: 00590514, Turma: B)

## Bibliotecas adicionais
Nenhuma biblioteca adicional além do ambiente padrão (Python 3.12) foi necessária para executar a implementação.

---

## 1. Avaliação: Tic-Tac-Toe Misère (Item 2.2a)

Para o Jogo da Velha Invertido (`tttm_minimax.py`), implementamos a função de utilidade terminal (`+1.0` para vitória, `0.0` para empate e `-1.0` para derrota) e executamos o algoritmo Minimax com poda alfa-beta (`minimax.py`) com profundidade ilimitada (`max_depth = -1`), explorando completamente a árvore de estados do jogo (profundidade máxima 9). Antes das partidas no servidor, a implementação foi validada nos testes unitários `test_pruning.py` (2/2 testes aprovados) e `test_minimax_tttm.py` (4/4 testes aprovados).

* **(i) O minimax sempre ganha ou empata jogando contra o `randomplayer`?**
  **Sim.** Em todos os testes realizados, o agente nunca perdeu para o `randomplayer`:
  * **Jogando como `B` (primeiro a jogar):** O agente abriu invariavelmente na posição central `(1, 1)` — única abertura que garante não perder com jogo perfeito. Em uma bateria de 10 partidas consecutivas contra o `randomplayer`, obteve **6 vitórias e 4 empates (0 derrotas)**, além da vitória na partida individual de validação (`1` a `-1`).
  * **Jogando como `W` (segundo a jogar):** O agente também venceu a partida disputada (`1` a `-1`), aproveitando jogadas subótimas do oponente aleatório para forçá-lo a alinhar três peças.

* **(ii) O minimax sempre empata consigo mesmo?**
  **Sim.** Nas partidas executadas entre duas instâncias do nosso agente (`beks_ia (B) x beks_ia (W)`), o resultado foi deterministicamente **empate (`0` a `0`)**, preenchendo todas as 9 casas do tabuleiro sem que nenhum dos lados formasse uma linha de três peças (sequência: `(1,1) -> (0,1) -> (2,1) -> (1,2) -> (1,0) -> (2,2) -> (0,0) -> (2,0) -> (0,2)`). Isso evidencia que ambos os jogadores seguem linhas ótimas de jogo.

* **(iii) O minimax não perde para você quando você usa a sua melhor estratégia?**
  **Sim, o agente não perdeu nenhuma partida.**
  * **Humano (`B`) x `beks_ia` (`W`):** Ao tentar abrir pelo centro `(1, 1)` e jogar na diagonal, o jogador humano acabou forçado pelo agente a fechar a diagonal principal `(0,0)-(1,1)-(2,2)`, resultando em vitória do Minimax (`1` a `-1`).
  * **`beks_ia` (`B`) x Humano (`W`):** Jogando defensivamente de forma cuidadosa contra a abertura central `(1, 1)` do agente, o melhor resultado alcançado pelo jogador humano foi o **empate (`0` a `0`)** após o preenchimento completo do tabuleiro.

---

## 2. Avaliação: Othello (Item 2.2b)

### 2.1. Heurística customizada (`othello_minimax_custom.py`)

A `evaluate_custom` avalia o estado do ponto de vista do jogador da raiz combinando quatro componentes clássicos da estratégia de Othello, com pesos que mudam conforme a **fase da partida** (medida pelo número de casas vazias). A ideia central é que *contar peças*, como faz a heurística de contagem, é um mau indicador até o fim do jogo (liderar cedo costuma significar peças instáveis e pouca mobilidade), enquanto a heurística posicional, embora melhor, é estática e ignora quantas jogadas cada lado tem. A customizada une os dois e acrescenta mobilidade e paridade dinâmica.

**Componentes (todos do ponto de vista do jogador):**

* **Valor posicional (`pos`):** usa a mesma máscara do `othello_minimax_mask.py` (não alterada), somando o peso das casas ocupadas pelo jogador e subtraindo as do oponente. Com um ajuste importante: as casas **X e C** (vizinhas de um canto), que a máscara penaliza fortemente (`-50`/`-30`), só continuam penalizadas **enquanto o canto correspondente está vazio**, pois ocupar uma casa X/C com o canto aberto convida o oponente a tomar o canto. Quando o canto já está preenchido, essas casas deixam de ser perigosas e passam a valer `+5`. O mapa `XC_CORNER` associa cada casa X/C ao seu canto.
* **Mobilidade (`mob`):** diferença **normalizada** entre o número de jogadas legais do jogador e do oponente, `100·(m_eu − m_op)/(m_eu + m_op)`. Restringir as opções do adversário costuma forçá-lo a jogar em casas ruins (inclusive entregar cantos).
* **Cantos (`cantos`):** `30` pontos por canto de vantagem. O canto é a única casa permanentemente estável (nunca pode ser capturada), por isso tem peso alto e independente da fase.
* **Paridade (`parity`):** diferença normalizada de peças, `100·(peças_eu − peças_op)/(total)`. Recebe peso quase nulo na abertura e **cresce no final**, quando o saldo de peças é o que de fato decide a partida.

**Pesos por fase:**

| Fase | Casas vazias | Fórmula |
| :--- | :---: | :--- |
| Abertura | > 40 | `1,0·pos + 4,0·mob + 30·cantos` |
| Meio de jogo | 15–40 | `1,0·pos + 3,0·mob + 30·cantos + 0,5·paridade` |
| Final | ≤ 14 | `0,5·pos + 1,0·mob + 30·cantos + 3,0·paridade` |

Estados **terminais** são tratados à parte: retornam o valor exato `10000·(peças_eu − peças_op)`, que sempre domina a avaliação heurística, garantindo que a busca prefira uma vitória/derrota real a qualquer estimativa.

**Validação.** Jogando com profundidade fixa 4 (ver 2.2) e de forma determinística, a heurística customizada venceu as duas básicas nas duas cores: contra a contagem, `55×9` (custom de Pretas) e `55×1` (custom de Brancas); contra a posicional, `52×12` e `62×1`. Também venceu as 4 partidas de teste contra o `randomplayer`, incluindo situações de turno repetido (jogos em que o oponente ficou sem jogadas), tratadas corretamente pelo `minimax.py`. O tempo por jogada em profundidade 4 ficou bem dentro do limite de 5 s (ver as medições na seção 2.2).

**Fontes.** A máscara posicional (`EVAL_TEMPLATE`) é a fornecida no kit, usada como está, adaptada de https://web.fe.up.pt/~eol/IA/MIA0203/trabalhos/Damas_Othelo/Docs/Eval.html. As ideias de avaliação por **contagem de peças** e por **valor posicional** (casas com pesos, cantos valendo muito) correspondem ao tratamento clássico de Othello descrito, por exemplo, no capítulo 18 de *Paradigms of Artificial Intelligence Programming* (Peter Norvig), referência que o próprio kit já cita em `othello/board.py`. Os demais componentes (**mobilidade** normalizada, **controle de cantos**, tratamento das **casas X/C** e **paridade ponderada por fase**) são conceitos consolidados da estratégia de Othello. **A combinação específica, os pesos e a divisão em fases não foram retirados de uma fonte única:** foram montados e calibrados pelo grupo, com apoio de uma ferramenta de IA, na mesma família de avaliação usada pelo agente do torneio (seção 3.2).

### 2.2. Critério de parada
* O critério de parada adotado foi a **profundidade máxima fixa**, com valor **4** nas três heurísticas (contagem, posicional e customizada). Escolhemos profundidade fixa, e não aprofundamento iterativo limitado por tempo, porque, com um prazo em tempo, a heurística mais barata de calcular alcançaria uma profundidade maior e poderia vencer por velocidade, e não por qualidade. Com a mesma profundidade, a diferença de resultado vem da heurística. Além disso, o jogo fica determinístico e reproduzível.

Para escolher o valor, medimos o tempo de `minimax_move` nas profundidades de 2 a 5, em posições de meio de jogo (jogadas 16 a 40), com um script de medição escrito com auxílio de IA. A máquina usada foi um notebook com AMD Ryzen 7 5700U (1,80 GHz), 8 GB de RAM, Windows e Python 3.14.7, na tomada. O pior tempo por jogada foi de 1.71s na profundidade 4 e de 11,35s na profundidade 5, o que a inviabiliza frente ao limite de 5 s. Escolhemos a profundidade 4, cujo pior caso (1,71 s) corresponde a cerca de um terço do limite, o que deixa margem caso a máquina de referência seja mais lenta que a nossa.

### 2.3. Resultados do Mini-Torneio
As 6 partidas obrigatórias foram disputadas com todos os agentes em profundidade fixa 4. Como não há aleatoriedade, os resultados são determinísticos e reproduzíveis. Vencedor e placar final de peças:

| Partida (Pretas `B` x Brancas `W`) | Vencedor | Placar Final (`B` x `W`) |
| :--- | :---: | :---: |
| Contagem de peças (`B`) x Valor posicional (`W`) | Valor posicional | 28 x 36 |
| Valor posicional (`B`) x Contagem de peças (`W`) | Contagem de peças | 22 x 42 |
| Contagem de peças (`B`) x Heurística customizada (`W`) | Heurística customizada | 1 x 55 |
| Heurística customizada (`B`) x Contagem de peças (`W`) | Heurística customizada | 55 x 9 |
| Valor posicional (`B`) x Heurística customizada (`W`) | Heurística customizada | 1 x 62 |
| Heurística customizada (`B`) x Valor posicional (`W`) | Heurística customizada | 52 x 12 |

* **Implementação mais bem-sucedida:** a **heurística customizada**, com **4 vitórias em 4 partidas**, contra 1 vitória da contagem de peças e 1 da posicional. Venceu nas duas cores e por larga margem, somando 224 peças próprias nas suas 4 partidas, contra 80 da contagem e 71 da posicional (cada uma também em 4 partidas). Entre as duas básicas houve empate em vitórias (1 a 1): curiosamente, nas duas partidas entre elas venceu sempre quem jogou de Brancas (segundo a jogar).

---

## 3. Agente do Torneio (`tournament_agent.py`)
### 3.1. Algoritmo
O agente do torneio usa **poda alfa-beta com aprofundamento iterativo limitado por tempo**. O arquivo é autocontido: não usa o `minimax.py` nem o `GameState.next_state` do kit, e tem uma simulação própria do tabuleiro (cópia de listas). O `next_state` do kit copia o tabuleiro convertendo-o para texto e de volta, o que é lento e limitaria a profundidade da busca. A geração e a aplicação de jogadas da simulação própria foram validadas contra o kit em 300 partidas aleatórias, com resultados idênticos.

* **Turno repetido:** o tipo do nó (MAX ou MIN) é decidido comparando o jogador da vez com o jogador da raiz, e não por alternância fixa. Se o jogador da vez não tem jogadas, a vez passa ao oponente; se nenhum dos dois tem, o estado é terminal.
* **Coordenadas:** o tabuleiro é indexado como `tiles[linha][coluna]` e as jogadas são retornadas como `(x, y) = (coluna, linha)`.

### 3.2. Heurística
A avaliação, feita do ponto de vista do jogador da raiz, combina:
* **Valor posicional:** a mesma máscara do `othello_minimax_mask.py`, com um ajuste: as casas X e C (vizinhas dos cantos) só são penalizadas enquanto o canto correspondente está vazio; com o canto ocupado, passam a valer `+5`.
* **Mobilidade:** diferença normalizada entre o número de jogadas legais de cada lado, `100·(m_eu − m_op)/(m_eu + m_op)`.
* **Cantos:** `30` pontos por canto de vantagem.
* **Paridade de peças:** diferença normalizada de peças, relevante só no fim do jogo.

Os pesos mudam conforme a fase da partida:

| Fase | Casas vazias | Fórmula |
| :--- | :---: | :--- |
| Abertura | > 40 | `1,0·pos + 4,0·mob + 30·cantos` |
| Meio de jogo | 15–40 | `1,0·pos + 3,0·mob + 30·cantos + 0,5·paridade` |
| Final | ≤ 14 | `0,5·pos + 1,0·mob + 30·cantos + 3,0·paridade` |

Estados terminais recebem o valor exato `10000 · (peças_eu − peças_op)`, que sempre domina a heurística.

### 3.3. Critério de parada e limites do torneio
* **Tempo:** o orçamento é de **3,5 s por jogada** (o servidor concede 5 s). A folga compensa a máquina do torneio (Xeon E5-2650, 2,0 GHz), que deve ser mais lenta que a usada nos testes. Como o limite é por tempo, e não por profundidade fixa, numa máquina mais lenta o agente apenas busca menos fundo.
* **Checagem dentro da busca:** o relógio é verificado em todo nó. Ao estourar o prazo, uma exceção interrompe a busca imediatamente. Isso importa porque o servidor chama o `make_move` numa thread e, num timeout, essa thread continuaria rodando em background; o agente nunca chega a esse ponto.
* **Iterações:** a busca começa na profundidade 1 e aumenta de 1 em 1. Uma nova profundidade só começa se ainda não se passaram 35% do orçamento, porque cada nível custa várias vezes o anterior. Se o tempo acaba no meio de uma profundidade, o agente usa a melhor jogada da última profundidade completa, ou a jogada da profundidade interrompida que já superou essa com busca completa (cujo valor é exato).
* **Final exato:** a busca para ao atingir o número de casas vazias. Nos finais com poucas casas vazias, a árvore é percorrida até o fim e a jogada é escolhida pelo resultado real.
* **Memória:** não há tabela de transposição nem estruturas que cresçam entre jogadas. A recursão tem no máximo cerca de 60 níveis e o pico medido foi de cerca de 40 KB, muito abaixo do limite de 4 GB.
* **Regras de desclassificação:** o agente não cria threads nem processos, não lê arquivos e não usa jogadas pré-calculadas.

### 3.4. Testes
Os testes rodaram num notebook com Python 3.14, com o agente jogando alternadamente de pretas e brancas. A versão final foi comparada com a versão anterior do mesmo agente (mesma heurística, sem as otimizações da seção 4):

| Adversário | Partidas | Resultado (V/E/D) | Saldo médio de peças |
| :--- | :---: | :---: | :---: |
| `randomplayer` | 4 | 4 / 0 / 0 | +55,0 |
| Minimax do grupo com a heurística posicional (profundidade 3) | 2 | 2 / 0 / 0 | +59,5 |
| Versão anterior do agente do torneio | 4 | 4 / 0 / 0 | +28,5 |

* **Tempo por jogada:** máximo de 3,53 s e média de cerca de 2,0 s.
* **Profundidade média alcançada:** 6, chegando a 11–14 no final do jogo.
* **Servidor oficial:** numa partida pelo `server.py` com limite de 5 s (`-d 5`), o agente venceu o `randomplayer` por 57 a 7, sem jogadas ilegais nem estouro de tempo, incluindo uma situação de turno repetido.

---

## 4. Extras
Melhorias de busca implementadas no `tournament_agent.py`:
* **Aprofundamento iterativo limitado por tempo:** descrito na seção 3.3.
* **Ordenação de jogadas:** na raiz, as jogadas são reordenadas pelo valor obtido na iteração anterior, de modo que a melhor é explorada primeiro e as podas aumentam. Nos nós internos, a ordem é estática pela máscara posicional: cantos primeiro, casas X e C por último.
* **Aproveitamento da iteração interrompida:** descrito na seção 3.3.
* **Otimizações de desempenho:**
  * teste de legalidade que para na primeira direção válida, sem montar listas;
  * mapa direto de cada casa X/C para o seu canto;
  * contagem de peças e valor posicional calculados numa única passada pelo tabuleiro.

  Juntas, essas otimizações deixaram a avaliação cerca de 1,6 vez mais rápida, o que se converte em mais profundidade dentro do mesmo tempo.

**Não implementado:** o MCTS opcional (`mcts.py`) ficou de fora. Em Python puro, o número de simulações possíveis em 5 s seria pequeno, e o grupo optou por concentrar o esforço na poda alfa-beta. A tabela de transposição também não foi implementada.

**Fontes:** a máscara posicional é a fornecida no kit (`EVAL_TEMPLATE`, adaptada de https://web.fe.up.pt/~eol/IA/MIA0203/trabalhos/Damas_Othelo/Docs/Eval.html). Os demais componentes da heurística (mobilidade, cantos, casas X/C e paridade) são conceitos clássicos de estratégia de Othello.

---

## 5. Declaração de uso de IA (LLMs / Chatbots)

O grupo utilizou os assistentes de IA **Claude** e **Gemini** como apoio ao longo do desenvolvimento, principalmente para esclarecer dúvidas sobre o enunciado, revisar conceitos de poda alfa-beta e de estratégia de Othello, e auxiliar no projeto e na calibração das heurísticas. 

Não utilizamos os assistentes para gerar automaticamente a solução completa do trabalho!
A implementação dos algoritmos foi feita pelo grupo.

* **Avaliação da experiência:** No geral achamos a experiência boa, com a ressalva de que os assistentes ajudaram mais a pensar do que a escrever código pronto. Eles renderam melhor quando já tínhamos uma ideia na cabeça e queríamos confirmar algo ou destravar um ponto específico. Alguns exemplos do que perguntamos ao longo do trabalho:
  * **Enunciado e kit:** a dúvida que mais apareceu foi o sistema de coordenadas, já que a jogada é `(x, y)` (coluna, linha) mas o tabuleiro é indexado `tiles[linha][coluna]`, e é fácil trocar os dois sem perceber. Também recorremos aos assistentes para entender a regra de passar a vez quando um jogador não tem jogada, que é o que faz o mesmo jogador jogar duas vezes seguidas, e para esclarecer as restrições do torneio (5 segundos, 4 GB, sem threads, arquivos externos ou jogadas pré-calculadas).
  * **Poda alfa-beta:** ajudou a entender por que o nó MAX ou MIN precisa ser decidido comparando o jogador da vez com o da raiz, em vez de assumir que os jogadores sempre se alternam, que é justamente o caso dos turnos repetidos.
  * **Tic-tac-toe misère:** confirmamos que a utilidade terminal é invertida e que dá para rodar sem limite de profundidade, porque a árvore do jogo é pequena.
  * **Heurísticas de Othello:** foi onde mais conversamos. Falamos sobre por que contar peças é um critério fraco (sair na frente cedo costuma ser ruim), como funciona o valor posicional e a máscara, e a ideia de juntar mobilidade, cantos, as casas X/C (que só são ruins enquanto o canto está vazio) e a paridade, que pesa mais no fim do jogo. Os assistentes também entraram na calibração dos pesos e na discussão de como testar se a customizada realmente ganhava das básicas.
  * **Critério de parada e testes:** discutimos usar profundidade fixa ou aprofundamento iterativo por tempo, e como montar as partidas de teste de forma determinística, jogando tanto de pretas quanto de brancas.

  O lado negativo é que às vezes eles respondem com muita confiança mesmo estando errados. A calibração dos pesos, por exemplo, só ficou confiável depois de jogar as partidas e ver os números, e não apenas pela sugestão do modelo. Também tivemos que ter cuidado com o sistema de coordenadas, que foi uma das maiores fontes de bug e nem sempre o modelo chamava atenção para isso.

* **Uso específico por integrante:**
  * Karina — Claude: script que roda as partidas do mini-torneio pelo servidor e monta as tabelas de resultado, script de verificação de corretude e de medição de tempo por profundidade.
  * Stefano — Claude (Claude Code), usado por Stefano: o `tournament_agent.py` foi escrito por mim e depois revisado com o Claude, que conferiu as coordenadas, o tratamento de turno repetido e o controle de tempo. O Claude também sugeriu e implementou otimizações de desempenho, que foram aprovadas antes de serem aplicadas: como aproveitar a iteração interrompida e um teste de legalidade mais rápido. Também escreveu os scripts de teste.
  * Elano — Gemini: apoio na análise do enunciado e divisão de tarefas do grupo, esclarecimento sobre a interface do `GameState` e o tratamento de turnos repetidos na poda alfa-beta, auxílio na estruturação e revisão do `minimax.py` e do `tttm_minimax.py` frente aos testes unitários (`test_pruning.py` e `test_minimax_tttm.py`), além da execução dos testes no servidor e redação inicial do `Readme.md` (Item 2.2a).
  * Bruna — Claude (Claude Code): utilizei o Claude para discutir e entender conceitos de avaliação em Othello e para refinar os pesos da heurística customizada. Implementei a `evaluate_custom` e o `make_move` e validei o agente em partidas contra o `randomplayer` e contra as heurísticas básicas, nas duas cores. O Claude auxiliou na automação da medição de tempo.