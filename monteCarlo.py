from __future__ import division
import datetime
from math import sqrt, log
from random import choice
from board import Board
from intrigue import Game
from intrigue_datatypes import Player_Colour


class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        """Takes an instance of a Board and optionally some keyword arguments. 
        Initializes the list of game states and the statistics tables."""
        self.board:Board = board
        self.states = []
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves', 100)
        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 1.4)

    def update(self, state):
        """Takes a game state, and appends it to the history."""
        self.states.append(state)

    def get_play(self):
        """Causes the AI to calculate the best move from the current game state and return it."""
        self.max_depth = 0
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.__run_simulation()
            games += 1
        
        moves_states = [(p, self.board.next_state(state, p)) for p in legal]

        # Display the number of calls of `run_simulation` and the time elapsed.
        print(games)
        print(datetime.datetime.utcnow() - begin)

        percent_wins, move = max( (self.wins.get((player, S), 0) / self.plays.get((player, S), 1), play) for play, S in moves_states)

        # Display the stats for each possible play.
        # for x in sorted(
        #     ((100 * self.wins.get((player, S), 0) /
        #       self.plays.get((player, S), 1),
        #       self.wins.get((player, S), 0),
        #       self.plays.get((player, S), 0), p)
        #      for p, S in moves_states),
        #     reverse=True
        # ):
        #     print("{3}: {0:.2f}% ({1} / {2})".format(*x))
        # print("Maximum depth searched:", self.max_depth)

        return move

    def __run_simulation(self):
        """Plays out a "random" game from the current position, then updates the statistics tables with the result."""
        plays, wins = self.plays, self.wins #Optimisation for local access.

        visited_states = set()
        states_copy:list[Game] = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)

        #Generates all legal plays for current state and picks one to be next state.
        expand = True
        for t in range(self.max_moves):
            legal = self.board.legal_plays(states_copy)
            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            # If we have stats on all of the legal moves here, use them.
            for p, S in moves_states:
                already_recorded = plays.get( (player, S) )
                if not already_recorded:
                    break
            if already_recorded:
                sum = 0
                for p, S in moves_states:
                    sum += plays[(player, S)]
                log_total = log( sum )
                value, move, state = max( ((wins[(player, S)] / plays[(player, S)]) + self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states)
            else:
                # if not moves_states:
                #     print(state)
                # Otherwise, just make an arbitrary decision.
                move, state = choice(moves_states)

            states_copy.append(state)

            # `player` here and below refers to the player who moved into that particular state.
            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if winner:
                break

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if player == winner:
                wins[(player, state)] += 1

def run():
    #Set up game board.
    board = Board()
    #Set up montecarlo.
    montecarlo = MonteCarlo(board)
    montecarlo.update(board.start())

    #Play game to completion for all players.
    while board.winner(montecarlo.states) == -1:
        best_move = montecarlo.get_play()
        next_state = board.next_state(montecarlo.states[-1], best_move)
        print(next_state)
        montecarlo.update( next_state )


    print("Winner:",Player_Colour(board.winner(montecarlo.states)))

    


run()