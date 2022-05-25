from board import Board
from game import Game
from intrigue_datatypes import Player_Colour
from piece import Piece
from player import Application


class IntrigueAI():
    """Main class for intrigue AI agents. \n
    Receive an intrigue Board instance, and implement the get_play() and update(game_state) methods."""
    
    def __init__(self, board:Board):
        self.board:Board = board
        self.states:list[Game] = []
        self.filename = ""

    def update(self, state:Game):
        """Takes a game state, and appends it to the history. \nUpdates log accordingly."""
        self.states.append(state)
        # file = open(self.filename,"a")
        # file.write(repr(self.states[-1])+"\n")
        # file.close()

    def get_play(self):
        """Returns a play for the current state. (Default: Random)\nUpdates log accordingly."""
        file = open(self.filename,"a")
        file.write(repr(self.states[-1])+"\n")
        chosen_play = self.board.get_random_legal_play(self.states)
        log_info = "Round:"+str(self.states[-1].turn_counter+1)+" "+Player_Colour(self.states[-1].get_player_turn()).clean_name()+" Turn\n"+"Random play chosen: \n"+repr(chosen_play)+"\n"
        print(log_info)
        file.write(log_info)
        file.close()
        return chosen_play
    
    def get_current_state(self):
        """Gets the last state in the state history."""
        return self.states[-1]