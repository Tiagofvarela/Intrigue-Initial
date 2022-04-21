#Structural basis for this program by Jeff Bradberry. https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

#State: Represents boards, pieces, players and their money.
#Player Number: 1,2,3,4

import sys

from intrigue import Game
from player import ApplicationLog, ConflictLog, PlacementLog, EarningsLog

GameMove = tuple[EarningsLog, ConflictLog, PlacementLog, ApplicationLog]

class Board(object):
    calls:int

    def start(self):
        """Returns a representation of the starting state of the game."""
        game = Game()
        # self.calls = 0
        return game

    def current_player(self, state:Game):
        """Takes the game state and returns the current player's number."""
        # print(state)
        return state.get_player_turn()

    def next_state(self, state:Game, play:GameMove):
        """Takes the game state, and the move to be applied.
        Returns the new game state."""
        return state.get_next_state(play)

    def legal_plays(self, state_history:list[Game]) -> list[GameMove]:
        """Takes a sequence of game states representing the full game history, 
        and returns the full list of moves that are legal plays for the current player."""
        plays = state_history[-1].get_legal_moves()
        return plays

    def winner(self, state_history:list[Game]):
        """Takes a sequence of game states representing the full game history.  
        If the game is now won, return the player number.  
        If the game is still ongoing, return -1.
        If the game is tied, return a different distinct value, e.g. PLAYER_COUNT+1."""
        return state_history[-1].get_winner()