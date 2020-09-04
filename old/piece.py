import abc


class Piece(abc.ABC):
    def __init__(self, board, colour, pos):
        self.pos = pos
        self.board = board
        self.colour = colour
        self.moved = False

    def set_moved(self):
        self.moved = True

    def set_pos(self, new_pos):
        self.pos = new_pos

    def get_pos(self):
        return self.pos

    def get_colour(self):
        return self.colour

    @property
    def colour_str(self):
        if self.colour == 1:
            return "w"
        return "b"

    @abc.abstractmethod
    def value(self) -> int:
        pass

    @abc.abstractmethod
    def type(self) -> str:
        pass

    @abc.abstractmethod
    def can_move(self, new_pos) -> bool:
        pass


class Pawn(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # if the distance is too far or too short
        if abs(nx - x) > 1 or abs(ny - y) > 2 or ny == y:
            return False
        # pawn tries to move in the wrong direction
        if (ny - y < 0) != (self.colour < 0) or (ny - y > 0) != (self.colour > 0):
            return False
        # if pawn tries to capture
        if x != nx:
            if ny == y + self.colour:
                # is there a piece to capture
                if self.board.en_passent == new_pos:
                    return True
                if self.board.squares[nx][ny]:
                    # check if own piece
                    return self.board.squares[nx][ny].get_colour() != self.colour
            return False
        if abs(ny - y) == 2:
            # check whether a piece is already in the new position or the square you skip
            if y == 1 or y == 6:
                return not (
                    self.board.squares[nx][ny]
                    or self.board.squares[nx][ny - self.colour]
                )
            else:
                return False
        # check whether a piece is already in the new position
        return not self.board.squares[nx][ny]

    @property
    def value(self):
        return self.colour * 1

    @property
    def type(self):
        return "p"


class Knight(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        if abs(nx - x) > 2 or abs(ny - y) > 2:
            return False
        # is there an L shape
        if (abs(nx - x) == 2 and abs(ny - y) == 1) or (
            abs(nx - x) == 1 and abs(ny - y) == 2
        ):
            # check whether a piece is already in the new position
            if self.board.squares[nx][ny]:
                return self.board.squares[nx][ny].get_colour() != self.colour
            return True

    @property
    def value(self):
        return self.colour * 3

    @property
    def type(self):
        return "n"


class Bishop(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # if not equal amount of squares horizontal as vertical then not diagonal movement = illegal!
        if not abs(nx - x) == abs(ny - y):
            return False
        # check if same square (if x == nx then y == ny because of above)
        if nx == x:
            return False
        # check directions
        if nx > x:
            dx = 1
        else:
            dx = -1
        if ny > y:
            dy = 1
        else:
            dy = -1
        # check in-between squares
        for i in range(1, abs(nx - x)):
            if self.board.squares[x + dx * i][y + dy * i]:
                return False
        # check whether a piece is already in the new position
        if self.board.squares[nx][ny]:
            return self.board.squares[nx][ny].get_colour() != self.colour
        return True

    @property
    def value(self):
        return self.colour * 3

    @property
    def type(self):
        return "b"


class Rook(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # if not purely horizontal or vertical movement
        if not (nx == x or ny == y):
            return False
        # check if the same square
        if nx == x and ny == y:
            return False
        if nx == x:
            dx = 0
            if ny > y:
                dy = 1
            else:
                dy = -1
        else:
            dy = 0
            if nx > x:
                dx = 1
            else:
                dx = -1
        # check in-between squares
        for i in range(1, max(abs(ny - y), abs(nx - x))):
            if self.board.squares[x + dx * i][y + dy * i]:
                return False
        # check whether a piece is already in the new position
        if self.board.squares[nx][ny]:
            return self.board.squares[nx][ny].get_colour() != self.colour
        return True

    @property
    def value(self):
        return self.colour * 5

    @property
    def type(self):
        return "r"


class Queen(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # check bishop or rook moves
        if not (abs(nx - x) == abs(ny - y) or (nx == x or ny == y)):
            return False
        # check if same square
        if nx == x and ny == y:
            return False
        if nx > x:
            dx = 1
        elif nx < x:
            dx = -1
        else:
            dx = 0
        if ny > y:
            dy = 1
        elif ny < y:
            dy = -1
        else:
            dy = 0
        # check in-between squares
        for i in range(1, max(abs(ny - y), abs(nx - x))):
            if self.board.squares[x + dx * i][y + dy * i]:
                return False
        # check whether a piece is already in the new position
        if self.board.squares[nx][ny]:
            return self.board.squares[nx][ny].get_colour() != self.colour
        return True

    @property
    def value(self):
        return self.colour * 9

    @property
    def type(self):
        return "q"


class King(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # check distance
        if abs(ny - y) > 1 or abs(nx - x) > 2:
            return False
        if abs(nx - x) == 2:
            if ny == y:
                if self.moved or self.board.in_check:
                    return False
                else:
                    if nx > x:
                        for piece in [
                            obj for obj in self.board.squares.flatten() if obj
                        ]:
                            if piece.get_colour() != self.colour and (
                                piece.can_move((5, y)) or piece.can_move((nx, ny))
                            ):
                                return False
                        if not self.board.squares[5][y] and self.board.squares[7][y]:
                            if self.board.squares[6][y]:
                                if self.board.squares[nx][ny]:
                                    return False
                                else:
                                    return not self.board.squares[7][y].moved
                            return not self.board.squares[7][y].moved
                        else:
                            return False
                    else:
                        for piece in [
                            obj for obj in self.board.squares.flatten() if obj
                        ]:
                            if piece.get_colour() != self.colour and (
                                piece.can_move((5, y)) or piece.can_move((nx, ny))
                            ):
                                return False
                        if not self.board.squares[3][y] and not self.board.squares[1][y] and self.board.squares[0][y]:
                            if self.board.squares[nx][y]:
                                return False
                            return not self.board.squares[0][y].moved
                        else:
                            return False
            else:
                return False

        # check if same square
        if nx == x and ny == y:
            return False
        # check whether a piece is already in the new position
        if self.board.squares[nx][ny]:
            return self.board.squares[nx][ny].get_colour() != self.colour
        return True

    @property
    def value(self):
        return 0

    @property
    def type(self):
        return "k"
