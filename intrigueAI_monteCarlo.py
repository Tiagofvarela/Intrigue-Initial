#Structural basis for this program by Jeff Bradberry. https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

from __future__ import division
import datetime
from math import sqrt, log
from random import choice
import random
from shutil import move
import time
from board import Board, GameMove
from game import Game
from intrigueAI import IntrigueAI
from intrigue_datatypes import PLAYER_COUNT, Player_Colour
from player import Player, recursive_hash_object


def random_max_tuple(tuple_list):
    tuple_list:list[tuple[int,...]] = list(tuple_list)
    max_tuples = [tuple_list[0]]
    max_val = tuple_list[0][0]
    for i in range(1,len(tuple_list)):
        if tuple_list[i][0] > max_val:
            max_val = tuple_list[i][0]
            max_tuples = [tuple_list[i]]
        elif tuple_list[i][0] == max_val:
            max_tuples.append(tuple_list[i])
    return random.choice(max_tuples)

def eval_greedy(player:int, state:Game):
    """Returns the difference between the player's money and the second player's money."""
    vals = sorted([p.money for p in state.players])
    return state.players[player].money - vals[1]

def filter_target_square_income_moveset(legal_plays:list[GameMove]) -> list[GameMove]:
    filtered:list[GameMove] = []
    income_one:list[GameMove] = []
    income_three:list[GameMove] = []
    income_six:list[GameMove] = []
    income_ten:list[GameMove] = []

    #Separate moves into money-making classes.
    for play in legal_plays:
        earnings, conflicts, placements, applications = play
        sum:float = 0
        for piece, square, bribe in applications:
            sum += square.value
        average:int = round(sum/2)
        if average >= 10:
            income_ten.append(play)
        elif average >= 6:
            income_six.append(play)
        elif average >= 3:
            income_three.append(play)
        else:
            income_one.append(play)

    if income_ten:
        if len(income_ten) == 0:
            raise Exception
        return income_ten
    if income_six:
        return income_six
    if income_three:
        return income_three
    if income_one:
        return income_one
    return filtered

def filter_resolution_square_income_moveset(legal_plays:list[GameMove]) -> list[GameMove]:
    filtered:list[GameMove] = []

    #Separate moves into money-making classes.
    for move in legal_plays:
        pass
    return filtered

def convert_move_natural_language(play:GameMove):
    """Converts a game move into two simplified strings in natural language."""
    _, _, placements, applications = play
    placement_string:str = ""
    application_string:str = ""
    if placements:
        placement_string = "Placements: "
        #Placements
        for app, square in placements:
            piece, app_square, bribe = app
            placement_string += "Placed "+repr(piece)+" in "+repr(square)
            placement_string += "; "
        placement_string += "\n"
    if applications:
        application_string = "Applications: "
        #Applications
        for piece, square, bribe in applications:
            application_string += "Sent "+repr(piece)+" to "+repr(square)+" with a bribe of "+str(bribe*1000)
            application_string += "; "
    return placement_string+application_string

#TODO: Create "legal plays filter" for legal plays to bias montecarlo agents towars making or not making certain plays.
#TODO: Create "bribe policy" to have a static/semi-static decider for each bribe, thereby not increasing the state space.

#TODO: The first move in a game doesn't need to calculate all combinations of pieces sent, since sending any two pieces is the same as any other two.
class MonteCarlo(IntrigueAI):
    def __init__(self, board, **kwargs):
        """Takes an instance of a Board and optionally some keyword arguments. 
        Initializes the list of game states and the statistics tables."""
        super().__init__(board)
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.min_moves = kwargs.get('min_moves', 1)
        self.wins:dict[int,int] = {}
        self.plays:dict[int,int] = {}
        self.C = kwargs.get('C', 1.4)

        # self.legal_moves_memory:dict[int,list[tuple[GameMove,Game]]] = {}
        # self.id_to_game:dict[int,Game] = {}
        # """Given a unique ID, stores the game corresponding to it. (The ID is the game's hash value.)"""

        self.eval_function = None
        self.filter_function = lambda l : l
        
        self.max_depth = 0

    def set_eval_function(self, function_type:str):
        if function_type == 'g':
            self.eval_function = eval_greedy

    def set_filter_function(self, function_type:str):
        if function_type == 't':
            self.filter_function = filter_target_square_income_moveset
        elif function_type == 'r':
            self.filter_function = filter_resolution_square_income_moveset

    def get_play(self):
        """Causes the AI to calculate the best move from the current game state and return it."""
        self.max_depth = 0
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:], self.decide_bribe)
        print(state)
        print("\nRound:"+str(state.turn_counter+1)+" "+Player_Colour(player).name+" Turn\nLegal moves available: "+str(len(legal)))
        log_info = repr(state)+"\nRound:"+str(state.turn_counter+1)+" "+Player_Colour(player).clean_name()+" Turn\nLegal moves available: "+str(len(legal))

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        filtered_legal = self.filter_function(legal)

        log_info += " Trimmed: "+repr(len(filtered_legal))
        print("Trimmed: "+repr(len(filtered_legal)))
        
        moves_states = [(play, self.board.next_state(state, play)) for play in filtered_legal]

        #TODO: Only shorten if not already shortened.
        current_calculation_time = self.__trim_calculation_time__(legal)

        games = 0
        games += self.run_simulation_min(moves_states,self.min_moves)
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < current_calculation_time:
            self.run_simulation_native(moves_states)
            games += 1
        
        file = open(self.filename,"a")
        file.write(log_info)
        # Display the number of calls of `run_simulation` and the time elapsed.
        file.write("\nPlays simulated: "+str(games)+"\n")
        file.write("Time spent simulating plays: "+str(datetime.datetime.utcnow() - begin)+"\n")

        percent_wins, move = random_max_tuple( (self.wins.get(recursive_hash_object((player, S)), 0) / self.plays.get(recursive_hash_object((player, S)), 1), play) for play, S in moves_states)
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
                play_natural_string = convert_move_natural_language(play)
                file.write(play_natural_string+" : "+str(percentage)+"% ("+str(wins)+" / "+str(plays)+")"+"\n")
            # file.write("{3}: {0:.2f}% ({1} / {2})".format(*x)+"\n") #play: win_percentage% (wins / plays)
        file.write("Maximum depth searched: "+ str(self.max_depth)+"\n\n")
        file.close()

        # print(self.plays)

        return move

    def __trim_calculation_time__(self, legal):
        """Reduces calculation time according to quantity of available plays."""
        length_counter = len(legal)
        current_calculation_time = self.calculation_time
        #Large move sets use time in parameters.
        if length_counter > 200:
            return current_calculation_time
        #Shorter move counters use shorter time.
        game_increments_100s = 2
        while length_counter > 100:
            game_increments_100s += 2
            length_counter -= 100
        print(str(current_calculation_time.total_seconds())+"s trimed to "+str(game_increments_100s)+"s")
        current_calculation_time = datetime.timedelta( seconds=min(current_calculation_time.total_seconds(), game_increments_100s) )
        return current_calculation_time

    def run_simulation_native(self, moves_states_initial):
        # A bit of an optimization here, so we have a local
        # variable lookup instead of an attribute access each loop.
        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)

        expand = True
        for move_counter in range(1, PLAYER_COUNT*5 + 1):
            legal = self.board.legal_plays(states_copy, self.decide_bribe)
            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get( recursive_hash_object((player, S)) ) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = log(
                    sum(plays[recursive_hash_object((player, S))] for p, S in moves_states))
                value, move, state = random_max_tuple(
                    ((wins[recursive_hash_object((player, S))] / plays[recursive_hash_object((player, S))]) +
                     self.C * sqrt(log_total / plays[recursive_hash_object((player, S))]), p, S)
                    for p, S in moves_states
                )
                # print("Selecting the best move in move "+str(move_counter))
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = choice(moves_states)

            states_copy.append(state)

            # `player` here and below refers to the player
            # who moved into that particular state.
            if expand and (recursive_hash_object((player, state)) not in plays.keys()):
                # print("Expanded at "+str(move_counter))
                expand = False
                plays[recursive_hash_object((player, state))] = 0
                wins[recursive_hash_object((player, state))] = 0
                if move_counter > self.max_depth:
                    self.max_depth = move_counter

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner_int, winners = self.board.winner(states_copy)
            if winner_int >= 0: #Game has finished.
                break

        for player, state in visited_states:
            if recursive_hash_object((player, state)) not in plays.keys():
                continue
            plays[recursive_hash_object((player, state))] += 1
            if player == winner_int:
                wins[recursive_hash_object((player, state))] += 1
    
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
        for move_counter in range(PLAYER_COUNT*5 + 1):

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
                    percent, move, state = random_max_tuple( ((self.wins[recursive_hash_object((player, S))] / self.plays[recursive_hash_object((player, S))]) + self.C * sqrt(log_total / self.plays[recursive_hash_object((player, S))]), play, S)
                        for play, S in moves_states)
                else:
                    # Otherwise, just make an arbitrary decision. [play and state that move results in]
                    move, state = choice(moves_states)
            else:
                move = self.board.get_random_legal_play(states_so_far, self.decide_bribe)
                state = self.board.next_state(state, move)

            #state now refers to state moved into
            states_so_far.append(state)

            #If this play hasn't been expanded, expand it. (Set stats to default 0) [player, state they moved into]
            if expand and recursive_hash_object((player, state)) not in self.plays.keys():
                expand = False
                self.plays[recursive_hash_object((player, state))] = 0
                self.wins[recursive_hash_object((player, state))] = 0
                #Logs the necessary depth to reach an unplayed move. (If this is being expanded, then lower depth has already been explored.)
                if move_counter > self.max_depth:
                    self.max_depth = move_counter

            visited_states[recursive_hash_object((player, state))] = (player,state)

            player = self.board.current_player(state)
            winner_int, winners = self.board.winner(states_so_far)
            if winner_int >= 0:  #Game has finished.
                break

        #Update stats for expanded plays. (Only expanded are in dictionary.)
        for player, state in visited_states.values():
            if recursive_hash_object((player, state)) in self.plays.keys():
                self.plays[recursive_hash_object((player, state))] += 1
                if self.eval_function:
                    self.wins[recursive_hash_object((player, state))] += self.eval_function( player, state )
                elif player == winner_int:
                    self.wins[recursive_hash_object((player, state))] += 1

    def run_simulation_min(self, moves_states:list[tuple[GameMove,Game]], min_n:int):
        """Plays out a "random" game from the current position, then updates the statistics tables with the result."""
        sim_count = 0
        current_n = min_n
        #Does min runs.
        while current_n > 0:
            current_n -= 1
            #Each run goes through each existing starting move until the end once.
            for play, next_state in moves_states:
                sim_count += 1

                #Each of these variables refer to a single run. self.plays and self.wins represent the memory of visited states.
                visited_states:dict[int,tuple[int,Game]] = {}
                states_so_far:list[Game] = self.states[:]
                state:Game = states_so_far[-1]
                player = self.board.current_player(state)

                expand = True #TODO: It's probably the case that pulling the check outside the while is best.

                #Simulate one full game for this move.
                first_move = True
                while True:

                    if first_move:
                        first_move = False
                        move = play
                        state = next_state
                    else:
                        move = self.board.get_random_legal_play(states_so_far, self.decide_bribe)
                        state = self.board.next_state(state, move)

                    #state now refers to state moved into
                    states_so_far.append(state)

                    #If this play hasn't been expanded, expand it. (Set stats to default 0) [player, state they moved into]
                    if expand and recursive_hash_object((player, state)) not in self.plays.keys():
                        expand = False
                        self.plays[recursive_hash_object((player, state))] = 0
                        self.wins[recursive_hash_object((player, state))] = 0

                    visited_states[recursive_hash_object((player, state))] = (player,state)

                    player = self.board.current_player(state)
                    winner_int, winners = self.board.winner(states_so_far)
                    if winner_int >= 0:  #Game has finished.
                        break

                #Update stats for expanded plays. (Only expanded are in dictionary.)
                for player, state in visited_states.values():
                    if recursive_hash_object((player, state)) in self.plays.keys():
                        self.plays[recursive_hash_object((player, state))] += 1
                        if self.eval_function:
                            self.wins[recursive_hash_object((player, state))] += self.eval_function( player, state )
                        elif player == winner_int:
                            self.wins[recursive_hash_object((player, state))] += 1

        if sim_count != len(moves_states)*min_n:
            raise Exception("Simulated "+str(sim_count)+" but should have been "+str(len(moves_states))+"*"+str(min)+" = "+str(len(moves_states)*min_n))
        return sim_count 


    # def __register_game(self, state:Game):
    #     """Given a game state, registers it with a unique id (its hash)."""
    #     id_val = hash(state)
    #     if not self.id_to_game.__contains__(id_val):
    #         self.id_to_game[id_val] = state