#Structural basis for this program by Jeff Bradberry. https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

from __future__ import division
import datetime
from math import sqrt, log
from random import choice
import time
from board import Board, GameMove
from game import Game
from intrigueAI import IntrigueAI
from intrigue_datatypes import PLAYER_COUNT, Player_Colour
from player import Player, recursive_hash_object


class MonteCarlo(IntrigueAI):
    def __init__(self, board, **kwargs):#TODO: Evaluation function parameter to evaluate a final state and attribute points.
        """Takes an instance of a Board and optionally some keyword arguments. 
        Initializes the list of game states and the statistics tables."""
        super().__init__(board)
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves', 100)
        self.wins:dict[int,int] = {}
        self.plays:dict[int,int] = {}
        self.C = kwargs.get('C', 1.4)

        # self.legal_moves_memory:dict[int,list[tuple[GameMove,Game]]] = {}
        # self.id_to_game:dict[int,Game] = {}
        # """Given a unique ID, stores the game corresponding to it. (The ID is the game's hash value.)"""
        
        self.max_depth = 0

    def get_play(self):
        """Causes the AI to calculate the best move from the current game state and return it."""
        self.max_depth = 0
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])
        print(state)
        print("\nRound:"+str(state.turn_counter+1)+" "+Player_Colour(player).name+" Turn\nLegal moves available: "+str(len(legal)))
        log_info = repr(state)+"\nRound:"+str(state.turn_counter+1)+" "+Player_Colour(player).clean_name()+" Turn\nLegal moves available: "+str(len(legal))

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]
        
        moves_states = [(play, self.board.next_state(state, play)) for play in legal]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(moves_states)
            games += 1
        
        file = open(self.filename,"a")
        file.write(log_info)
        # Display the number of calls of `run_simulation` and the time elapsed.
        file.write("\nPlays simulated: "+str(games)+"\n")
        file.write("Time spent simulating plays: "+str(datetime.datetime.utcnow() - begin)+"\n")
        percent_wins, move = max( (self.wins.get(recursive_hash_object((player, S)), 0) / self.plays.get(recursive_hash_object((player, S)), 1), play) for play, S in moves_states)
        file.write("Montecarlo move chosen:\n"+repr(move))
        file.write("\n\nMost simulated moves:\n")
        # Display the stats for each possible play.
        for x in sorted(
            ((100 * self.wins.get(recursive_hash_object((player, S)), 0) /
              self.plays.get(recursive_hash_object((player, S)), 1),           #Win percentage
              self.wins.get(recursive_hash_object((player, S)), 0),            #Number of Wins.
              self.plays.get(recursive_hash_object((player, S)), 0),           #Number of times simulated.
              p)                                        #Play
             for p, S in moves_states),
            reverse=True
        ):
            percentage, wins, plays, play = x
            if percentage > 0 or plays > 1:
                file.write(repr(play)+": "+str(percentage)+"% ("+str(wins)+" / "+str(plays)+")"+"\n")
            # file.write("{3}: {0:.2f}% ({1} / {2})".format(*x)+"\n") #play: win_percentage% (wins / plays)
        file.write("Maximum depth searched: "+ str(self.max_depth)+"\n\n")
        file.close()

        # print(self.plays)

        return move

    def run_simulation(self, moves_states:list[tuple[GameMove,Game]]):
        """Plays out a "random" game from the current position, then updates the statistics tables with the result."""

        visited_states:dict[int,tuple[int,Game]] = {}
        states_so_far:list[Game] = self.states[:]
        state:Game = states_so_far[-1]
        player = self.board.current_player(state)

        
        #All moves should be generated in order to explore interesting games.
        #But this generation only needs to be done once, since the starting state is always the same.
        #Depth 1, 2, 3 and so on do not need to apply UCT. They choose a move randomly.
        starting_move = True

        #Generates all legal plays for current state and picks one to be next state.
        expand = True
        for move_counter in range(self.max_moves):

            # #Code to general set of legal moves for this depth.
            # #If the current state was previously visited, reuse all legal moves.
            # if self.legal_moves_memory.__contains__(recursive_hash_object(states_so_far[-1])):
            #     print("\nMemory works.\n")
            #     moves_states = self.legal_moves_memory[recursive_hash_object(states_so_far[-1])]
            # else:
            #     legal = self.board.legal_plays(states_so_far)
            #     moves_states = [(play, self.board.next_state(state, play)) for play in legal]
            #     self.legal_moves_memory[recursive_hash_object(states_so_far[-1])] = moves_states

            # If we have stats on all of the legal moves here, use them. 
            # TODO: Use a flag and counter to figure out if all plays have been explored.
            if starting_move:
                starting_move = False
                for play, S in moves_states:
                    already_recorded = self.plays.get( recursive_hash_object((player, S)), None )
                    if not already_recorded:
                        break
                if already_recorded:
                    sum = 0
                    for play, S in moves_states:
                        sum += self.plays[recursive_hash_object((player, S))]
                    log_total = log( sum )
                    value, move, state = max( ((self.wins[recursive_hash_object((player, S))] / self.plays[recursive_hash_object((player, S))]) + self.C * sqrt(log_total / self.plays[recursive_hash_object((player, S))]), play, S)
                        for play, S in moves_states)
                else:
                    # Otherwise, just make an arbitrary decision.
                    move, state = choice(moves_states)
            else:
                move = self.board.get_random_legal_play(states_so_far)
                state = self.board.next_state(state, move)

            states_so_far.append(state)

            #If this play hasn't been expanded, expand it. (Set stats to default 0)
            if expand and recursive_hash_object((player, state)) not in self.plays.keys():
                expand = False
                self.plays[recursive_hash_object((player, state))] = 0
                self.wins[recursive_hash_object((player, state))] = 0
                #Logs the necessary depth to reach an unplayed move. (If this is being expanded, then lower depth has already been explored.)
                if move_counter > self.max_depth:
                    self.max_depth = move_counter

            visited_states[recursive_hash_object((player, state))] = (player,state)

            player = self.board.current_player(state)
            winner = self.board.winner(states_so_far)
            if winner > 0:  #Game has finished.
                break

        #Update stats for expanded plays. (Only expanded are in dictionary.)
        for player, state in visited_states.values():
            if recursive_hash_object((player, state)) in self.plays.keys():
                self.plays[recursive_hash_object((player, state))] += 1
                if player == winner:
                    self.wins[recursive_hash_object((player, state))] += 1

    # def __register_game(self, state:Game):
    #     """Given a game state, registers it with a unique id (its hash)."""
    #     id_val = hash(state)
    #     if not self.id_to_game.__contains__(id_val):
    #         self.id_to_game[id_val] = state