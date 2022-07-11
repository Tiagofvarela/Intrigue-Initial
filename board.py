#Structural basis for this program by Jeff Bradberry. https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

#State: Represents boards, pieces, players and their money.
#Player Number: 0,1,2,3

import sys

from game import Game
from player import ApplicationLog, ConflictLog, PlacementLog, EarningsLog

GameMove = tuple[EarningsLog, ConflictLog, PlacementLog, ApplicationLog]

class Board(object):
    calls:int

    def start(self):
        """Returns a representation of the starting state of the game."""
        game = Game()
        return game

    def current_player(self, state:Game):
        """Takes the game state and returns the current player's number."""
        return state.get_player_turn()

    def next_state(self, state:Game, play:GameMove):
        """Takes the game state, and the move to be applied.
        Returns the new game state."""
        return state.get_next_state(play)

    def legal_plays(self, state_history:list[Game], decide_bribe) -> list[GameMove]:
        """Takes a sequence of game states representing the full game history, 
        and returns the full list of moves that are legal plays for the current player."""
        plays = state_history[-1].get_legal_moves(decide_bribe)
        return plays

    def get_random_legal_play(self, state_history:list[Game], decide_bribe) -> GameMove:
        """Takes a sequence of game states representing the full game history, 
        and returns a random legal play for the current player."""
        play = state_history[-1].get_random_legal_move(decide_bribe)
        return play

    def winner(self, state_history:list[Game]):
        """Takes a sequence of game states representing the full game history.  
        If the game is now won, return the player number.  
        If the game is still ongoing, return -1.
        If the game is tied, return a different distinct value, e.g. PLAYER_COUNT+1."""
        return state_history[-1].get_winner()