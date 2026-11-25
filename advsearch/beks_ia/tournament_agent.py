import time
from typing import Tuple

# Agente do torneio de Othello (beks_ia).
# Poda alfa-beta com aprofundamento iterativo limitado por tempo,
# ordenacao de jogadas e heuristica combinada (posicional + mobilidade + cantos).
#
# Regras respeitadas:
#  - nada de threads/processos extras (o controle de tempo e' feito dentro da busca)
#  - nada de leitura de arquivos externos nem jogadas pre-calculadas
#  - retorna (x, y) = (coluna, linha); o tabuleiro e' indexado tiles[linha][coluna]

# Orcamento por jogada. O servidor da' 5 s; deixamos folga porque a maquina
# do torneio (Xeon E5-2650, 2.0 GHz) deve ser mais lenta que a nossa.
TIME_BUDGET = 3.5

EMPTY, BLACK, WHITE = '.', 'B', 'W'
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
CORNERS = [(0, 0), (7, 0), (0, 7), (7, 7)]

# Mesma mascara do othello_minimax_mask.py
WEIGHTS = [
    [100, -30, 6, 2, 2, 6, -30, 100],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [100, -30, 6, 2, 2, 6, -30, 100],
]

# Casas X/C -> canto ao qual pertencem: so' sao ruins enquanto o canto esta' vazio
XC_CORNER = {
    (1, 0): (0, 0), (0, 1): (0, 0), (1, 1): (0, 0),
    (6, 0): (7, 0), (7, 1): (7, 0), (6, 1): (7, 0),
    (0, 6): (0, 7), (1, 7): (0, 7), (1, 6): (0, 7),
    (6, 7): (7, 7), (7, 6): (7, 7), (6, 6): (7, 7),
}


class _Timeout(Exception):
    pass


def _opp(c):
    return WHITE if c == BLACK else BLACK


def _flips(tiles, x, y, color):
    """Pecas viradas se 'color' jogar em (x, y). Lista vazia = jogada ilegal."""
    if tiles[y][x] != EMPTY:
        return []
    opp = _opp(color)
    result = []
    for dx, dy in DIRECTIONS:
        cx, cy = x + dx, y + dy
        line = []
        while 0 <= cx < 8 and 0 <= cy < 8 and tiles[cy][cx] == opp:
            line.append((cx, cy))
            cx += dx
            cy += dy
        if line and 0 <= cx < 8 and 0 <= cy < 8 and tiles[cy][cx] == color:
            result.extend(line)
    return result


def _is_legal(tiles, x, y, color, opp):
    """Teste de legalidade rapido: para na primeira direcao valida e nao monta listas."""
    for dx, dy in DIRECTIONS:
        cx, cy = x + dx, y + dy
        if not (0 <= cx < 8 and 0 <= cy < 8) or tiles[cy][cx] != opp:
            continue
        cx += dx
        cy += dy
        while 0 <= cx < 8 and 0 <= cy < 8:
            c = tiles[cy][cx]
            if c == color:
                return True
            if c != opp:
                break
            cx += dx
            cy += dy
    return False


def _legal_moves(tiles, color):
    opp = _opp(color)
    moves = []
    for y in range(8):
        row = tiles[y]
        for x in range(8):
            if row[x] == EMPTY and _is_legal(tiles, x, y, color, opp):
                moves.append((x, y))
    return moves


def _apply(tiles, move, color):
    """Retorna um novo tabuleiro com a jogada aplicada (nao altera o original)."""
    x, y = move
    new = [row[:] for row in tiles]
    new[y][x] = color
    for fx, fy in _flips(tiles, x, y, color):
        new[fy][fx] = color
    return new


def _evaluate(tiles, me, my_moves=None, opp_moves=None):
    """Heuristica do ponto de vista de 'me'."""
    opp = _opp(me)

    if my_moves is None:
        my_moves = _legal_moves(tiles, me)
    if opp_moves is None:
        opp_moves = _legal_moves(tiles, opp)

    # contagem de pecas e valor posicional numa unica passada pelo tabuleiro
    mine = theirs = pos = 0
    for y in range(8):
        row = tiles[y]
        wrow = WEIGHTS[y]
        for x in range(8):
            c = row[x]
            if c == EMPTY:
                continue
            wgt = wrow[x]
            if wgt < 0:
                # penalidade de X/C so' vale enquanto o canto esta' vazio
                cx, cy = XC_CORNER[(x, y)]
                if tiles[cy][cx] != EMPTY:
                    wgt = 5
            if c == me:
                mine += 1
                pos += wgt
            else:
                theirs += 1
                pos -= wgt

    # estado terminal: resultado exato, com peso enorme
    if not my_moves and not opp_moves:
        return 10000 * (mine - theirs)

    empties = 64 - mine - theirs

    # mobilidade (diferenca normalizada)
    lm, lo = len(my_moves), len(opp_moves)
    mob = 100 * (lm - lo) / (lm + lo) if lm + lo else 0

    # cantos
    cm = co = 0
    for cx, cy in CORNERS:
        c = tiles[cy][cx]
        if c == me:
            cm += 1
        elif c == opp:
            co += 1

    # contagem de pecas so' importa no fim do jogo
    parity = 100 * (mine - theirs) / (mine + theirs)

    if empties > 40:      # abertura
        return 1.0 * pos + 4.0 * mob + 30 * (cm - co)
    elif empties > 14:    # meio de jogo
        return 1.0 * pos + 3.0 * mob + 30 * (cm - co) + 0.5 * parity
    else:                 # final
        return 0.5 * pos + 1.0 * mob + 30 * (cm - co) + 3.0 * parity


def _order(moves):
    """Ordena jogadas: cantos primeiro, casas X/C por ultimo."""
    return sorted(moves, key=lambda m: WEIGHTS[m[1]][m[0]], reverse=True)


def _alphabeta(tiles, to_move, me, depth, alpha, beta, deadline):
    if time.perf_counter() > deadline:
        raise _Timeout()

    moves = _legal_moves(tiles, to_move)
    other = _opp(to_move)

    if not moves:
        other_moves = _legal_moves(tiles, other)
        if not other_moves:  # fim de jogo
            return _evaluate(tiles, me, [], [])
        # turno repetido: o outro jogador joga de novo (nao assume alternancia fixa)
        if depth == 0:
            if to_move == me:
                return _evaluate(tiles, me, [], other_moves)
            return _evaluate(tiles, me, other_moves, [])
        return _alphabeta(tiles, other, me, depth - 1, alpha, beta, deadline)

    if depth == 0:
        if to_move == me:
            return _evaluate(tiles, me, moves, None)
        return _evaluate(tiles, me, None, moves)

    if to_move == me:  # MAX
        value = float('-inf')
        for m in _order(moves):
            value = max(value, _alphabeta(_apply(tiles, m, to_move), other, me,
                                          depth - 1, alpha, beta, deadline))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:  # MIN
        value = float('inf')
        for m in _order(moves):
            value = min(value, _alphabeta(_apply(tiles, m, to_move), other, me,
                                          depth - 1, alpha, beta, deadline))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def _search_root(tiles, me, moves, depth, deadline, partial):
    """Busca na raiz. 'partial' guarda a melhor jogada ja' confirmada nesta iteracao,
    para ser aproveitada se o tempo acabar no meio dela."""
    best_move, best_val = moves[0], float('-inf')
    alpha, beta = float('-inf'), float('inf')
    other = _opp(me)
    scored = []
    for m in moves:
        v = _alphabeta(_apply(tiles, m, me), other, me, depth - 1, alpha, beta, deadline)
        scored.append((v, m))
        if v > best_val:
            best_val, best_move = v, m
            partial['move'] = m
        alpha = max(alpha, best_val)
    return best_move, best_val, scored


LAST_DEPTH = 0  # profundidade completa alcancada na ultima jogada (usado nos testes)


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state.
    Consider that this will be called in the Othello tournament situation,
    so you should call the best implementation you got.

    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    global LAST_DEPTH
    start = time.perf_counter()
    deadline = start + TIME_BUDGET

    me = state.player
    tiles = [row[:] for row in state.board.tiles]
    moves = _legal_moves(tiles, me)
    LAST_DEPTH = 0

    if not moves:  # nao deveria acontecer (o servidor so' chama quem tem jogada)
        return (-1, -1)
    if len(moves) == 1:
        return moves[0]

    moves = _order(moves)
    best = moves[0]
    empties = sum(row.count(EMPTY) for row in tiles)

    depth = 1
    while depth <= empties:
        partial = {}
        try:
            move, _, scored = _search_root(tiles, me, moves, depth, deadline, partial)
        except _Timeout:
            # A primeira jogada testada e' a melhor da iteracao anterior. Se outra jogada
            # a superou com busca completa, o valor dela e' exato e pode ser usada.
            if 'move' in partial and partial['move'] != moves[0]:
                best = partial['move']
            break
        best = move
        LAST_DEPTH = depth
        # reordena pela iteracao anterior: a melhor jogada e' explorada primeiro
        scored.sort(key=lambda t: t[0], reverse=True)
        moves = [m for _, m in scored]
        depth += 1
        # se a proxima iteracao provavelmente nao cabe no tempo, para
        if time.perf_counter() - start > TIME_BUDGET * 0.35:
            break

    return best
