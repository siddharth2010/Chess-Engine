"""Helper file for move generation"""

from .check import next_point

def get_knight_moves():
    """Generate a knight's movement range."""
    return [(-1, 2), (-1, -2), (2, 1), (2, -1),
            (-2, 1), (-2, -1), (1, 2), (1, -2)]

def get_bishop_moves(points, start):
    """Generate a given bishop's movement range."""
    moves = []

    for axis in [2, 3]:
        for positive in [True, False]:
            bound = next_point(start, points, axis, positive)

            if axis == 2:
                direction = (1, -1)
            else:
                direction = (1, 1)

            if positive:
                if bound is None:
                    bound = (7, 7)
            else:
                direction = tuple(map(lambda x: -x, direction))
                if bound is None:
                    bound = (0, 0)

            bound = bound[0]

            for i in range(1, abs(start[0] - bound) + 1):
                moves.append(tuple(i*j for j in direction))

    return moves

def get_rook_moves(points, start):
    """Generate a given rook's movement range."""
    moves = []

    for axis in [0, 1]:
        for positive in [True, False]:
            bound = next_point(start, points, axis, positive)
            if axis == 0:
                direction = (0, 1)
            else:
                direction = (1, 0)

            if positive:
                if bound is None:
                    bound = (7, 7)
            else:
                direction = tuple(map(lambda x: -x, direction))
                if bound is None:
                    bound = (0, 0)

            if axis == 0:
                bound = bound[1]
                move_range = range(1, abs(start[1] - bound) + 1)
            else:
                bound = bound[0]
                move_range = range(1, abs(start[0] - bound) + 1)

            for i in move_range:
                moves.append(tuple(i*j for j in direction))

    return moves

def get_queen_moves(points, start):
    """Generate a given queen's movement range."""
    return get_bishop_moves(points, start) + get_rook_moves(points, start)

def get_king_moves():
    """Generate the king's movement range."""
    return [(1, 0), (1, -1), (-1, 0), (-1, -1),
            (0, 1), (0, -1), (-1, 1), (1, 1)]

def get_finish(board, start, moves):
    """Generates white's finish points w.r.t. start for given moves."""
    valid_moves = []
    for move in moves:
        finish = tuple(map(sum, zip(start, move)))
        if (-1 < finish[0] < 8) and (-1 < finish[1] < 8):
            if finish not in board:
                valid_moves.append((start, finish))
            elif board[finish] in 'pnbrqk':
                valid_moves.append((start, finish))
    return valid_moves

def get_pawn_finish(board, start, enpassant_square):
    """Generate finish points for a given white pawn."""
    moves = []
    # check square(s) ahead
    finish = (start[0] - 1, start[1])
    if finish not in board:
        moves.append((start, finish))
        # check if pawn on starting square
        if start in {(6, col_num) for col_num in range(8)}:
            finish = (start[0] - 2, start[1])
            if finish not in board:
                moves.append((start, finish))
    # check diagonal squares
    finish = (start[0] - 1, start[1] + 1)
    if (finish in board) and (board[finish] in 'pnbrqk'):
        moves.append((start, finish))
    finish = (start[0] - 1, start[1] - 1)
    if (finish in board) and (board[finish] in 'pnbrqk'):
        moves.append((start, finish))
    # check enpassant_target
    if enpassant_square != None:
        finish = enpassant_square
        if start[0] - finish[0] == 1:
            if abs(start[1] - finish[1]) == 1:
                moves.append((start, finish))
    return moves

def get_king_finish(board, start, moves, castling_availability):
    """Generate finish points for the white king."""
    valid_moves = get_finish(board, start, moves)
    if 'K' in castling_availability:
        if next_point(start, board, 0, True) == (7, 7):
            valid_moves.append((start, (7, 6)))
    if 'Q' in castling_availability:
        if next_point(start, board, 0, False) == (7, 0):
            valid_moves.append((start, (7, 2)))
    return valid_moves

def get_moves(board, castling_availability, enpassant_square):
    """List of all moves for white for the given position."""
    moves = []
    points = board.keys()
    for start, piece in board.items():
        if piece == 'P':
            moves.extend(get_pawn_finish(board, start, enpassant_square))
        if piece == 'N':
            knight_moves = get_knight_moves()
            moves.extend(get_finish(board, start, knight_moves))
        if piece == 'B':
            bishop_moves = get_bishop_moves(points, start)
            moves.extend(get_finish(board, start, bishop_moves))
        if piece == 'R':
            rook_moves = get_rook_moves(points, start)
            moves.extend(get_finish(board, start, rook_moves))
        if piece == 'Q':
            queen_moves = get_queen_moves(points, start)
            moves.extend(get_finish(board, start, queen_moves))
        if piece == 'K':
            king_moves = get_king_moves()
            moves.extend(get_king_finish(board, start, king_moves,
                                         castling_availability))
    return moves
