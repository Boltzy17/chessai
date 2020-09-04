from env import ChessEnvironment

buffer_max_length = 10000


class EvalAgent:
    def __init__(self):
        self.env = ChessEnvironment()

    def create_model(self):
        print(self.env.observation_spec)
        #model = tf.keras.Sequential()
        #model.add(tf.keras.Input(shape = self.env.observation_spec))
        #model.add(tf.keras.layers.Dense())


nn = EvalAgent()
nn.create_model()
