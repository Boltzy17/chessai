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

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def can_move(self, new_pos) -> bool:
        pass


class Pawn(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"pawn_{col}"

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # if the distance is too far
        if abs(nx - x) > 1 or abs(ny - y) > 2 or abs(ny - y) < 1:
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
            if y == 1:
                # check whether a piece is already in the new position or the square you skip
                return not (
                    self.board.squares[nx][ny] or self.board.squares[nx][ny - 1]
                )
            if y == 6:
                # check whether a piece is already in the new position or the square you skip
                return not (
                    self.board.squares[nx][ny] or self.board.squares[nx][ny + 1]
                )
        # check whether a piece is already in the new position
        return not self.board.squares[nx][ny]


class Knight(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"knight_{col}"

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        if abs(nx - x) > 2 or abs(ny - y) > 2:
            return False
        # return whether there is an L shape
        if (abs(nx - x) == 2 and abs(ny - y) == 1) or (
            abs(nx - x) == 1 and abs(ny - y) == 2
        ):
            # check whether a piece is already in the new position
            if self.board.squares[nx][ny]:
                return self.board.squares[nx][ny].get_colour() != self.colour
            return True


class Bishop(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"bishop_{col}"

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


class Rook(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"rook_{col}"

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


class Queen(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"queen_{col}"

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


class King(Piece):
    def __init__(self, board, colour, pos):
        super().__init__(board, colour, pos)

    def __repr__(self):
        if self.colour == 1:
            col = "w"
        else:
            col = "b"
        return f"king_{col}"

    def can_move(self, new_pos):
        x, y = self.pos
        nx, ny = new_pos
        # check distance
        if abs(ny - y) > 1 or abs(nx - x) > 2:
            return False
        if abs(nx - x) == 2:
            if self.moved or self.board.in_check:
                return False
            else:
                if nx > x:
                    for piece in [obj for obj in self.board.squares.flatten() if obj]:
                        if piece.get_colour() != self.colour and (
                            piece.can_move((5, y)) or piece.can_move((nx, ny))
                        ):
                            return False
                    if not self.board.squares[5][y] and self.board.squares[7][y]:
                        if self.board.squares[6][y]:
                            return (
                                self.board.squares[nx][ny].get_colour() != self.colour
                                and not self.board.squares[7][y].moved
                            )
                        return not self.board.squares[7][y].moved
                    else:
                        return False
                else:
                    for piece in [obj for obj in self.board.squares.flatten() if obj]:
                        if piece.get_colour() != self.colour and (
                            piece.can_move((5, y)) or piece.can_move((nx, ny))
                        ):
                            return False
                    if not self.board.squares[3][y] and self.board.squares[0][y]:
                        if self.board.squares[2][y]:
                            return (
                                self.board.squares[nx][ny].get_colour() != self.colour
                                and not self.board.squares[0][y].moved
                            )
                        return not self.board.squares[0][y].moved
                    else:
                        return False

        # check if same square
        if nx == x and ny == y:
            return False
        # check whether a piece is already in the new position
        if self.board.squares[nx][ny]:
            return self.board.squares[nx][ny].get_colour() != self.colour
        return True
