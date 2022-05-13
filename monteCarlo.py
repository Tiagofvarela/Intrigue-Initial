#Structural basis for this program by Jeff Bradberry. https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/


from __future__ import division
import datetime
from math import sqrt, log
from random import choice
import time
from board import Board
from intrigue import Game
from intrigue_datatypes import Player_Colour
from player import Player, recursive_hash_object


class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        """Takes an instance of a Board and optionally some keyword arguments. 
        Initializes the list of game states and the statistics tables."""
        self.board:Board = board
        self.states = []
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves', 100)
        self.wins:dict[int,Game] = {}
        self.plays:dict[int,Game] = {}
        self.C = kwargs.get('C', 1.4)
        
        self.max_depth = 0

    def update(self, state):
        """Takes a game state, and appends it to the history."""
        self.states.append(state)

    def get_play(self):
        """Causes the AI to calculate the best move from the current game state and return it."""
        self.max_depth = 0
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])
        print("Round:",state.turn_counter)
        print("Legal moves available:",len(legal))

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation()
            games += 1
        
        moves_states = [(p, self.board.next_state(state, p)) for p in legal]
        file = open("search-log.txt","a")

        # Display the number of calls of `run_simulation` and the time elapsed.
        file.write("Plays simulated: "+str(games)+"\n")
        file.write("Time spent simulating plays: "+str(datetime.datetime.utcnow() - begin)+"\n")

        percent_wins, move = max( (self.wins.get((player, S), 0) / self.plays.get((player, S), 1), play) for play, S in moves_states)

        # Display the stats for each possible play.
        for x in sorted(
            ((100 * self.wins.get((player, S), 0) /
              self.plays.get((player, S), 1),
              self.wins.get((player, S), 0),
              self.plays.get((player, S), 0), p)
             for p, S in moves_states),
            reverse=True
        ):
            file.write("{3}: {0:.2f}% ({1} / {2})".format(*x)+"\n")
        file.write("Maximum depth searched: "+ str(self.max_depth)+"\n\n")
        file.close()

        return move

    def run_simulation(self):
        """Plays out a "random" game from the current position, then updates the statistics tables with the result."""

        visited_states = set()
        states_copy:list[Game] = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)

        #Generates all legal plays for current state and picks one to be next state.
        expand = True   #
        for move_counter in range(self.max_moves):
            # legal = self.board.legal_plays(states_copy)
            # moves_states = [(play, self.board.next_state(state, play)) for play in legal]

            # # If we have stats on all of the legal moves here, use them.
            # for play, S in moves_states:
            #     already_recorded = self.plays.get( (player, S) )
            #     if not already_recorded:
            #         break
            # if already_recorded:
            #     sum = 0
            #     for play, S in moves_states:
            #         sum += self.plays[(player, S)]
            #     log_total = log( sum )
            #     value, move, state = max( ((wins[(player, S)] / self.plays[(player, S)]) + self.C * sqrt(log_total / self.plays[(player, S)]), play, S)
            #         for play, S in moves_states)
            # else:
            #     # if not moves_states:
            #     #     print(state)
            #     # Otherwise, just make an arbitrary decision.
            #     move, state = choice(moves_states)

            move = self.board.get_random_legal_play(states_copy)
            state = self.board.next_state(state, move)

            states_copy.append(state)

            #player refers to person who made the move into state.
            if expand and (player, state) not in self.plays:
                expand = False
                self.plays[recursive_hash_object((player, state))] = 0
                self.wins[recursive_hash_object((player, state))] = 0
                #Logs the necessary depth to reach an unplayed move.
                if move_counter > self.max_depth:
                    self.max_depth = move_counter

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if winner < 0:  #Game hasn't finished.
                break

        for player, state in visited_states:
            if recursive_hash_object((player, state)) not in self.plays:
                # print("Not")
                continue
            # print("It is in self.plays:")
            self.plays[recursive_hash_object((player, state))] += 1
            # print(self.plays)
            if player == winner:
                self.wins[recursive_hash_object((player, state))] += 1

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


    print("Winner:",Player_Colour(board.winner(montecarlo.states)))
    toc = time.perf_counter()
    taken_minutes = (toc - tic)/60
    print("It has taken",taken_minutes,"minutes.")
    print(montecarlo.plays)

    


# run()