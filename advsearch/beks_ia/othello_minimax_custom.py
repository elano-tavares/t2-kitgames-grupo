from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move

EMPTY = Board.EMPTY

# Mascara posicional do othello_minimax_mask.py (nao alterar os valores).
EVAL_TEMPLATE = [
    [100, -30, 6, 2, 2, 6, -30, 100],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [100, -30, 6, 2, 2, 6, -30, 100],
]

CORNERS = [(0, 0), (7, 0), (0, 7), (7, 7)]

# Cada casa X/C (coordenadas x, y) mapeada para o canto a que pertence.
XC_CORNER = {
    (1, 0): (0, 0), (0, 1): (0, 0), (1, 1): (0, 0),
    (6, 0): (7, 0), (7, 1): (7, 0), (6, 1): (7, 0),
    (0, 6): (0, 7), (1, 7): (0, 7), (1, 6): (0, 7),
    (6, 7): (7, 7), (7, 6): (7, 7), (6, 6): (7, 7),
}

XC_WHEN_CORNER_TAKEN = 5


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state
    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    return minimax_move(state, 4, evaluate_custom)


def evaluate_custom(state, player: str) -> float:
    """
    Evaluates an othello state from the point of view of the given player.
    If the state is terminal, returns its utility.
    If non-terminal, returns an estimate of its value based on your custom heuristic
    :param state: state to evaluate (instance of GameState)
    :param player: player to evaluate the state for (B or W)
    """
    board = state.get_board()
    tiles = board.tiles
    opponent = Board.opponent(player)

    mine = theirs = pos = 0
    for y in range(8):
        row = tiles[y]
        wrow = EVAL_TEMPLATE[y]
        for x in range(8):
            c = row[x]
            if c == EMPTY:
                continue
            w = wrow[x]
            if w < 0:  # casa X/C so penaliza enquanto o canto estiver vazio
                cx, cy = XC_CORNER[(x, y)]
                if tiles[cy][cx] != EMPTY:
                    w = XC_WHEN_CORNER_TAKEN
            if c == player:
                mine += 1
                pos += w
            else:
                theirs += 1
                pos -= w

    lm = len(board.legal_moves(player))
    lo = len(board.legal_moves(opponent))

    if lm == 0 and lo == 0:  # estado terminal: resultado exato
        return 10000.0 * (mine - theirs)

    cm = co = 0
    for cx, cy in CORNERS:
        c = tiles[cy][cx]
        if c == player:
            cm += 1
        elif c == opponent:
            co += 1

    mob = 100.0 * (lm - lo) / (lm + lo) if (lm + lo) else 0.0
    parity = 100.0 * (mine - theirs) / (mine + theirs) if (mine + theirs) else 0.0
    empties = 64 - mine - theirs

    if empties > 40:
        return 1.0 * pos + 4.0 * mob + 30.0 * (cm - co)
    elif empties > 14:
        return 1.0 * pos + 3.0 * mob + 30.0 * (cm - co) + 0.5 * parity
    else:
        return 0.5 * pos + 1.0 * mob + 30.0 * (cm - co) + 3.0 * parity
