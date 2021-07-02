from PIL import Image, ImageTk

import tkinter as tk
# import numpy as np

import random

from eventhandler import EventHandler
from env import ChessEnvironment


class ChessGUI:
    def __init__(self, x, y):
        self.board_size = min(x, y)
        self.piece_size = self.board_size // 8
        self.bg_image = Image.open("./resources/images/chessboard.png")
        self.og_pieces = self.load_piece_images()
        self.pieces = self.og_pieces
        self.board = self.bg_image.copy()
        self.play_board = self.board.copy()

        self.env = ChessEnvironment()

        self.root = tk.Tk(className="Chess")
        self.root.geometry("{}x{}".format(x, y))

        self.eh = EventHandler(self)
        self.root.bind("<Configure>", self.eh.on_configure)
        self.root.bind("<Return>", self.eh.on_confirm)

        self.tk_image = ImageTk.PhotoImage(self.play_board)
        self.board_label = tk.Label(self.root, image=self.tk_image)
        self.board_label.place(relx=0.05, rely=0.05)

        self.game_label = tk.Label(self.root, text="Game playing")
        self.game_label.place(relx=0.05, rely=0.96)

        self.move_var = tk.StringVar()
        self.move_var.set("")
        self.move_var.trace("w", self.eh.check_move)
        self.move_box = tk.Entry(self.root, textvariable=self.move_var)
        self.move_box.place(relx=0.15, rely=0.01)

        self.move_label = tk.Label(self.root, text="NOT a valid move")
        self.move_label.place(relx=0.25, rely=0.01)

        self.random_move_button = tk.Button(
            self.root, text="Random Move", command=self.eh.on_random_move
        )
        self.random_move_button.place(relx=0.35, rely=0.01)

        self.start_button = tk.Button(
            self.root, text="New Game", command=self.eh.on_start
        )
        self.start_button.place(relx=0.05, rely=0.01)

        self.root.mainloop()
        self.on_resize()

    def play_move(self):
        if not self.env.game_over:
            self.env.move(self.move_var.get())
            print(f"check = {self.env.game.in_check}")
            self.move_var.set("")
            self.game_label.configure(foreground="black", text="Game Playing")
            self.set_valid_move(False)
            self.after_move()
        else:
            self.game_label.configure(foreground="red")

    def get_game_result(self):
        res = self.env.result
        if res == 1:
            return "White won!"
        if res == -1:
            return "Black won!"
        if res == 0:
            return "It was a draw!"
        return "Unexpected result"

    def play_random_move(self):
        if len(self.env.possible_moves) > 0:
            rand = random.randint(0, len(self.env.possible_moves))
            self.env.move(self.env.possible_moves_str[rand])
            self.on_update()
        else:
            print("Game is over!")

    def after_move(self):
        if self.env.game_over:
            self.game_label.configure(text=f"Game Over! {self.get_game_result()}")
        print(self.env.possible_moves_str)
        self.on_update()

    def set_valid_move(self, b):
        if b:
            self.move_label.configure(text="Valid move")
        else:
            self.move_label.configure(text="Not a valid move")

    def on_resize(self):
        x, y = self.root.winfo_width(), self.root.winfo_height()
        self.board_size = min(x, y) - int(0.1 * min(x, y))
        self.piece_size = self.board_size // 8
        self.board = self.bg_image.resize((self.board_size, self.board_size))
        self.play_board = self.board.copy()
        new_pieces = {}
        for pie in self.og_pieces:
            new_pieces[pie] = self.og_pieces[pie].resize(
                (self.piece_size, self.piece_size)
            )
        self.pieces = new_pieces
        self.on_update()

    def on_update(self):
        self.load_board(self.env.game.board.fen())
        self.tk_image = ImageTk.PhotoImage(self.play_board)
        self.board_label.configure(image=self.tk_image)

    def load_board(self, fen):
        self.play_board = self.board.copy()
        rows = fen.split("/")
        ycount = 0
        for row in rows:
            xcount = 0
            for char in list(row):
                if "1" <= char <= "8":
                    for _ in range(int(char)):
                        xcount += 1
                else:
                    xoff, yoff = (
                        xcount * self.piece_size,
                        self.board_size - ((ycount + 1) * self.piece_size),
                    )
                    self.play_board.paste(
                        self.pieces[char], (xoff, yoff), self.pieces[char]
                    )  # 2nd one is mask (alpha)
                    xcount += 1
            ycount += 1

    def load_piece_images(self):
        pieces = {
            "P": Image.open("./resources/images/pawn.png"),
            "N": Image.open("./resources/images/knight.png"),
            "B": Image.open("./resources/images/bishop.png"),
            "R": Image.open("./resources/images/rook.png"),
            "Q": Image.open("./resources/images/queen.png"),
            "K": Image.open("./resources/images/king.png"),
            "p": Image.open("./resources/images/pawnb.png"),
            "n": Image.open("./resources/images/knightb.png"),
            "b": Image.open("./resources/images/bishopb.png"),
            "r": Image.open("./resources/images/rookb.png"),
            "q": Image.open("./resources/images/queenb.png"),
            "k": Image.open("./resources/images/kingb.png"),
            "E": Image.open("./resources/images/EP.png"),
        }
        return pieces


if __name__ == "__main__":
    cg = ChessGUI(1200, 800)
