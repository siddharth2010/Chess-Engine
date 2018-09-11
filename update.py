"""Helper file for updating after a move"""

def new_b(board, enpassant_target, start, finish, promotion_piece):
    """Update board"""
    files = 'abcdefgh'
    piece = board[start]

    # remove captured pawn for enpassant
    if files[finish[1]] == enpassant_target[0]:
        if (piece == 'P') and (finish[0] == 2):
            board.pop((finish[0] + 1, finish[1]))
        if (piece == 'p') and (finish[0] == 5):
            board.pop((finish[0] - 1, finish[1]))

    # move rook for castling
    if piece in 'Kk':
        rook_finish = (start[0], (start[1] + finish[1])//2)
        if start[1] - finish[1] == 2:
            rook_start = (start[0], 0)
            board[rook_finish] = board.pop(rook_start)
        if start[1] - finish[1] == -2:
            rook_start = (start[0], 7)
            board[rook_finish] = board.pop(rook_start)

    # update piece position
    board[finish] = board.pop(start)

    # replace last rank pawn with promotion piece
    if piece in 'Pp':
        if finish[0] in [0, 7]:
            board[finish] = promotion_piece

    return board

def new_pp(board):
    """Update piece_placement"""
    nboard = [[' ']*8 for _ in range(8)]
    for square in board:
        nboard[square[0]][square[1]] = board[square]

    piece_placement = ''

    for row_num in range(8):
        count = 0
        for col_num in range(8):
            square = nboard[row_num][col_num]
            if square == ' ':
                count += 1
            else:
                if count != 0:
                    piece_placement += str(count)
                piece_placement += square
                count = 0
        if count != 0:
            piece_placement += str(count)
        piece_placement += '/'

    return piece_placement[:-1]

def new_ca(board, castling_availability):
    """Update castling_availability"""

    if (7, 7) in board:
        if board[(7, 7)] != 'R':
            castling_availability = castling_availability.replace('K', '')
    if (7, 0) in board:
        if board[(7, 0)] != 'R':
            castling_availability = castling_availability.replace('Q', '')

    if (7, 4) in board:
        if board[(7, 4)] != 'K':
            castling_availability = castling_availability.replace('K', '')
            castling_availability = castling_availability.replace('Q', '')

    if (0, 7) in board:
        if board[(0, 7)] != 'r':
            castling_availability = castling_availability.replace('k', '')
    if (0, 0) in board:
        if board[(0, 0)] != 'r':
            castling_availability = castling_availability.replace('q', '')

    if (0, 4) in board:
        if board[(0, 4)] != 'k':
            castling_availability = castling_availability.replace('k', '')
            castling_availability = castling_availability.replace('q', '')

    if castling_availability == '':
        castling_availability = '-'

    return castling_availability

def new_et(piece, start, finish):
    """Update enpassant_target"""
    files = 'abcdefgh'

    if (piece in 'Pp') and (abs(start[0] - finish[0]) == 2):
        row = 8 - (start[0] + finish[0])//2
        col = start[1]
        enpassant_target = files[col] + str(row)
    else:
        enpassant_target = '-'

    return enpassant_target

def new_hc(board, halfmove_clock, piece, finish):
    """Update halfmove_clock"""
    if (finish not in board) and (piece not in 'Pp'):
        halfmove_clock += 1
    else:
        halfmove_clock = 0
    return halfmove_clock
