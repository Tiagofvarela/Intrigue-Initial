from intrigueAI import IntrigueAI
from intrigue_datatypes import MINIMUM_BRIBE
from piece import Piece
from player import Application
from square import Square


class Human(IntrigueAI):
    

    def get_application(self, board, previous_app:Application|None): #TODO: If both applications are equal, warn the player and ask again.
        """Asks the human player to select two pieces to send."""
        game = self.get_current_state()
        my_player = game.players[game.get_player_turn()]

        if previous_app:
            previous_piece = [previous_app[0]]
            previous_square = [previous_app[1]]
            previous_bribe = previous_app[2]
        else:
            previous_piece = []
            previous_square = []
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
        print(my_player.pieces-previous_piece)
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

    def decide_bribe(self, piece:Piece, square:Square, max_spendable:int) -> int:
        print("Application: "+str(piece)+square.__colour_str__())
        #print("Applicant bribes (-1 are unknown): "+str(previous_bribes))
        print("Select bribe amount (value will be adjusted to the nearest limit). Min",MINIMUM_BRIBE,"Max",max_spendable)
        bribe = max(int(input()), MINIMUM_BRIBE)
        bribe = min(bribe, max_spendable)
        return bribe
    
    def select_square_to_place(self, application:Application):
        game = self.get_current_state()
        palace = game.board[game.get_player_turn()]
        print(palace)
        #print("Bribes: "+str(bribes))
        print("\nChoose which square to place the piece",application[0],". It must be unocupied:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
        square_i = int(input())
        while palace[square_i].piece:
            print("\nThat index is occupied. Please select another.")
            square_i = int(input())
        return palace[square_i]
        
    def resolve_conflict(self, conflict:list[Application]):
        print("Applications: "+str(conflict))
        print("\nOut of the applicants, choose one. Type the index of the chosen applicant:")
        try:
            chosen = conflict[int(input())]   
        except:
            print("Invalid index. Please select again.")
            return self.resolve_conflict(conflict)
        return chosen