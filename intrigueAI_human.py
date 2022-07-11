from textwrap import shorten
from typing import Optional
from board import GameMove
from intrigueAI import IntrigueAI
from intrigue_datatypes import MINIMUM_BRIBE, Player_Colour
from piece import Piece
from player import Application, ApplicationLog, ConflictLog, EarningsLog, Gameboard, PlacementLog
from square import Square


class Human(IntrigueAI):
    
    def get_play(self) -> GameMove:
        """Returns a play for the current state. (Default: Random)\nUpdates log accordingly."""
        file = open(self.filename,"a")
        file.write(repr(self.states[-1])+"\n")

        game = self.get_current_state()
        my_player = game.players[game.get_player_turn()]
        #Get play
        earnings_log:EarningsLog = my_player.collect_earnings(game.boards)
        #ConflictLog
        conflict_log:ConflictLog = []
        for conflict in my_player.get_conflicts(game.boards):
            conflict_log.append( (conflict, self.resolve_conflict(conflict)) )
        #PlacementLog
        placement_log, applications_to_place = my_player.get_applications_to_place(conflict_log)
        for app in applications_to_place:
            placement_log.append( (app, self.select_square_to_place(app)) )
        #ApplicationLog
        application_log:ApplicationLog = []
        application_log.append(self.get_application(game.boards, None))
        application_log.append(self.get_application(game.boards, application_log[-1]))
        
        chosen_play:GameMove = (earnings_log, conflict_log, placement_log, application_log)

        log_info = "Round:"+str(game.turn_counter+1)+" "+my_player.colour.clean_name()+" Turn\n"+"Random play chosen: \n"+repr(chosen_play)+"\n"
        print(log_info)
        file.write(log_info)
        file.close()
        return chosen_play
        
    def resolve_conflict(self, conflict:list[Application]):#TODO: Mark internal choice by checking app[1].square.piece == app[0].piece
        print("Applications: "+repr(conflict))
        print("\nOut of the applicants, choose one. Type the index of the chosen applicant:")
        try:
            return conflict[int(input())]   
        except Exception as e:
            print("\nError:",e.args[0])
            print("\nInvalid index. Please select again.")
            return self.resolve_conflict(conflict)

    def select_square_to_place(self, application:Application):#TODO: Remember where previous pieces were placed.
        game = self.get_current_state()
        palace = game.boards[game.get_player_turn()]
        print(palace)
        #print("Bribes: "+str(bribes))
        print("\nChoose which square to place the piece",application[0],". It must be unocupied:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
        square_i = int(input())
        while palace[square_i].piece:
            print("\nThat index is occupied. Please select another.")
            square_i = int(input())
        return palace[square_i]

    def get_application(self, board:Gameboard, previous_app:Optional[Application]): #TODO: If both applications are equal, warn the player and ask again.
        """Asks the human player to select two pieces to send."""
        game = self.get_current_state()
        my_player = game.players[game.get_player_turn()]

        if previous_app:
            previous_piece:Optional[Piece] = previous_app[0]
            previous_square:Optional[Square] = previous_app[1]
            previous_bribe = previous_app[2]
        else:
            previous_piece = None
            previous_square = None
            previous_bribe = 0

        #Choose target player
        player_i = -1
        while player_i < 0 or player_i > 3:
            print("Choose to which player you will send a piece. Type one of the following numerical values:"
            +"\n0 (Red), 1 (Green), 2 (Blue), 3 (Yellow)")
            player_i = int(input())
            if player_i == my_player.colour.value:
                print("You cannot send an application to yourself.")
                player_i = -1
                continue
        #Choose target square
        square_i = -1
        while square_i < 0 or square_i > 3:
            print("Choose which square you want your piece to go to. Type one of the following numerical values:"
            +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
            square_i = int(input())
            
        #Choose piece
        if previous_piece:
            pieces_no_repeat = my_player.pieces.copy().remove(previous_piece)
            print( pieces_no_repeat )
        else:
            print(my_player.pieces)
            
        piece_i = -1
        while piece_i < 0 or piece_i > len(my_player.pieces)-1:
            print("Choose which piece you will send. The first piece is index 0. Type the index corresponding to the piece:")
            piece_i = int(input())

        piece_to_play = my_player.pieces[piece_i]
        square_to_send_to = board[player_i][square_i]

        #Choose bribe amount
        if previous_app:
            bribe = self.decide_bribe(piece_to_play, square_to_send_to, my_player.money-previous_bribe)
        else:
            bribe = self.decide_bribe(piece_to_play, square_to_send_to, my_player.money-1)
        return (piece_to_play, square_to_send_to, bribe)

    def decide_bribe(self, piece:Piece, square:Square, max_spendable:int= None) -> int:
        assert max_spendable
        print("Application: "+str(piece)+square.__colour_repr__())
        #print("Applicant bribes (-1 are unknown): "+str(previous_bribes))
        print("Select bribe amount (value will be adjusted to the nearest limit). Min",MINIMUM_BRIBE,"Max",max_spendable)
        bribe = max(int(input()), MINIMUM_BRIBE)
        bribe = min(bribe, max_spendable)
        return bribe
    