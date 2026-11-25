# Relatório — Trabalho 2: Busca com Adversário (`beks_ia`)

## Integrantes
* Elano Tavares do Nascimento (Cartão: 00588513, Turma: B)
* Bruna Rosa Bragança de Lima (Cartão: 00588681, Turma: B)
* Karina [Sobrenome] (Cartão: XXXXXXXX, Turma: X)
* Stefano [Sobrenome] (Cartão: XXXXXXXX, Turma: X)

## Bibliotecas adicionais
Nenhuma biblioteca adicional além do ambiente padrão (Python 3.12) foi necessária para executar a implementação.

---

## 1. Avaliação — Tic-Tac-Toe Misère (Item 2.2a)

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

## 2. Avaliação — Othello (Item 2.2b)

### 2.1. Heurística customizada (`othello_minimax_custom.py`)
* **[Preencher — Bruna]:** Explicar o funcionamento da heurística customizada (`evaluate_custom`), os componentes avaliados (ex.: mobilidade, estabilidade, cantos/quinas, paridade, contagem) e eventuais fontes consultadas (artigos/sites e como foram adaptados).

### 2.2. Critério de parada
* **[Preencher — Bruna / Karina]:** Descrever o critério de parada adotado nos agentes de Othello (profundidade máxima fixa ou aprofundamento iterativo limitado por tempo) para respeitar o limite de 5 segundos por jogada na máquina de referência.

### 2.3. Resultados do Mini-Torneio
* **[Preencher — Karina]:** Preencher os resultados das 6 partidas obrigatórias (vencedor e placar final de peças):

| Partida (Pretas `B` x Brancas `W`) | Vencedor | Placar Final (`B` x `W`) |
| :--- | :---: | :---: |
| Contagem de peças (`B`) x Valor posicional (`W`) | - | - |
| Valor posicional (`B`) x Contagem de peças (`W`) | - | - |
| Contagem de peças (`B`) x Heurística customizada (`W`) | - | - |
| Heurística customizada (`B`) x Contagem de peças (`W`) | - | - |
| Valor posicional (`B`) x Heurística customizada (`W`) | - | - |
| Heurística customizada (`B`) x Valor posicional (`W`) | - | - |

* **Implementação mais bem-sucedida:** [Indicar qual heurística teve mais vitórias e, em caso de empate, maior saldo/captura de peças].

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
* **[Preencher — Grupo ao final]:** Declarar explicitamente se o grupo utilizou chatbots ou assistentes baseados em LLMs (como Gemini, ChatGPT, Claude, Copilot), relatando de que forma foram utilizados (ex.: esclarecimento de dúvidas sobre o enunciado, apoio na estruturação de testes e revisão de conceitos de poda alfa-beta/heurísticas, sem geração integral automática do trabalho) e avaliando a experiência de uso.