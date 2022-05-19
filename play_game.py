from __future__ import division
import sys
import time
from board import Board
from intrigueAI import IntrigueAI
from intrigue_datatypes import PLAYER_COUNT, Player_Colour
from intrigueAI_monteCarlo import MonteCarlo

def run():
    #Set up game board.
    board = Board()
    #Montecarlo Parameters
    args = {'time':10,'max_moves':120,'C':1.3}

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
    #TODO: Player-Log should note start state, play and end state for each play, and the most considered options.
    #Depending on AI type, should also write "why" something was chosen.

    tic = time.perf_counter()
    #Play game to completion for all players.
    current_player = agent_AIs[board.current_player(board.start())]
    while board.winner(current_player.states) == -1:
        chosen_move = current_player.get_play()
        next_state = board.next_state(current_player.get_current_state(), chosen_move)
        print(next_state)
        for ai in agent_AIs:
            ai.update(next_state)
        current_player = agent_AIs[board.current_player(next_state)]

    if board.winner(current_player.states) >= PLAYER_COUNT:
        print("The game was a tie.")#TODO: Establish who is tieing.
    else:
        print("Winner:",Player_Colour(board.winner(current_player.states)).name)
    toc = time.perf_counter()
    taken_minutes = (toc - tic)/60
    print("It has taken",taken_minutes,"minutes.")
    # print(montecarlo.plays)

run()