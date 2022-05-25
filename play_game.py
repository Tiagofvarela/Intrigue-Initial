from __future__ import division
import datetime
from io import TextIOWrapper
import sys
import time
from board import Board, GameMove
from game import Game
from intrigueAI import IntrigueAI
from intrigueAI_human import Human
from intrigue_datatypes import CHOSEN_MOVE_STRING, PLAYER_COUNT, Player_Colour
from intrigueAI_monteCarlo import MonteCarlo
from player import EarningsLog

# def read_move(move_str:str) -> GameMove:
#     line_index = 0
#     earnings:EarningsLog = []

#     while move_str[line_index] != '[':
#         line_index += 1
#     #Earnings Log
#     line_index += 1
#     #Read square
#     if move_str[line_index] == '|':
#         pass

#     #Conflict Log

#     return ([],[],[],[])

# def play_from_log(gamelog_name:str):
#     board = Board()
#     state = board.start()

#     file = open(gamelog_name)
#     while True:
#         line = file.readline()
#         if not line:
#             break
#         if line[:-1] == CHOSEN_MOVE_STRING:
#             gamemove = read_move(line)
#             state = board.next_state(state, gamemove)
#             print(state)
#     file.close()
#     if board.winner([state]) >= PLAYER_COUNT:
#         print("The game was a tie.")#TODO: Establish who is tieing.
#     else:
#         print("Winner:",Player_Colour(board.winner([state])).name)

def log_natural_language(gamelog:TextIOWrapper, play:GameMove, player_name:str):
    earnings, conflicts, placements, applications = play
    if earnings:
        gamelog.write("Earnings:\n")
        #Earnings
        for square in earnings:
            gamelog.write(player_name+" has collected "+str(square.value)+" from "+repr(square))
            gamelog.write("\n")
    if conflicts:
        gamelog.write("Conflicts:\n")    
        #Conflicts and collections
        for conflict, chosen_app in conflicts:
            gamelog.write(player_name+" has chosen "+repr(chosen_app)+" out of "+repr(conflict))
            gamelog.write("\n")
    if placements:
        gamelog.write("Placements:\n")
        #Placements
        for app, square in placements:
            piece, app_square, bribe = app
            gamelog.write(player_name+" has placed "+repr(piece)+" in "+repr(square)+" for a bribe of "+str(bribe*1000))
            gamelog.write("\n")
            if square.value != app_square.value:
                gamelog.write(piece.owner.clean_name()+" wanted the piece in "+repr(app_square))
                gamelog.write("\n")
                # gamelog.write("\n")
    if applications:
        gamelog.write("Applications:\n")
        #Applications
        for piece, square, bribe in applications:
            gamelog.write(player_name+" has sent "+repr(piece)+" to "+repr(square)+" with a bribe of "+str(bribe*1000))
            gamelog.write("\n")

def is_float(string:str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False

def run():
    #Set up game board.
    board = Board()
    #Parameters
    args = {'time':15,'max_moves':120,'C':1.4}
    number_of_games = 1
    
    #Generate intrigue agents.
    agent_AIs:list[IntrigueAI] = []
    argument_counter = 1
    try:
        for arg in sys.argv[1:]:
            print(arg)
            if str.isdigit(arg):
                #Number of games
                if argument_counter == 1:
                    number_of_games = max(int(arg),1)
                #Montecarlo thinking time
                elif isinstance(agent_AIs[-1], MonteCarlo):
                    agent_AIs[-1].calculation_time = datetime.timedelta(seconds=int(arg))
                else:
                    raise Exception("This agent type does not receive int arguments.")
                continue
            #Constant
            elif is_float(arg):
                if isinstance(agent_AIs[-1], MonteCarlo):
                    agent_AIs[-1].C = float(arg)
                else:
                    raise Exception("This agent type does not receive float arguments.")
                continue
            elif arg == "montecarlo":
                agent_AIs.append(MonteCarlo(board, **args))
            elif arg == "random":                
                agent_AIs.append(IntrigueAI(board))
            elif arg == "human":
                agent_AIs.append(Human(board))
            else:
                raise AttributeError()
            argument_counter += 1   
        if len(agent_AIs) < 4:
            raise Exception("Not enough player types indicated.")   
    except AttributeError as e:
        print("\nError: The given type of player does not exist.")
        exit()
    except Exception as e:
        print("\nError:",e.args[0])
        print("Please indicate four player types by writing four type names separated by spaces. Ex:")
        print("montecarlo montecarlo random random")
        print("Montecarlo instances have optional 'calculation_time' (integer) and 'constant C' (decimal) arguments. Ex:")
        print("montecarlo 20 1.5 montecarlo 1.2 montecarlo montecarlo 6")
        exit()

    #TODO: Feed Game-Log to replay a game.
    #TODO: Player-Log should, depending on AI type, also write "why" something was chosen.

    game_counter = 0
    wins_tally:list[int] = [0,0,0,0]
    while game_counter < number_of_games:
        game_counter += 1
        #Initialise logs and players.
        open(str(game_counter)+"_game_log.txt", 'w').close()  
        gamelog = open(str(game_counter)+"_game_log.txt", 'a') 
        for i in range(len(agent_AIs)):
            file_name = str(game_counter)+"_player"+str(i)+"-log.txt"
            open(file_name, 'w').close()  
            agent_AIs[i].filename = file_name
            agent_AIs[i].update(board.start())

        tic = time.perf_counter()
        #Play game to completion for all players.
        current_player = agent_AIs[board.current_player(board.start())]

        gamelog.write(repr(current_player.states[-1]))
        gamelog.write("\n")
        gamelog.write("Round 1: "+str(Player_Colour(0).clean_name())+" turn\n")

        while board.winner(current_player.states) == -1:
            chosen_move = current_player.get_play()
            #Register move
            gamelog.write(CHOSEN_MOVE_STRING)
            gamelog.write("\n")
            gamelog.write(repr(chosen_move))
            gamelog.write("\n\n")
            log_natural_language(gamelog,chosen_move,Player_Colour(current_player.get_current_state().get_player_turn()).clean_name())

            next_state = board.next_state(current_player.get_current_state(), chosen_move)
            print(next_state)
            for ai in agent_AIs:
                ai.update(next_state)
            current_player_id = board.current_player(next_state)
            current_player = agent_AIs[current_player_id]

            gamelog.write(repr(next_state))
            gamelog.write("\n")
            gamelog.write("Round "+str(next_state.turn_counter+1)+": "+str(Player_Colour(current_player_id).clean_name())+" turn\n")

        if board.winner(current_player.states) >= PLAYER_COUNT:
            print("The game was a tie.")#TODO: Establish who is tieing.
            gamelog.write("The game was a tie.")
        else:
            winner_int = board.winner(current_player.states)
            print("Winner:",Player_Colour(winner_int).name)
            gamelog.write("Winner: "+str(Player_Colour(winner_int).clean_name()))
            wins_tally[winner_int] += 1
        toc = time.perf_counter()
        taken_minutes = (toc - tic)/60
        print("It has taken",taken_minutes,"minutes.")
        gamelog.write("It has taken "+str(taken_minutes)+" minutes.")
        # print(montecarlo.plays)
        gamelog.close()
    for i in range(len(wins_tally)):
        print(Player_Colour(i).name+" won "+str(wins_tally[i])+" times.")

run()