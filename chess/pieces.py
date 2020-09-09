EMPTY_SQUARE = 0
WHITE_PIECES = frozenset([1, 2, 3, 4, 5, 6])
BLACK_PIECES = frozenset([-1, -2, -3, -4, -5, -6])
WHITE_PROMOTIONS = WHITE_PIECES - {6}
BLACK_PROMOTIONS = BLACK_PIECES - {-6}


def colour_of_piece(piece):
    if piece in WHITE_PIECES:
        return 1
    if piece in BLACK_PIECES:
        return -1


class Piece:
    fen = None

    def __init__(self):
        pass

    def move_squares(self, board, start):
        raise NotImplementedError()

    def threat_squares(self, board, start):
        raise NotImplementedError()

    # def poss_squares(self, board, start):
    #     return self.move_squares(board, start).union(self.threat_squares(board, start))

    def generate_end_squares(
        self,
        board,
        start,
        delta_x: int,
        delta_y: int,
        max_moves=7,
        can_take=True,
    ):
        ends = []
        pos = start
        for _ in range(max_moves):
            if not (0 < pos.rank + delta_y < 9) or not (0 < pos.file + delta_x < 9):
                break
            pos = pos.delta(delta_x, delta_y)
            if not pos:
                break

            piece_at_pos = board.piece_at(pos)
            if piece_at_pos == 0:
                ends.append(pos)
            else:
                if can_take and colour_of_piece(piece_at_pos) != self.colour:
                    ends.append(pos)
                break
        return ends

    @property
    def colour(self):
        return colour_of_piece(PIECES_FENS[self.fen])


class Knight(Piece):
    def move_squares(self, board, start):
        ends = set()
        for x in (1, -1):
            for y in (2, -2):
                ends.update(self.generate_end_squares(board, start, x, y, max_moves=1))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)


class WhiteKnight(Knight):
    fen = "N"


class BlackKnight(Knight):
    fen = "n"


class Bishop(Piece):
    def move_squares(self, board, start):
        ends = set()
        for x in (1, -1):
            for y in (1, -1):
                ends.update(self.generate_end_squares(board, start, x, y))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)


class WhiteBishop(Bishop):
    fen = "B"


class BlackBishop(Bishop):
    fen = "b"


class Rook(Piece):
    def move_squares(self, board, start):
        ends = set()
        for x in (1, -1):
            ends.update(self.generate_end_squares(board, start, x, 0))
            ends.update(self.generate_end_squares(board, start, 0, x))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)


class WhiteRook(Rook):
    fen = "R"


class BlackRook(Rook):
    fen = "r"


class Queen(Piece):
    def move_squares(self, board, start):
        ends = set()
        for x in (1, -1):
            for y in (1, -1):
                ends.update(self.generate_end_squares(board, start, x, y))
            ends.update(self.generate_end_squares(board, start, x, 0))
            ends.update(self.generate_end_squares(board, start, 0, x))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)


class WhiteQueen(Queen):
    fen = "Q"


class BlackQueen(Queen):
    fen = "q"


class King(Piece):
    def move_squares(self, board, start):
        ends = set()
        for x in (1, -1):
            for y in (1, -1):
                ends.update(self.generate_end_squares(board, start, x, y, max_moves=1))
            ends.update(self.generate_end_squares(board, start, x, 0, max_moves=1))
            ends.update(self.generate_end_squares(board, start, 0, x, max_moves=1))
        return ends

    def threat_squares(self, board, start):
        return self.move_squares(board, start)


class WhiteKing(King):
    fen = "K"


class BlackKing(King):
    fen = "k"


class Pawn(Piece):
    def move_squares(self, board, start):
        start_square = False
        if self.fen == "P":
            dy = 1
            if start.rank == 2:
                start_square = True
        else:
            dy = -1
            if start.rank == 7:
                start_square = True
        if start_square:
            max_m = 2
        else:
            max_m = 1
        ends = set(
            self.generate_end_squares(
                board, start, 0, dy, max_moves=max_m, can_take=False
            )
        )
        return ends

    def threat_squares(self, board, start):
        ends = set()
        if self.fen == "P":
            dy = 1
        else:
            dy = -1
        ends.update(self.generate_end_squares(board, start, 1, dy, max_moves=1))
        ends.update(self.generate_end_squares(board, start, -1, dy, max_moves=1))
        return ends


class WhitePawn(Pawn):
    fen = "P"


class BlackPawn(Pawn):
    fen = "p"


class EnPassentTarget(Piece):
    fen = "E"

    def move_squares(self, board, start):
        ends = set()
        return ends

    def threat_squares(self, board, start):
        ends = set()
        return ends


# TODO this is horrible.
PIECES_FENS = {
    "K": 1,
    "Q": 2,
    "R": 3,
    "B": 4,
    "N": 5,
    "P": 6,
    "k": -1,
    "q": -2,
    "r": -3,
    "b": -4,
    "n": -5,
    "p": -6,
    "E": 7,
}
PIECES = {
    1: WhiteKing,
    2: WhiteQueen,
    3: WhiteRook,
    4: WhiteBishop,
    5: WhiteKnight,
    6: WhitePawn,
    -1: BlackKing,
    -2: BlackQueen,
    -3: BlackRook,
    -4: BlackBishop,
    -5: BlackKnight,
    -6: BlackPawn,
    7: EnPassentTarget,
}
