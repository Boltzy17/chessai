import numpy as np
from piece import Pawn, Knight, Bishop, Rook, Queen, King


# White = 1, Black = -1
class Game:
    def __init__(self):
        self.squares = np.empty((8, 8), dtype=object)
        self.in_check = False
        self.en_passent = None
        self.on_move = 1
        self.reset_board()

    def reset_board(self):
        # empty the board
        self.on_move = 1
        self.squares = np.empty((8, 8), dtype=object)

        # create all pawns
        for i in range(8):
            self.squares[i][1] = Pawn(self, 1, (i, 1))
            self.squares[i][6] = Pawn(self, -1, (i, 6))

        # white pieces
        self.squares[0][0] = Rook(self, 1, (0, 0))
        self.squares[7][0] = Rook(self, 1, (7, 0))
        self.squares[1][0] = Knight(self, 1, (1, 0))
        self.squares[6][0] = Knight(self, 1, (6, 0))
        self.squares[2][0] = Bishop(self, 1, (2, 0))
        self.squares[5][0] = Bishop(self, 1, (5, 0))
        self.squares[3][0] = Queen(self, 1, (3, 0))
        self.squares[4][0] = King(self, 1, (4, 0))

        # black pieces
        self.squares[0][7] = Rook(self, -1, (0, 7))
        self.squares[7][7] = Rook(self, -1, (7, 7))
        self.squares[1][7] = Knight(self, -1, (1, 7))
        self.squares[6][7] = Knight(self, -1, (6, 7))
        self.squares[2][7] = Bishop(self, -1, (2, 7))
        self.squares[5][7] = Bishop(self, -1, (5, 7))
        self.squares[3][7] = Queen(self, -1, (3, 7))
        self.squares[4][7] = King(self, -1, (4, 7))

    def move(self, pos, new_pos, prom = None):
        x, y = pos
        pawn = isinstance(self.squares[x][y], Pawn)
        if prom:
            if new_pos[1] != 7 or not pawn:
                print("Cannot promote piece!")
                return False
        else:
            if pawn and new_pos[1] == 7:
                prom = "q"
        if self.squares[x][y]:
            if self.squares[x][y].get_colour() == self.on_move:
                if self.squares[x][y].can_move(new_pos):
                    nx, ny = new_pos
                    copy = self.squares.copy()
                    # en passent rules
                    if pawn and self.en_passent == new_pos:
                        # take the pawn
                        copy[nx][ny - copy[x][y].get_colour()] = None
                    # move the piece
                    copy[nx][ny] = copy[x][y]
                    copy[nx][ny].set_pos(new_pos)
                    copy[x][y] = None
                    if self.check_safe_king(copy):
                        # en passent rules
                        if pawn and self.en_passent == new_pos:
                            # take the pawn
                            self.squares[nx][ny - self.squares[x][y].get_colour()] = None
                        if pawn and abs(ny - y) == 2:
                            self.en_passent = (x, ny - self.squares[x][y].get_colour())
                        else:
                            self.en_passent = None
                        # move the piece
                        if prom:
                            self.squares[nx][ny] = self.get_prom_piece(prom, new_pos)
                        else:
                            self.squares[nx][ny] = self.squares[x][y]
                        self.squares[nx][ny].set_pos(new_pos)
                        self.squares[nx][ny].set_moved()
                        self.squares[x][y] = None
                        self.on_move *= -1
                        print(f"Move succesful! piece {self.squares[nx][ny]}")
                        self.after_move()
                        return True
                    else:
                        print("You are in check!")
                else:
                    print("Could not move there")
            else:
                print("Not your move!")
        else:
            print("No piece on starting square")
        return False

    def check_safe_king(self, board):
        for piece in [obj for obj in board.flatten() if obj]:
            if isinstance(piece, King) and piece.get_colour() == self.on_move:
                for piece_2 in [obj for obj in board.flatten() if obj]:
                    if (
                        piece_2.can_move(piece.get_pos())
                        and piece_2.get_colour() != self.on_move
                    ):
                        return False
        return True

    def after_move(self):
        self.in_check = False
        # check for check
        for piece in [obj for obj in self.squares.flatten() if obj]:
            if isinstance(piece, King) and piece.get_colour() != self.on_move:
                for piece_2 in [obj for obj in self.squares.flatten() if obj]:
                    if (
                        piece_2.can_move(piece.get_pos())
                        and piece_2.get_colour() == self.on_move
                    ):
                        self.in_check = True

    def get_prom_piece(self, piece, pos):
        if piece == "q":
            return Queen(self, self.on_move, pos)
        if piece == "r":
            return Rook(self, self.on_move, pos)
        if piece == "b":
            return Bishop(self, self.on_move, pos)
        if piece == "n":
            return Knight(self, self.on_move, pos)
