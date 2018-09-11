"""Chessboard class"""
from six import python_2_unicode_compatible

from .check import flip, is_check
from .moves import get_moves
from .update import new_b, new_pp, new_ca, new_et, new_hc
from .notation import san, tup

@python_2_unicode_compatible
class Chessboard:
    """
    Chessboard class that supports 2 player games.
    """
    PIECES = 'KQRBNPkqrbnp'

    STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    ENPASSANT_MAP = {'a': (2, 0), 'b': (2, 1), 'c': (2, 2),
                     'd': (2, 3), 'e': (2, 4), 'f': (2, 5),
                     'g': (2, 6), 'h': (2, 7), '-': None}

    PRETTY_SYMBOLS = {'K' : u'\u2654', 'Q' : u'\u2655', 'R' : u'\u2656',
                      'B' : u'\u2657', 'N' : u'\u2658', 'P' : u'\u2659',
                      'k' : u'\u265A', 'q' : u'\u265B', 'r' : u'\u265C',
                      'b' : u'\u265D', 'n' : u'\u265E', 'p' : u'\u265F'}

    def __init__(self, fen=STARTING_FEN, pretty_print=False):
        """Create a new Chessboard"""
        self.pretty_print = pretty_print
        self.fen = fen

        fields = self.fen.split(' ')
        self.piece_placement = fields[0]
        self.active_color = fields[1]
        self.castling_availability = fields[2]
        self.enpassant_target = fields[3]
        self.halfmove_clock = int(fields[4])
        self.fullmove_number = int(fields[5])

        self.fen_stack = [self.fen]
        self.board = {}

        rows = self.piece_placement.split('/')
        for row_num, row in enumerate(rows):
            col_num = 0
            for square in row:
                if square in '12345678':
                    col_num += int(square)
                if square in Chessboard.PIECES:
                    self.board[(row_num, col_num)] = square
                    col_num += 1

    def move(self, ply):
        """Move a Piece"""
        promotion_piece = {'w': 'Q', 'b': 'q'}[self.active_color]
        if len(ply) == 5:
            if self.active_color == 'w':
                promotion_piece = ply[4].upper()
            else:
                promotion_piece = ply[4].lower()
            ply = ply[:4]

        start, finish = tup(ply)
        moves = self.get_legal_moves()

        fen_frequency = dict()
        for fen in self.fen_stack:
            partial_fen = ' '.join(fen.split(' ')[:4])
            if partial_fen in fen_frequency:
                fen_frequency[partial_fen] += 1
            else:
                fen_frequency[partial_fen] = 1
        repitition = max(fen_frequency.values())

        if (ply in moves) and (promotion_piece in 'bBnNrRqQ'):
            if (repitition != 5) and (self.halfmove_clock != 150):
                piece = self.board[start]

                self.halfmove_clock = new_hc(self.board, self.halfmove_clock, piece, finish)
                self.board = new_b(self.board, self.enpassant_target, start, finish, promotion_piece)
                self.castling_availability = new_ca(self.board, self.castling_availability)
                self.enpassant_target = new_et(piece, start, finish)
                self.piece_placement = new_pp(self.board)

                if self.active_color == 'w':
                    self.active_color = 'b'
                else:
                    self.active_color = 'w'
                    self.fullmove_number += 1

                self.fen = ' '.join([self.piece_placement,
                                     self.active_color,
                                     self.castling_availability,
                                     self.enpassant_target,
                                     str(self.halfmove_clock),
                                     str(self.fullmove_number)])

                self.fen_stack.append(self.fen)

                return self.game_status()

        return 'Invalid Move!'

    def get_legal_moves(self):
        """Generate Legal Moves"""
        board = dict(self.board)
        castling_availability = self.castling_availability
        enpassant_square = Chessboard.ENPASSANT_MAP[self.enpassant_target[0]]

        if self.active_color == 'b':
            board = flip(board)
            castling_availability = castling_availability.swapcase()

        all_moves = get_moves(board, castling_availability, enpassant_square)

        valid_moves = []
        for move in all_moves:
            nboard = dict(board)
            check_flag = is_check(nboard)

            # remove captured pawn for enpassant
            if (nboard[move[0]] == 'P') and (enpassant_square != None):
                if move[1] == enpassant_square:
                    nboard.pop((move[1][0] + 1, move[1][1]))

            # update piece position
            nboard[move[1]] = nboard.pop(move[0])

            if not is_check(nboard):
                # check adjacent squares before castling
                if nboard[move[1]] == 'K':
                    if abs(move[0][1] - move[1][1]) == 2:
                        finish = (7, (move[0][1] + move[1][1])//2)
                        nboard[finish] = nboard.pop(move[1])
                        if (not check_flag) and (not is_check(nboard)):
                            valid_moves.append(move)
                    else:
                        valid_moves.append(move)
                else:
                    valid_moves.append(move)

        if self.active_color == 'b':
            nmoves = []
            for move in valid_moves:
                start = (7 - move[0][0], move[0][1])
                finish = (7 - move[1][0], move[1][1])
                nmoves.append((start, finish))
            return [san(move) for move in nmoves]

        return [san(move) for move in valid_moves]

    def game_status(self):
        """Current Game Status"""
        board = dict(self.board)
        moves = self.get_legal_moves()
        if self.active_color == 'b':
            board = flip(board)
        check_status = is_check(board)

        if moves == []:
            if check_status:
                return 'Checkmate!'
            return 'Stalemate!'

        fen_frequency = dict()
        for fen in self.fen_stack:
            partial_fen = ' '.join(fen.split(' ')[:4])
            if partial_fen in fen_frequency:
                fen_frequency[partial_fen] += 1
            else:
                fen_frequency[partial_fen] = 1
        repitition = max(fen_frequency.values())

        if (self.halfmove_clock == 150) or (repitition == 5):
            status = 'Draw!'
            if check_status:
                status = 'Check!\n' + status
            return status
        if (self.halfmove_clock >= 100) or (repitition >= 3):
            status = 'Claim Draw?'
            if check_status:
                status = 'Check!\n' + status
            return status

        return None

    def undo(self):
        """Undo a Move"""
        fen_stack = self.fen_stack
        self.__init__(fen=self.fen_stack[-2], pretty_print=self.pretty_print)
        self.fen_stack = fen_stack[:-1]

    def reset(self):
        """Reset the Chessboard"""
        self.__init__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        board = [[' ']*8 for _ in range(8)]
        for i in self.board:
            if self.pretty_print:
                board[i[0]][i[1]] = Chessboard.PRETTY_SYMBOLS[self.board[i]]
            else:
                board[i[0]][i[1]] = self.board[i]
        return '\n'.join(map(''.join, board))
