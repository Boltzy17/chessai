import chess.pieces

import copy
import numpy as np


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
        return hash((self.start, self.end, self.prom))

    @property
    def man_dist(self):
        return abs(self.start.file - self.end.file) + abs(
            self.start.rank + self.end.rank
        )


class Board:
    def __init__(self, squares=None, fen=None):
        self.squares = np.zeros((64), dtype=float)
        if squares is not None:
            assert len(squares) == 64
            self.squares = squares
        elif fen:
            self.load_from_fen(fen)
        else:
            self.default_board()
        self.white_in_check = False
        self.black_in_check = False

    def default_board(self):
        # pawns
        for i in range(8):
            # white
            self.squares[8 + i] = pieces.PIECES_FENS["P"]
            # black
            self.squares[6 * 8 + i] = pieces.PIECES_FENS["p"]
        # white pieces
        self.squares[0] = pieces.PIECES_FENS["R"]
        self.squares[1] = pieces.PIECES_FENS["N"]
        self.squares[2] = pieces.PIECES_FENS["B"]
        self.squares[3] = pieces.PIECES_FENS["Q"]
        self.squares[4] = pieces.PIECES_FENS["K"]
        self.squares[5] = pieces.PIECES_FENS["B"]
        self.squares[6] = pieces.PIECES_FENS["N"]
        self.squares[7] = pieces.PIECES_FENS["R"]
        # black pieces
        self.squares[56 + 0] = pieces.PIECES_FENS["r"]
        self.squares[56 + 1] = pieces.PIECES_FENS["n"]
        self.squares[56 + 2] = pieces.PIECES_FENS["b"]
        self.squares[56 + 3] = pieces.PIECES_FENS["q"]
        self.squares[56 + 4] = pieces.PIECES_FENS["k"]
        self.squares[56 + 5] = pieces.PIECES_FENS["b"]
        self.squares[56 + 6] = pieces.PIECES_FENS["n"]
        self.squares[56 + 7] = pieces.PIECES_FENS["r"]

    def fen(self):
        fen = ""
        for y in range(8):
            empty_count = 0
            for x in range(8):
                if self.squares[8 * y + x] == pieces.EMPTY_SQUARE:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += f"{empty_count}"
                        empty_count = 0
                    fen += pieces.PIECES[self.squares[8 * y + x]]().fen
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
                        squares.append(pieces.EMPTY_SQUARE)
                else:
                    squares.append(pieces.PIECES_FENS[char])
        assert len(squares) == 64
        self.squares = squares

    def piece_at(self, square: Square):
        return self.squares[square.to_index()]

    def set_en_passent(self, square: Square):
        self.squares[square.to_index()] = 7

    def remove_en_passent(self):
        for i in range(len(self.squares)):
            if self.squares[i] == 7:
                self.squares[i] = pieces.EMPTY_SQUARE

    def threats(self, col):
        threats = set()
        for file in range(1, 9):
            for rank in range(1, 9):
                square = Square(file, rank)
                piece = self.piece_at(square)
                if piece == pieces.EMPTY_SQUARE:
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
                if piece == pieces.EMPTY_SQUARE:
                    continue
                piece_o = pieces.PIECES[piece]()
                if isinstance(piece_o, pieces.WhiteKing):
                    white_sq = square
                if isinstance(piece_o, pieces.BlackKing):
                    black_sq = square
                colour = pieces.colour_of_piece(piece)
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
        new_board_squares[start_i] = pieces.EMPTY_SQUARE

        piece_o = pieces.PIECES[piece]()
        # Castle rules
        if isinstance(piece_o, pieces.King):
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
                new_board_squares[rook_start] = pieces.EMPTY_SQUARE

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
            new_board_squares[taken_i] = pieces.EMPTY_SQUARE
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
                self.board.set_en_passent(self.en_passent)
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
            if self.board.piece_at(end) != pieces.EMPTY_SQUARE:
                ends.add(end)
            if self.en_passent == end:
                if isinstance(piece_o, pieces.Pawn):
                    ends.add(end)
        other_colour = piece_o.colour * -1
        other_threats = self.board.threats(other_colour)
        if (
            isinstance(piece_o, pieces.BlackKing) and not self.board.black_in_check
        ) or (isinstance(piece_o, pieces.WhiteKing) and not self.board.white_in_check):

            def can_castle_through(square):
                return (
                    self.board.piece_at(square) is None and square not in other_threats
                )

            if isinstance(piece_o, pieces.WhiteKing):
                if self.castles["K"]:
                    if (
                        can_castle_through(Square(3, 1))
                        and can_castle_through(Square(4, 1))
                        and self.board.piece_at(Square(2, 1)) is None
                    ):
                        ends.add(Square(3, 1))
                if self.castles["Q"]:
                    if can_castle_through(Square(6, 1)) and can_castle_through(
                        Square(7, 1)
                    ):
                        ends.add(Square(7, 1))
            if isinstance(piece_o, pieces.BlackKing):
                if self.castles["k"]:
                    if (
                        can_castle_through(Square(3, 8))
                        and can_castle_through(Square(4, 8))
                        and self.board.piece_at(Square(2, 8)) is None
                    ):
                        ends.add(Square(3, 8))
                if self.castles["q"]:
                    if can_castle_through(Square(6, 8)) and can_castle_through(
                        Square(7, 8)
                    ):
                        ends.add(Square(7, 8))
        moves = []
        if piece_o.colour == 1:
            for end in ends:
                if isinstance(piece_o, pieces.WhitePawn) and end.rank == 8:
                    # Promotion to Queen
                    if not self.board.board_after_move(
                        Move(start, end, prom="Q"), self.en_passent
                    ).white_in_check:
                        moves.append(Move(start, end, prom="Q"))
                    # Promotion to rook
                    if not self.board.board_after_move(
                        Move(start, end, prom="R"), self.en_passent
                    ).white_in_check:
                        moves.append(Move(start, end, prom="R"))
                    # Promotion to Bishop
                    if not self.board.board_after_move(
                        Move(start, end, prom="B"), self.en_passent
                    ).white_in_check:
                        moves.append(Move(start, end, prom="B"))
                    # Promotion to knight
                    if not self.board.board_after_move(
                        Move(start, end, prom="N"), self.en_passent
                    ).white_in_check:
                        moves.append(Move(start, end, prom="N"))
                else:
                    if not self.board.board_after_move(
                        Move(start, end), self.en_passent
                    ).white_in_check:
                        moves.append(Move(start, end))
        else:
            for end in ends:
                if isinstance(piece_o, pieces.BlackPawn) and end.rank == 1:
                    # Promotion to Queen
                    if not self.board.board_after_move(
                        Move(start, end, prom="q"), self.en_passent
                    ).black_in_check:
                        moves.append(Move(start, end, prom="q"))
                    # Promotion to rook
                    if not self.board.board_after_move(
                        Move(start, end, prom="r"), self.en_passent
                    ).black_in_check:
                        moves.append(Move(start, end, prom="r"))
                    # Promotion to Bishop
                    if not self.board.board_after_move(
                        Move(start, end, prom="b"), self.en_passent
                    ).black_in_check:
                        moves.append(Move(start, end, prom="b"))
                    # Promotion to knight
                    if not self.board.board_after_move(
                        Move(start, end, prom="n"), self.en_passent
                    ).black_in_check:
                        moves.append(Move(start, end, prom="n"))
                else:
                    if not self.board.board_after_move(
                        Move(start, end), self.en_passent
                    ).black_in_check:
                        moves.append(Move(start, end))
        return moves

    def generate_moves(self):
        print(self.en_passent)
        moves = set()
        for i in range(len(self.board.squares)):
            x = (i % 8) + 1
            y = (i // 8) + 1
            start = Square(x, y)
            piece = self.board.piece_at(start)
            if piece == pieces.EMPTY_SQUARE:
                continue
            if pieces.PIECES[piece]().colour != self.on_move:
                continue
            moves.update(self.legal_moves(piece, start))
        return moves

    def move(self, move: Move):
        piece = self.board.piece_at(move.start)
        new_game = Game(self.fen())
        capture = False
        if new_game.board.piece_at(move.end) != pieces.EMPTY_SQUARE:
            capture = True
        new_game.board = new_game.board.board_after_move(move, self.en_passent)
        new_game.board.check_check()

        piece_o = pieces.PIECES[piece]()
        # on_move changes and 50 mr
        new_game.on_move = self.on_move * -1
        if new_game.on_move == 1:
            new_game.full_move_count += 1
        new_game.en_passent = None
        new_game.board.remove_en_passent()
        if isinstance(piece_o, pieces.Pawn):
            new_game.fifty_mr = 0
            if move.end.rank - move.start.rank == 2:
                new_game.en_passent = move.start.delta(0, 1)
                new_game.board.set_en_passent(new_game.en_passent)
            elif move.end.rank - move.start.rank == -2:
                new_game.en_passent = move.start.delta(0, -1)
                new_game.board.set_en_passent(new_game.en_passent)
        elif capture:
            new_game.fifty_mr = 0
        else:
            new_game.fifty_mr += 1

        # update castle rights
        if isinstance(piece_o, pieces.BlackRook):
            if move.start.file == 1:
                new_game.castles["q"] = False
            elif move.start.file == 8:
                new_game.castles["k"] = False
        elif isinstance(piece_o, pieces.BlackKing):
            new_game.castles["q"] = False
            new_game.castles["k"] = False
        elif isinstance(piece_o, pieces.WhiteRook):
            if move.start.file == 1:
                new_game.castles["Q"] = False
            elif move.start.file == 8:
                new_game.castles["K"] = False
        elif isinstance(piece_o, pieces.WhiteKing):
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
        return len(self.generate_moves()) < 1 or self.fifty_mr >= 50

    def result(self):
        if self.fifty_mr >= 50:
            return 0
        if len(self.generate_moves()) < 1:
            if self.on_move == 1:
                if self.board.black_in_check:
                    return 1
            else:
                if self.board.white_in_check:
                    return -1
            return 0
