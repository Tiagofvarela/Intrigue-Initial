from __future__ import division
from io import TextIOWrapper
import sys
import time
from board import Board, GameMove
from intrigueAI import IntrigueAI
from intrigue_datatypes import PLAYER_COUNT, Player_Colour
from intrigueAI_monteCarlo import MonteCarlo

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

def run():
    #Set up game board.
    board = Board()
    #Montecarlo Parameters
    args = {'time':30,'max_moves':120,'C':1.4}

    #Generate intrigue agents.
    agent_AIs:list[IntrigueAI] = []
    log_counter = 1
    try:
        for type in sys.argv[1:]:
            if type == "montecarlo":
                agent_AIs.append(MonteCarlo(board, **args))
            elif type == "random":                
                agent_AIs.append(IntrigueAI(board))
            elif type == "human":
                pass #TODO: Implement human functionality.
            else:
                raise AttributeError()
            #Set up text log.
            file_name = "player"+str(log_counter)+"-log.txt"
            open(file_name, 'w').close()   
            log_counter += 1   
            agent_AIs[-1].update_file_name(filename=file_name)
            agent_AIs[-1].update(board.start())
        if len(agent_AIs) < 4:
            raise Exception("Not enough player types indicated.")   
    except AttributeError as e:
        print("\nError: The given type of player does not exist.")
        exit()
    except Exception as e:
        print("\nError:",e.args[0])
        print("Please indicate four player types by writing four type names separated by spaces. Ex:")
        print("montecarlo montecarlo random random")
        exit()

    #TODO: Feed Game-Log to replay a game.
    #TODO: Game-Log should have all states and plays (plays in natural language)
    #TODO: Player-Log should, depending on AI type, also write "why" something was chosen.
    open("game_log.txt", 'w').close()  
    gamelog = open("game_log.txt", 'a') 

    tic = time.perf_counter()
    #Play game to completion for all players.
    current_player = agent_AIs[board.current_player(board.start())]

    gamelog.write(repr(current_player.states[-1]))
    gamelog.write("\n")
    gamelog.write("Round 1: "+str(Player_Colour(0).clean_name())+" turn\n")

    while board.winner(current_player.states) == -1:
        chosen_move = current_player.get_play()

        gamelog.write("Chosen move:\n")
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
        print("Winner:",Player_Colour(board.winner(current_player.states)).name)
        gamelog.write("Winner: "+str(Player_Colour(board.winner(current_player.states)).clean_name()))
    toc = time.perf_counter()
    taken_minutes = (toc - tic)/60
    print("It has taken",taken_minutes,"minutes.")
    gamelog.write("It has taken"+str(taken_minutes)+"minutes.")
    # print(montecarlo.plays)
    gamelog.close()

run()