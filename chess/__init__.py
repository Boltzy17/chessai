import chess.pieces
import copy


class InvalidSquareException(Exception):
    """Created when trying to make an illegal square"""

    pass


class InvalidEnPassentException(Exception):
    """ Created when trying to take en passent but on an illegal rank"""

    pass


class InvalidCastleException(Exception):
    """ Created when trying to castle but to an illegal file"""

    pass


def string_to_coords(data: str):
    if len(data) != 2:
        raise InvalidSquareException(f"{data} is not a valid square")
    file = ord(data[0]) - ord("a") + 1
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

    def to_index(self):
        return (self.rank - 1) * 8 + (self.file - 1)

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
        s = f"{self.start}{self.end}"
        if self.prom:
            s += f"{self.prom}"
        return s

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
    def __init__(self, squares=None, fen=None):
        self.squares = [None for _ in range(64)]
        if squares:
            assert len(squares) == 64
            self.squares = squares
        elif fen:
            self.load_from_fen(fen)
        else:
            self.squares[0:8] = "RNBQKBNR"
            self.squares[8:16] = "P" * 8
            self.squares[48:56] = "p" * 8
            self.squares[56:64] = "rnbqkbnr"
        self.white_in_check = False
        self.black_in_check = False

    def fen(self):
        fen = ""
        for y in range(8):
            empty_count = 0
            for x in range(8):
                if self.squares[8 * y + x] is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += f"{empty_count}"
                        empty_count = 0
                    fen += self.squares[8 * y + x]
            if empty_count > 0:
                fen += f"{empty_count}"
            fen += "/"
        return fen

    def load_from_fen(self, fen):
        rows = fen.split("/")
        squares = []
        for row in rows:
            for char in row:
                if "1" <= char <= "8":
                    for _ in range(int(char)):
                        squares.append(None)
                else:
                    squares.append(char)
        assert len(squares) == 64
        self.squares = squares

    def piece_at(self, square: Square):
        if self.squares[square.to_index()]:
            return self.squares[square.to_index()]
        else:
            return None

    def threats(self, col):
        threats = set()
        for file in range(1, 9):
            for rank in range(1, 9):
                square = Square(file, rank)
                piece = self.piece_at(square)
                if piece is None:
                    continue
                if col != pieces.colour_of_piece(piece):
                    continue
                piece_o = pieces.PIECES[piece]()
                threats.update(piece_o.threat_squares(self, square))
        return threats

    def check_check(self):
        self.white_in_check = False
        self.black_in_check = False
        white_threats = set()
        black_threats = set()
        white_sq = None
        black_sq = None
        for file in range(1, 9):
            for rank in range(1, 9):
                square = Square(file, rank)
                piece = self.piece_at(square)
                if piece is None:
                    continue
                if piece == "K":
                    white_sq = square
                if piece == "k":
                    black_sq = square
                colour = pieces.colour_of_piece(piece)
                piece_o = pieces.PIECES[piece]()
                threats = piece_o.threat_squares(self, square)
                if colour == 1:
                    white_threats.update(threats)
                else:
                    black_threats.update(threats)
        if white_sq in black_threats:
            self.white_in_check = True
        if black_sq in white_threats:
            self.black_in_check = True

    def board_after_move(self, move, en_passent):
        new_board_squares = copy.deepcopy(self.squares)
        start_i = move.start.to_index()
        end_i = move.end.to_index()
        if move.prom:
            piece = move.prom
        else:
            piece = new_board_squares[start_i]
        new_board_squares[end_i] = piece
        new_board_squares[start_i] = None

        # Castle rules
        if piece == "k" or piece == "K":
            if abs(move.end.file - move.start.file) == 2:
                if move.end.rank == 8:
                    if move.end.file == 3:
                        rook_start = Square(1, 8).to_index()
                        rook_end = Square(4, 8).to_index()
                    elif move.end.file == 7:
                        rook_start = Square(8, 8).to_index()
                        rook_end = Square(6, 8).to_index()
                    else:
                        raise InvalidCastleException("You cannot castle there!")
                elif move.end.rank == 1:
                    if move.end.file == 3:
                        rook_start = Square(1, 1).to_index()
                        rook_end = Square(4, 1).to_index()
                    elif move.end.file == 7:
                        rook_start = Square(8, 1).to_index()
                        rook_end = Square(6, 1).to_index()
                    else:
                        raise InvalidCastleException("You cannot castle there!")
                else:
                    raise InvalidCastleException("You cannot castle there!")
                r = new_board_squares[rook_start]
                new_board_squares[rook_end] = r
                new_board_squares[rook_start] = None

        # En passent rules
        if move.end == en_passent:
            if en_passent.rank == 3:
                # take the pawn (black takes ep)
                taken_i = Square(move.end.file, 3).to_index()
            elif en_passent.rank == 6:
                # take the pawn (white takes ep)
                taken_i = Square(move.end.file, 6).to_index()
            else:
                raise InvalidEnPassentException()
            new_board_squares[taken_i] = None
        new_board = Board(squares=new_board_squares)
        new_board.check_check()
        return new_board


class Game:
    def __init__(self, fen=None):
        self.board = Board()
        self.on_move = 1
        self.castles = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passent = None
        self.fifty_mr = 0
        self.full_move_count = 1
        if fen:
            board, on_move, castles, en_passent, fifty_mr, mc = fen.split(" ")
            self.board = Board(fen=board)
            self.on_move = on_move
            for s in self.castles.keys():
                self.castles[s] = s in castles
            if en_passent != "-":
                ep_f, ep_r = string_to_coords(en_passent)
                self.en_passent = Square(ep_f, ep_r)
            self.fifty_mr = int(fifty_mr)
            self.full_move_count = int(mc)

    def fen(self):
        ep_str = self.en_passent or "-"
        castles_str = ""
        for s, v in self.castles.items():
            if v:
                castles_str += s
        if len(castles_str) < 1:
            castles_str = "-"
        return f"{self.board.fen()} {self.on_move} {castles_str} {ep_str} {self.fifty_mr} {self.full_move_count}"

    def legal_moves(self, piece, start):
        piece_o = pieces.PIECES[piece]()
        ends = set()
        p_ends = piece_o.move_squares(self.board, start)
        p_threat_ends = piece_o.threat_squares(self.board, start)
        ends.update(p_ends)
        for end in p_threat_ends - p_ends:
            if self.board.piece_at(end) is not None:
                ends.add(end)
            if self.en_passent == end:
                if piece == "p" or piece == "P":
                    ends.add(end)
        other_colour = piece_o.colour * -1
        other_threats = self.board.threats(other_colour)
        if (piece == "k" and not self.board.black_in_check) or (
            piece == "K" and not self.board.black_in_check
        ):

            def can_castle_through_square(square):
                return (
                    self.board.piece_at(square) is None and square not in other_threats
                )

            if piece == "K":
                if self.castles["K"]:
                    if (
                        can_castle_through_square(Square(3, 1))
                        and can_castle_through_square(Square(4, 1))
                        and self.board.piece_at(Square(2, 1)) is None
                    ):
                        ends.add(Square(3, 1))
                if self.castles["Q"]:
                    if can_castle_through_square(
                        Square(6, 1)
                    ) and can_castle_through_square(Square(7, 1)):
                        ends.add(Square(7, 1))
            if piece == "k":
                if self.castles["k"]:
                    if (
                        can_castle_through_square(Square(3, 8))
                        and can_castle_through_square(Square(4, 8))
                        and self.board.piece_at(Square(2, 8)) is None
                    ):
                        ends.add(Square(3, 8))
                if self.castles["q"]:
                    if can_castle_through_square(
                        Square(6, 8)
                    ) and can_castle_through_square(Square(7, 8)):
                        ends.add(Square(7, 8))

        if piece_o.colour == 1:
            move_boards = zip(
                [Move(start, end) for end in ends],
                [
                    self.board.board_after_move(
                        Move(start, end), self.en_passent
                    ).white_in_check
                    for end in ends
                ],
            )
        else:
            move_boards = zip(
                [Move(start, end) for end in ends],
                [
                    self.board.board_after_move(
                        Move(start, end), self.en_passent
                    ).black_in_check
                    for end in ends
                ],
            )
        mb_copy = copy.deepcopy(move_boards)
        for move_board in mb_copy:
            print(f"{move_board[0]}, {move_board[1]}")
        moves = set(
            [move_board[0] for move_board in move_boards if not move_board[1]]
        )
        return moves

    def generate_moves(self):
        moves = set()
        for i in range(len(self.board.squares)):
            x = (i % 8) + 1
            y = (i // 8) + 1
            start = Square(x, y)
            piece = self.board.piece_at(start)
            if piece is None:
                continue
            if pieces.PIECES[piece]().colour != self.on_move:
                continue
            moves.update(self.legal_moves(piece, start))
        return moves

    def move(self, move: Move):
        piece = self.board.piece_at(move.start)
        new_game = Game(self.fen())
        capture = False
        if new_game.board.piece_at(move.end):
            capture = True
        new_game.board = new_game.board.board_after_move(move, self.en_passent)
        new_game.board.check_check()

        # on_move changes and 50 mr
        new_game.on_move = self.on_move * -1
        if new_game.on_move == 1:
            new_game.full_move_count += 1
        new_game.en_passent = None
        if piece == "p" or piece == "P":
            new_game.fifty_mr = 0
            if move.end.rank - move.start.rank == 2:
                new_game.en_passent = move.start.delta(0, 1)
            elif move.end.rank - move.start.rank == -2:
                new_game.en_passent = move.start.delta(0, -1)
        elif capture:
            new_game.fifty_mr = 0
        else:
            new_game.fifty_mr += 1

        # update castle rights
        if piece == "r":
            if move.start.file == 1:
                new_game.castles["q"] = False
            elif move.start.file == 8:
                new_game.castles["k"] = False
        elif piece == "k":
            new_game.castles["q"] = False
            new_game.castles["k"] = False
        elif piece == "R":
            if move.start.file == 1:
                new_game.castles["Q"] = False
            elif move.start.file == 8:
                new_game.castles["K"] = False
        elif piece == "K":
            new_game.castles["Q"] = False
            new_game.castles["K"] = False

        return new_game

    @property
    def in_check(self):
        if self.on_move == 1:
            return self.board.white_in_check
        else:
            return self.board.black_in_check

    @property
    def game_over(self):
        return len(self.generate_moves()) < 1
