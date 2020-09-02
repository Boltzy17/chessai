max_resize_cd = 3


class EventHandler:
    def __init__(self, gui):
        self.gui = gui

        self.resize_cd = max_resize_cd - 1

    def on_confirm(self, *event):
        self.gui.play_move()

    def on_configure(self, *event):
        if self.gui.root.winfo_exists():
            self.resize_cd = (self.resize_cd + 1) % max_resize_cd
            if self.resize_cd == 0:
                self.gui.on_resize()

    def on_click(self, event):
        pass

    def check_move(self, *event):
        if self.gui.move_var.get() in self.gui.game.possible_moves_str:
            print("valid")
            self.gui.set_valid_move(True)
        else:
            self.gui.set_valid_move(False)

    def on_random_move(self, *event):
        self.gui.play_random_move()

    def on_start(self, *event):
        self.gui.game.reset()
        self.gui.on_update()
