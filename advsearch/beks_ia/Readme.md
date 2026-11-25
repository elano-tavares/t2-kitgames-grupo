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
* **[Preencher — Stefano]:** Descrever a estratégia final adotada no `tournament_agent.py` (algoritmo base, heurística utilizada, critério de parada/tempo e otimizações aplicadas para respeitar o limite de 5s e 4 GB de RAM sem processos em background ou dados pré-calculados).

---

## 4. Extras
* **[Preencher — Stefano / Grupo]:** Relatar melhorias adicionais implementadas (ex.: ordenação de jogadas, aprofundamento iterativo, tabela de transposição ou MCTS opcional em `mcts.py`) e eventuais fontes utilizadas. Caso nenhum extra tenha sido implementado, declarar explicitamente.

---

## 5. Declaração de uso de IA (LLMs / Chatbots)
* **[Preencher — Grupo ao final]:** Declarar explicitamente se o grupo utilizou chatbots ou assistentes baseados em LLMs (como Gemini, ChatGPT, Claude, Copilot), relatando de que forma foram utilizados (ex.: esclarecimento de dúvidas sobre o enunciado, apoio na estruturação de testes e revisão de conceitos de poda alfa-beta/heurísticas, sem geração integral automática do trabalho) e avaliando a experiência de uso.