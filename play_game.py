from __future__ import division
from math import sqrt, log
from random import choice
import time
from board import Board
from intrigue_datatypes import PLAYER_COUNT, Player_Colour
from monteCarlo import MonteCarlo

def run():
    #Set up game board.
    board = Board()
    #Parameters
    args = {'time':1,'max_moves':120,'C':1.3}
    #Set up montecarlo.
    open('search-log.txt', 'w').close()
    montecarlo = MonteCarlo(board, **args)
    montecarlo.update(board.start())

    tic = time.perf_counter()
    #Play game to completion for all players.
    while board.winner(montecarlo.states) == -1:
        best_move = montecarlo.get_play()
        next_state = board.next_state(montecarlo.states[-1], best_move)
        print(next_state)
        montecarlo.update( next_state )

    if board.winner(montecarlo.states) >= PLAYER_COUNT:
        print("The game was a tie.")#TODO: Establish who is tieing.
    else:
        print("Winner:",Player_Colour(board.winner(montecarlo.states)).name)
    toc = time.perf_counter()
    taken_minutes = (toc - tic)/60
    print("It has taken",taken_minutes,"minutes.")
    print(montecarlo.plays)

run()