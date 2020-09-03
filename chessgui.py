from PIL import Image, ImageTk

import tkinter as tk
import numpy as np

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

        self.game = ChessEnvironment()

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
        if not self.game.game_over:
            self.game.move(self.move_var.get())
            print(f"check = {self.game.board.in_check}")
            self.move_var.set("")
            self.set_valid_move(False)
            self.after_move()
        else:
            self.game_label.configure(text="Game Over!")

    def play_random_move(self):
        if not self.game.game_over:
            poss_moves = self.game.possible_moves_str
            rand = np.random.randint(len(poss_moves))
            print(f"selected move: {poss_moves[rand]}")
            self.game.move(poss_moves[rand])
            self.after_move()
        else:
            print("No Moves!")

    def after_move(self):
        if self.game.game_over:
            self.game_label.configure(text="Game Over!")
        print(self.game.possible_moves_str)
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
        self.load_board()
        self.tk_image = ImageTk.PhotoImage(self.play_board)
        self.board_label.configure(image=self.tk_image)

    def load_board(self):
        self.play_board = self.board.copy()
        for piece in [p for p in self.game.board.get_board().flatten() if p]:
            x, y = piece.get_pos()
            xoff, yoff = (
                x * self.piece_size,
                self.board_size - ((y + 1) * self.piece_size),
            )
            piece_str = piece.type + piece.colour_str
            self.play_board.paste(
                self.pieces[piece_str], (xoff, yoff), self.pieces[piece_str]
            )  # 2nd one is mask (alpha)

    def load_piece_images(self):
        pieces = {
            "pw": Image.open("./resources/images/pawn.png"),
            "nw": Image.open("./resources/images/knight.png"),
            "bw": Image.open("./resources/images/bishop.png"),
            "rw": Image.open("./resources/images/rook.png"),
            "qw": Image.open("./resources/images/queen.png"),
            "kw": Image.open("./resources/images/king.png"),
            "pb": Image.open("./resources/images/pawnb.png"),
            "nb": Image.open("./resources/images/knightb.png"),
            "bb": Image.open("./resources/images/bishopb.png"),
            "rb": Image.open("./resources/images/rookb.png"),
            "qb": Image.open("./resources/images/queenb.png"),
            "kb": Image.open("./resources/images/kingb.png"),
        }
        return pieces


cg = ChessGUI(1200, 800)
