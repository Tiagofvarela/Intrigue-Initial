from __future__ import annotations
from typing import Any
from intrigue_datatypes import Player_Colour, MINIMUM_BRIBE
from player import Application, Gameboard, Player, copy_application
from piece import Piece
from square import Square
from random import choice, randint
import sys, copy
#from colorama import Fore, Style

class Game():
    boards:Gameboard
    players:list[Player]

    def __init__(self, player_types:list[str]):
        self.boards = []
        self.players = []
        try:
            for i in range(4):
                def str_to_class(classname):
                    return getattr(sys.modules[__name__], classname)
                print("Creating player of type",player_types[i])
                self.players.append(str_to_class(player_types[i])(Player_Colour(i)))
                #Line of Squares owned by Player i.
                self.boards.append([Square(0,self.players[-1]),Square(1,self.players[-1]),Square(2,self.players[-1]),Square(3,self.players[-1])])
        except AttributeError as e:
            print("\nError: The class name given does not exist inside intrigue.py")
            exit()
        except Exception as e:
            print("\nError:",e.args[0])
            print("Please indicate four player types by writing four type names separated by spaces.")
            exit()
        print(self)
        
    def play_game(self):
        """
        For each player:
            Collect earnings. (Sweep board and get money from each own piece.)\n
            Sweep and register each applicant.\n
            Accept applicants.\n
                Place uncontested ones.\n
                resolve_external_conflict()\n
                resolve_internal_conflict()\n
            play_piece() * 2
        """
        def player_send_piece(p:Player) -> tuple[Application,Player]:
            """Player p sends a piece to a player of their choosing."""
            app, player = p.play_piece(self.boards, self.players)
            #Remove piece from p and send to player.
            print(p.colour.name+" sent "+str(app[0])+" to "+player.colour.name)
            p.pieces.remove(app[0])
            player.palace_applicants.append(app)   
            return copy_application(app), player.__deepcopy__(None)

        #game_log:list[dict[str,Any]] = [{"earnings_log":[], }]
        
        counter = 1
        while counter <= 6:
            print("\n############# ROUND ",counter,"#############\n")
            for p in self.players:
                print("\n###",p.colour.name,"TURN ###\n")

                application_log:list[tuple[Application,Player]] = []
                earnings_log = p.collect_earnings(self.boards)  
                conflict_log, placement_log = p.resolve_applications(self.boards, self.players)
                if counter <= 4:
                    print("\n# Send Pieces #\n")
                    application_log.append( player_send_piece(p) )
                    application_log.append( player_send_piece(p) )
                print(self)
                # print("Earnings:")
                # print(earnings_log)
                # print("Conflict Log:")
                # print(conflict_log)
                # print("Placement Log:")
                # print(placement_log)
                # print("Application Log:")
                # print(application_log)
                print("\n###",p.colour.name,"TURN  End ###\nPress enter to continue.")
                input()
            counter += 1

    def __str__(self):
        def line_str(squares:list[Square]) -> str:
            """Given a row of squares, prints their simple strings in a line."""
            line = ""
            for square in squares:
                line += str(square)
            return line
        
        board_rep = "________________________________________________________________________"
        for row in range(len(self.boards)):
            board_rep += "\n"+line_str(self.boards[row])+Player_Colour(row).name+" \nApplicants: "
            for piece, square in self.players[row].palace_applicants:
                board_rep += repr(piece)+" "#+str(piece.bribe)+"; "
            board_rep +="\n"
        board_rep += "\n"
        for p in self.players:
            board_rep += str(p)
        board_rep += "\n________________________________________________________________________"
        return board_rep

    def __repr__(self):
        return self.__str__()

def run():
    player_types = sys.argv
    player_types.pop(0)

    Game(player_types).play_game()
    print("Running!")

############################################### Player Classes ###############################################

class PlayerRandom(Player):
    def __init__(self, colour:Player_Colour):
        Player.__init__(self, colour)

    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        #Choose random player and square.
        player_i = randint(0,3)
        while Player_Colour(player_i) == self.colour:
            player_i = randint(0,3)
        square_i = randint(0,3)
        #Select random piece.
        piece_to_play = choice(self.pieces)
        #Add piece and preferred square (Piece,Square) to application.
        player = players[player_i]
        application = (piece_to_play, board[player_i][square_i])
        #Saves square and piece each time they make a request.
        self.history_applications.append((application,player))
        return application,player
    
    def decide_bribe(self, application:Application, previous_bribes:dict[Application,int]) -> int:
        #Bribe is set to random value between min and a fourth of total.
        bribe = randint(MINIMUM_BRIBE, max(round(self.money/4),MINIMUM_BRIBE) )
        self.money -= bribe
        return bribe

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application, bribes:dict[Application,int]):
        #Choose random unocupied square and place piece in it.
        palace = board[self.colour.value]
        square_i = randint(0,3)
        while palace[square_i].piece:
            square_i = randint(0,3)
        #palace[square_i].piece = application[0]
        return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], bribes:dict[Application,int]):
        #Chooses random application.
        chosen = choice(list(bribes.keys()))
        return chosen

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:dict[Application,int]):        
        #Randomly choose to replace or not.
        return choice(list(bribes.keys()))

class PlayerHonest(Player):
    def __init__(self, colour:Player_Colour):
        Player.__init__(self, colour)

    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        def choose_squares() -> list[Square]:
            """Returns contender squares to send a piece to."""
            #TODO: Select possible squares randomly.
            most_valuable_squares:list[Square] = self.get_max_value_unoccupied_squares(board)            
            
            #Starts looking in 10000 squares (index 2), then 6000 (index 1), and so on.
            priority = [2,1,3,0]
            priority_counter = 0
            while len(most_valuable_squares) == 0:  #No valid free squares found. GET MAX VALUE UNNOCUPIED SQUARES
                for i in range(len(board)):
                    square = board[i][ priority[priority_counter] ]
                    if not square.piece:    #Any free squares were already considered by previous function.
                        continue
                    #It must be possible to send piece to the square, competing with the piece already there.
                    can_compete = len([p for p in self.pieces if p.type == square.piece.type]) > 0
                    if Player_Colour(i) != self.colour and square.piece.owner != self and can_compete:
                        most_valuable_squares.append(square)
                priority_counter += 1
                if priority_counter > 4:
                    print(self.pieces)
                    raise Exception("Could not find a Square to send Piece to.")   #Stop execution if unexpected behaviour occurs.
            return most_valuable_squares

        def choose_player_square(squares:list[Square]) -> Square: 
            """Given the potential squares, chooses the square from the preferred player."""           
            #Choose a square from a Player who has accepted an application last time.
            chosen_square:Square
            for square in squares:
                if len(self.history_applications) >= 2:
                    for application,player in self.history_applications[-2::1]: #Last two applications.
                        if square.owner == player and application[1].piece == application[0]:
                                chosen_square = square
                                break
            #No accepted application found. 
            else:
                #Find a player whose pieces we host.
                for player in [s.owner for s in squares]:
                    for square in board[self.colour.value]:
                        if square.piece and square.piece.owner == player:
                            chosen_square = square
                            break
                #No accepted application found. 
                else:
                    #Find poorest possible player.
                    min_money = min([p.money for p in [s.owner for s in squares]])
                    chosen_square = [s for s in squares if s.owner.money == min_money][0]
            return chosen_square
        def choose_piece(square:Square) -> Piece:
            """Choose an appropriate piece to send to and attain desired square."""           
            if square.piece:
                #To get position we must match piece type.
                return [p for p in self.pieces if p.type == square.piece.type][0]
            
            #Else, avoid conflicting with other pieces to guarantee position.

            #Avoid conflicting with palace pieces.
            other_pieces_in_row = [s.piece for s in board[square.owner.colour.value] if s.piece]
            no_palace_conflicts = [p for p in self.pieces if p.type not in [p2.type for p2 in other_pieces_in_row]]

            #Avoid conflicting with other applications.
            conflicting_types = [a[0].type for a in square.owner.palace_applicants]
            no_application_conflicts = [p for p in no_palace_conflicts if p.type not in conflicting_types]

            if len(no_application_conflicts) > 0:   #No conflicts at all.
                return choice(no_application_conflicts)
            elif len(no_palace_conflicts) > 0:      #Conflicts only with applications.
                return choice(no_palace_conflicts)

            print(square)
            print(board[square.owner.colour.value])
            print(self.pieces)
            print(self.get_max_value_unoccupied_squares(board))
            raise Exception("The Square is empty, yet a non-conflicting piece couldn't be found.")

        square = choose_player_square(choose_squares())
        player = square.owner
        piece = choose_piece(square)

        application = (piece, square)   

        #Saves square and piece each time they make a request.
        self.history_applications.append((application,player))
        return application,player

    def decide_bribe(self, application:Application, previous_bribes:dict[Application,int]) -> int:
        #Bribe is set to the largest of the group, or the value of the square if no one has bribed yet.
        bribe = min(max(list(previous_bribes.values())) + 1, self.money) 
        #If no one has bribed yet.
        if bribe < 1000:
            bribe = min(application[1].value, self.money) 
        self.money -= bribe
        return bribe

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application, bribes:dict[Application,int]):
        #Attempts to place the piece in the requested square, else random.
        palace = board[self.colour.value]
        piece,square = application
        if not square.piece:
            return square
        else:
            #Set the piece at a random spot. TODO: Behaviour for putting most valuable keys in most valuable places.
            square_i = randint(0,3)
            while palace[square_i].piece:
                square_i = randint(0,3)
            return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], bribes:dict[Application,int]):
        #Chooses highest bribing piece.
        return self.get_max_bribe_application(bribes)

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:dict[Application,int]):
        #Chooses highest bribing piece.
        return self.get_max_bribe_application(bribes)

class PlayerHuman(Player):
    def __init__(self, colour:Player_Colour):
        Player.__init__(self, colour)

    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        #Choose player, square and piece.
        player_i = self.colour.value
        while player_i == self.colour.value:
            print("Choose to which player you will send a piece. Type one of the following numerical values:"
            +"\n0 (Red), 1 (Green), 2 (Blue), 3 (Yellow)")
            player_i = int(input())
        print("Choose which square you want your piece to go to. Type one of the following numerical values:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
        square_i = int(input())
        print(self.pieces)
        print("Choose which piece you will send. Type the index corresponding to the piece:")
        piece_to_play = self.pieces[int(input())]
        #Add piece and preferred square (Piece,Square) to application.
        player = players[player_i]
        application = (piece_to_play, board[player_i][square_i])
        #Saves square and piece each time they make a request.
        self.history_applications.append((application,player))
        return application,player

    def decide_bribe(self, application:Application, previous_bribes:dict[Application,int]) -> int:
        print("Application: "+str(application))
        #print("Applicant bribes (-1 are unknown): "+str(previous_bribes))
        print("Select bribe amount (value will be adjusted to the nearest limit). Min",MINIMUM_BRIBE,"Max",self.money)
        bribe = max(int(input()), MINIMUM_BRIBE)
        bribe = min(bribe, self.money)
        self.money -= bribe
        return bribe

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application, bribes:dict[Application,int]):
        palace = board[self.colour.value]
        print(palace)
        #print("Bribes: "+str(bribes))
        print("\nChoose which square to place the piece",application[0],". It must be unocupied:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
        square_i = int(input())
        while palace[square_i].piece:
            print("\nThat index is occupied. Please select another.")
            square_i = int(input())
        return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], bribes:dict[Application,int]):
        print("Applicant bribes: "+str(bribes))
        print("\nOut of the applicants, choose one. Type the index of the applicant:")
        chosen = list(bribes.keys())[int(input())]   #dict are ordered
        return chosen

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:dict[Application,int]):
        print("Applicant bribes for square "+str(board_square)+": "+str(bribes))
        print("\nOut of the two applicants, choose one. Type the index of the piece:")
        chosen = list(bribes.keys())[int(input())]   #dict are ordered
        return chosen

run()