# from env import ChessEnvironment

import tensorflow as tf
import numpy as np

buffer_max_length = 10000


class EvalAgent:
    def __init__(self):
        # self.env = ChessEnvironment()
        self.nn = None
        self.create_model()

    def create_model(self):
        inputs = tf.keras.Input(shape = (64,), dtype=float, name = "input")
        l1 = tf.keras.layers.Dense(64, input_shape=(64,), activation="sigmoid", dtype=float, name = "l1")(inputs)
        l2 = tf.keras.layers.Dense(32, input_shape=(64,), activation="sigmoid", dtype=float, name = "l2")(l1)
        l3 = tf.keras.layers.Dense(16, input_shape=(32,), activation="sigmoid", dtype=float, name = "l3")(l2)
        output = tf.keras.layers.Dense(1, input_shape=(16,), activation="sigmoid", dtype=float, name = "output")(l3)
        model = tf.keras.Model(inputs=inputs, outputs=output, name="eval_model")
        self.nn = model

    def eval(self, boards):
        dat = tf.convert_to_tensor(boards, dtype=float)
        return self.nn.predict(dat)

    def print_eval(self):
        pass


nn = EvalAgent()
nn.create_model()
nn.print_eval()
