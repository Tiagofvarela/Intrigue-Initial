from board import Board
from intrigue import Game


class IntrigueAI():
    """Main class for intrigue AI agents. \n
    Receive an intrigue Board instance, and implement the get_play() and update(game_state) methods."""
    
    def __init__(self, board:Board):
        self.board:Board = board
        self.states:list[Game] = []

    def update(self, state:Game):
        """Takes a game state, and appends it to the history."""
        self.states.append(state)

    def get_play(self):
        """Returns a play for the current state. (Default: Random)"""
        return self.board.get_random_legal_play(self.states)
    
    def get_current_state(self):
        """Gets the last state in the state history."""
        return self.states[-1]