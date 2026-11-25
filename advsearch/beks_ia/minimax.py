from typing import Tuple, Callable

def minimax_move(state, max_depth: int, eval_func: Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    jogador_raiz = state.player
    alfa = float('-inf')
    beta = float('inf')

    melhor_valor = float('-inf')
    melhor_jogada = None

    prox_profundidade = -1 if max_depth == -1 else max_depth - 1

    for jogada in state.legal_moves():
        proximo_estado = state.next_state(jogada)
        valor = _minimax(
            proximo_estado,
            prox_profundidade,
            alfa,
            beta,
            jogador_raiz,
            eval_func
        )

        if melhor_jogada is None or valor > melhor_valor:
            melhor_valor = valor
            melhor_jogada = jogada

        if melhor_valor > alfa:
            alfa = melhor_valor

    return melhor_jogada


def _minimax(state, profundidade: int, alfa: float, beta: float, jogador_raiz: str, eval_func: Callable) -> float:
    if state.is_terminal() or (profundidade != -1 and profundidade <= 0):
        return eval_func(state, jogador_raiz)

    jogadas = state.legal_moves()
    if not jogadas:
        return eval_func(state, jogador_raiz)

    prox_profundidade = -1 if profundidade == -1 else profundidade - 1

    # Nó MAX (vez do jogador da raiz)
    if state.player == jogador_raiz:
        v = float('-inf')
        for jogada in jogadas:
            proximo_estado = state.next_state(jogada)
            valor = _minimax(proximo_estado, prox_profundidade, alfa, beta, jogador_raiz, eval_func)
            if valor > v:
                v = valor
            if v >= beta:
                return v  # Poda beta
            if v > alfa:
                alfa = v
        return v

    # Nó MIN (vez do oponente)
    else:
        v = float('inf')
        for jogada in jogadas:
            proximo_estado = state.next_state(jogada)
            valor = _minimax(proximo_estado, prox_profundidade, alfa, beta, jogador_raiz, eval_func)
            if valor < v:
                v = valor
            if v <= alfa:
                return v  # Poda alfa
            if v < beta:
                beta = v
        return v