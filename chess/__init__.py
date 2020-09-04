import chess.pieces


class InvalidSquareException(Exception):
    """Created when trying to make an illegal square"""

    pass


def string_to_coords(data: str):
    if len(data) != 2:
        raise InvalidSquareException(f"{data} is not a valid square")
    file = ord(data[0]) - ord("a")
    rank = int(data[1])
    return (file, rank)


def coords_to_string(data: tuple):
    if len(data) != 2:
        raise InvalidSquareException(f"{data} is not a valid square")
    file = ord(data[0] + ord("a") - 1)
    return f"{file}{data[1]}"


class Square:
    def __init__(self, file: int, rank: int):
        if file < 1 or file > 8:
            raise InvalidSquareException(f"{file} is not a valid file")
        if rank < 1 or rank > 8:
            raise InvalidSquareException(f"{rank} is not a valid rank")
        self.file = file
        self.rank = rank

    def delta(self, dx, dy):
        return Square(self.file + dx, self.rank + dy)

    def to_coords(self):
        return (self.file, self.rank)

    def __str__(self):
        file = chr(self.file - 1 + ord("a"))
        return f"{file}{self.rank}"

    def __eq__(self, other):
        if other is None:
            return False
        return self.rank == other.rank and self.file == other.file

    def __hash__(self):
        return hash((self.rank, self.file))


class Move:
    def __init__(self, start: Square, end: Square, prom=None):
        self.start = start
        self.end = end
        self.prom = prom

    def __str__(self):
        s = f"({self.start} to {self.end})"
        if self.prom:
            s += f"{self.prom}"

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

    @property
    def man_dist(self):
        return abs(self.start.file - self.end.file) + abs(
            self.start.rank + self.end.rank
        )


class Board:
    def __init__(self, fen=None):
        self.squares = [None for _ in range(64)]
        self.white_in_check = False
        self.black_in_check = False
        if fen:
            self.load_from_fen(fen)
        else:
            self.squares[0:7] = list("RNBQKBNR")
            self.squares[8:15] = ["P" for _ in range(8)]
            self.squares[48:55] = ["p" for _ in range(8)]
            self.squares[56:63] = list("rnbqkbnr")

    def fen(self):
        fen = ""
        for y in range(8):
            empty_count = 0
            for x in range(8):
                if self.squares[8*y + x] is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += f"{empty_count}"
                        empty_count = 0
                    fen += self.squares[8 * y + x]
            if empty_count > 0:
                fen += f"{empty_count}"
            fen += '/'
        return fen

    def load_from_fen(self, fen):
        rows = fen.split('/')
        squares = []
        for row in rows:
            for char in row:
                if '1' <= char <= '8':
                    for _ in range(int(char)):
                        squares.append(None)
                else:
                    squares.append(char)
        assert(len(squares) == 64)
        self.squares = squares

    def piece_at(self, square: Square):
        coords = square.to_coords()
        index = coords[1] * 8 + coords[0]
        return self.squares[index]

    def check_check(self):
        white_threats = set()
        black_threats = set()
        white_sq = None
        black_sq = None
        for file in range(1, 9):
            for rank in range(1, 9):
                square = Square(file, rank)
                piece = self.piece_at(square)
                if not piece:
                    continue
                if piece == "K":
                    white_sq = square
                if piece == "k":
                    black_sq = square
                colour = pieces.colour_of_piece(piece)
                piece_o = pieces.PIECES[piece]()
                threats = piece_o.threat_squares(self.squares, square)
                if colour == "w":
                    white_threats.update(threats)
                elif colour == "b":
                    black_threats.update(threats)
        if white_sq in black_threats:
            self.white_in_check = True
        if black_sq in white_threats:
            self.black_in_check = True


class Game:
    def __init__(self, fen=None):
        self.board = Board()
        self.on_move = "w"
        self.castles = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passent = None
        self.fifty_mr = 0
        self.full_move_count = 1
        if fen:
            board, on_move, castles, en_passent, fifty_mr, mc = fen.split(" ")
            self.board = Board(board)
            self.on_move = on_move
            for s in self.castles.keys():
                self.castles[s] = s in castles
            if en_passent != '-':
                ep_f, ep_r = string_to_coords(en_passent)
                self.en_passent = Square(ep_f, ep_r)
            self.fifty_mr = int(fifty_mr)
            self.full_move_count = int(mc)

    def move(self, move: Move):
        pass

    @property
    def in_check(self):
        if self.on_move == "w":
            return self.board.white_in_check
        else:
            return self.board.black_in_check
