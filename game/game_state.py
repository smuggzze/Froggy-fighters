# game/game_state.py
class GameState:
    def __init__(self):
        self.winner_name = None

    def set_winner(self, name):
        self.winner_name = name

    def is_game_over(self):
        return self.winner_name is not None

    def reset(self):
        self.winner_name = None
