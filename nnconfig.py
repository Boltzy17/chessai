from env import ChessEnvironment
import numpy as np

buffer_max_length = 10000


class NNConfig:
    def __init__(self):
        self.buffer = np.empty(buffer_max_length, dtype=object)

        self.env = ChessEnvironment()
        self.env.move("e2e4")
        self.env.move("e7e5")
        self.env.move("f1b5")
        self.env.move("f8c5")
        self.env.move("g1f3")
        self.env.move("g8f6")
        self.env.get_possible_moves()
        self.env.print_possible_moves()
        self.env.move("e1g1")
        print(self.env.board.get_board())
        self.env.get_possible_moves()
        self.env.print_possible_moves()
        self.env.move("e8g8")
        print(np.rot90(self.env.board.get_board()))


nn = NNConfig()
