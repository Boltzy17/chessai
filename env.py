from board import Board


class ChessEnvironment:
    def __init__(self):
        super().__init__()
        self.game = Board()
        self.move_list = []
        self.possible_moves = []  # in the form pos, new_pos, prom

    def new_game(self):
        self.game.reset_board()

    def move(self, move: str):
        if not (3 < len(move) < 6):
            print("Invalid format")
        pos = self.string_to_pos(move[:2])
        new_pos = self.string_to_pos(move[2:4])
        prom = None
        if len(move) == 5:
            prom = move[4]
        if self.game.move(pos, new_pos, prom=prom):
            self.move_list.append(move)
            return True
        else:
            print("Invalid move")
            return False

    def get_possible_moves(self):
        self.possible_moves = []
        for piece in [obj for obj in self.game.get_board().flatten() if obj]:
            for i in range(8):
                for j in range(8):
                    if (
                        piece.can_move((i, j))
                        and piece.get_colour() == self.game.on_move
                    ):
                        if piece.type == "p" and j == 7:
                            self.possible_moves.append((piece.get_pos(), (i, j), "q"))
                            self.possible_moves.append((piece.get_pos(), (i, j), "r"))
                            self.possible_moves.append((piece.get_pos(), (i, j), "b"))
                            self.possible_moves.append((piece.get_pos(), (i, j), "n"))
                        else:
                            self.possible_moves.append((piece.get_pos(), (i, j), ""))

    def string_to_pos(self, square):
        x = ord(square[0]) - ord("a")
        y = int(square[1]) - 1
        return x, y

    def print_possible_moves(self):
        poss_moves = []
        for move in self.possible_moves:
            start = self.pos_to_string(move[0])
            end = self.pos_to_string(move[1])
            prom = move[2]
            new_move = start + end + prom
            poss_moves.append(new_move)
        print(poss_moves)

    def pos_to_string(self, square):
        x = chr(square[0] + ord("a"))
        y = square[1] + 1
        return str(x) + str(y)

    # ****GUI****

    def show_env(self):
        pass

    # *********** NN functions ************
