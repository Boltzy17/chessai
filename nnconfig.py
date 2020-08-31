from env import Environment
import numpy as np

buffer_max_length = 10000


class NNConfig:
    def __init__(self):
        self.buffer = np.empty(buffer_max_length, dtype = object)
        self.env = Environment()
        self.env.get_possible_moves()
        self.env.print_possible_moves()
        self.env.move("a2a4")
        self.env.get_possible_moves()
        self.env.print_possible_moves()
