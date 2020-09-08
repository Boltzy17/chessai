import chess


class ChessEnvironment:
    def __init__(self):
        self.game = chess.Game()
        self.move_list = []
        self.possible_moves = []  # Move objects
        self.reset()

    def reset(self):
        self.game = chess.Game()
        self.get_possible_moves()

    def load_from_fen(self, fen):
        self.game = chess.Game(fen = fen)

    def move(self, move: str):
        if not self.game_over:
            if not (3 < len(move) < 6):
                print("Invalid format")
            pos = chess.string_to_coords(move[:2])
            start = chess.Square(pos[0], pos[1])
            new_pos = chess.string_to_coords(move[2:4])
            end = chess.Square(new_pos[0], new_pos[1])
            prom = None
            if len(move) == 5:
                prom = move[4]
            move_o = chess.Move(start, end, prom=prom)
            if move_o in self.possible_moves:
                self.game = self.game.move(move_o)
                self.move_list.append(move)
                self.after_move()
                return True
        return False

    def get_possible_moves(self):
        self.possible_moves = [*self.game.generate_moves(),]

    def pos_to_string(self, square):
        x = chr(square[0] + ord("a"))
        y = square[1] + 1
        return str(x) + str(y)

    def after_move(self):
        self.get_possible_moves()

    @property
    def possible_moves_str(self):
        poss_moves = []
        for move in self.possible_moves:
            poss_moves.append(str(move))
        return poss_moves

    @property
    def game_over(self):
        return self.game.game_over

    @property
    def result(self):
        return 1

    # NN stuff
    @property
    def observation_spec(self):
        return (64,)

