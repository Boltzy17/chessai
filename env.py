from game import Game


class Environment:
    def __init__(self):
        self.game = Game()
        self.move_list = []
        self.possible_moves = []

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
        if self.game.move(pos, new_pos, prom = prom):
            self.move_list.append(move)
        else:
            print("Invalid move")

    def get_possible_moves(self):
        self.possible_moves = []
        for piece in [obj for obj in self.game.squares.flatten() if obj]:
            for i in range(8):
                for j in range(8):
                    if piece.can_move((i, j)) and piece.get_colour() == self.game.on_move:
                        self.possible_moves.append((piece.get_pos(), (i, j)))

    def string_to_pos(self, square):
        print(square)
        x = ord(square[0]) - ord('a')
        y = int(square[1]) - 1
        return x, y

    def print_possible_moves(self):
        poss_moves = []
        for move in self.possible_moves:
            start = self.pos_to_string(move[0])
            end = self.pos_to_string(move[1])
            new_move = start + end
            poss_moves.append(new_move)
        print(poss_moves)

    def pos_to_string(self, square):
        x = chr(square[0] + ord('a'))
        y = square[1] + 1
        return str(x) + str(y)


env = Environment()
env.get_possible_moves()
env.print_possible_moves()
env.move("a2a4")
env.get_possible_moves()
env.print_possible_moves()

