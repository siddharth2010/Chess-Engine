"""Helper file to test for check"""

def next_point(ref, points, axis, positive):
    """
    Returns next_point in points w.r.t. ref on given axis and direction.
    {int: axis} = {0: row, 1: column, 2: anti-diagonal, 3: diagonal}
    """
    if axis == 0:
        line = list(filter(lambda p: p[0] == ref[0], points))
        if positive:
            line = list(filter(lambda p: p[1] > ref[1], line))
            if line != []:
                return min(line, key=lambda p: p[1])
        else:
            line = list(filter(lambda p: p[1] < ref[1], line))
            if line != []:
                return max(line, key=lambda p: p[1])
    if axis == 1:
        line = list(filter(lambda p: p[1] == ref[1], points))
    if axis == 2:
        line = list(filter(lambda p: p[0] + p[1] == ref[0] + ref[1], points))
    if axis == 3:
        line = list(filter(lambda p: p[0] - p[1] == ref[0] - ref[1], points))

    if positive:
        line = list(filter(lambda p: p[0] > ref[0], line))
    else:
        line = list(filter(lambda p: p[0] < ref[0], line))
    if line != []:
        if positive:
            return min(line, key=lambda p: p[0])
        return max(line, key=lambda p: p[0])

    return None

def flip(board):
    """Returns horizontal mirror image of board with inverted colors."""
    flipped_board = dict()
    for square, piece in board.items():
        flipped_board[(7 - square[0], square[1])] = piece.swapcase()
    return flipped_board


def is_check(board):
    """Returns True if White in Check, False otherwise."""
    pieces = board.keys()

    enemy_knights = []
    enemy_pawns = []

    for square, piece in board.items():
        if piece == 'K':
            king = square
        if piece == 'k':
            enemy_king = square
        if piece == 'n':
            enemy_knights.append(square)
        if piece == 'p':
            enemy_pawns.append(square)

    # check for attack by enemy bishops, rooks, and queens
    for axis in range(4):
        for positive in [True, False]:
            square = next_point(king, pieces, axis, positive)
            if square != None:
                if (axis in [0, 1]) and (board[square] in 'qr'):
                    return True
                if (axis in [2, 3]) and (board[square] in 'qb'):
                    return True

    # check for attack by enemy knights
    for knight in enemy_knights:
        if (king[0] - knight[0])**2 + (king[1] - knight[1])**2 == 5:
            return True

    # check for attack by enemy pawns
    for pawn in enemy_pawns:
        if (king[0] - pawn[0] == 1) and (abs(king[1] - pawn[1]) == 1):
            return True

    # check for attack by enemy king
    if (king[0] - enemy_king[0])**2 + (king[1] - enemy_king[1])**2 < 3:
        return True

    return False
