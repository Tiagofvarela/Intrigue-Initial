from __future__ import annotations
from intrigue_datatypes import Player_Colour, MINIMUM_BRIBE
from player import Application, Gameboard, Player
from piece import Piece
from square import Square
from random import choice, randint
import sys

class Game():
    def __init__(self, player_types:list[str]):
        self.boards = []
        self.players = []
        try:
            for i in range(4):
                self.boards.append([Square(0),Square(1),Square(2),Square(3)])
                print("Creating player of type",player_types[i])
                if player_types[i] == 'random':
                    self.players.append(PlayerRandom(Player_Colour(i)))
                elif player_types[i] == 'human':
                    self.players.append(PlayerHuman(Player_Colour(i)))
                elif player_types[i] == 'honest':
                    self.players.append(PlayerHonest(Player_Colour(i)))
                else:
                    raise Exception(player_types[i]+" is an invalid player type.")
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
            play_piece() * 2\n
            EXTRA: Update bribes (Ideally this would be done when each player is negotiating, not all at once at the end of a turn.)
        """
        def player_send_piece(p:Player):
            app, player = p.play_piece(self.boards, self.players)
            #Remove piece from p and send to player.
            print(p.colour.name+" sent "+str(app[0])+" to "+player.colour.name)
            p.pieces.remove(app[0])
            player.palace_applicants.append(app)            
        
        counter = 1
        while counter <= 6:
            print("\n############# ROUND ",counter," #############\n")
            for p in self.players:
                p:Player
                print("\n###",p.colour.name,"TURN ###\n")
                p.collect_earnings(self.boards)  
                p.resolve_applications(self.boards, self.players)
                if counter <= 4:
                    print("\n# Send Pieces #\n")
                    player_send_piece(p)
                    player_send_piece(p)
                print(self)
            counter += 1

    def __str__(self):
        board_rep = "________________________________________________________________________"
        for row in range(len(self.boards)):
            board_rep += "\n"+str(self.boards[row])+Player_Colour(row).name+" \nApplicants: "
            for piece, square in self.players[row].palace_applicants:
                board_rep += repr(piece)+" "+str(piece.bribe)+"; "
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
        #self.pieces.remove(piece_to_play)

        #Add piece and preferred square (Piece,Square) to application.
        player = players[player_i]
        application = (piece_to_play, board[player_i][square_i])
        #player.palace_applicants.append(application)

        #Bribe is set to random value between min and a fourth of total.
        piece_to_play.bribe = randint(MINIMUM_BRIBE, max(round(self.money/4),MINIMUM_BRIBE) )

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        return application,player

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application):
        #Choose random unocupied square and place piece in it.
        palace = board[self.colour.value]

        #print(self.colour.name,": Placing application ",application,"in palace",palace)

        square_i = randint(0,3)
        while palace[square_i].piece:
            square_i = randint(0,3)
        #palace[square_i].piece = application[0]
        return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], external_conflicts:list[Application]):  
        #Chooses random application.
        chosen = choice(external_conflicts)
        #external_conflicts.remove(chosen)
        #print(self.colour.name,": For this external conflict I choose ",chosen,"compared to",external_conflicts)
        return chosen

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, piece:Piece):
        #Randomly choose to replace or not.
        return choice([board_square.piece, piece])

class PlayerHonest(Player):
    def __init__(self, colour:Player_Colour):
        Player.__init__(self, colour)

    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        #Choose random player and square.
        player_i = randint(0,3)
        while Player_Colour(player_i) == self.colour:
            player_i = randint(0,3)
        square_i = randint(0,3)

        #Select random piece.
        piece_to_play:Piece = choice(self.pieces)
        #self.pieces.remove(piece_to_play)

        #Add piece and preferred square (Piece,Square) to application.
        player = players[player_i]
        square = board[player_i][square_i]
        application = (piece_to_play, square)
        #player.palace_applicants.append(application)

        #Bribe is set to the value of the square, or the as high as possible otherwise.
        piece_to_play.bribe = min(square.value, self.money) 

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        return application,player

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application):
        #Attempts to place the piece in the requested square, else random.
        palace = board[self.colour.value]
        piece,square = application
        if not square.piece:
            return square
        else:
            #Set the piece at a random spot.
            square_i = randint(0,3)
            while palace[square_i].piece:
                square_i = randint(0,3)
            return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], external_conflicts:list[Application]):
        #Chooses highest bribing piece.
        max_application = self.get_highest_bribe_application(external_conflicts)
        return max_application

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, piece:Piece):
        #Chooses highest bribing piece.
        highest_piece, square = self.get_highest_bribe_application([(board_square.piece,board_square),(piece,board_square)])
        return highest_piece
        
    def get_highest_bribe_application(self, applications):
        """Given a list of applications, chooses the application with the highest bribe."""
        max_application = None
        max = 0
        for piece,square in applications:
            if piece.bribe_history[-1] > max:
                max_application = (piece,square)
        return max_application

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

        #Bribe is set to random value between min and a fourth of total.
        print("Select bribe amount. Min",MINIMUM_BRIBE,"Max",self.money)
        bribe = min(int(input()), self.money)
        piece_to_play.bribe = max(bribe, MINIMUM_BRIBE)
        
        #TODO: Adjust current money everytime a bribe is set, so future calculations don't overshoot available amount.
        #Bribe value is stored in piece.
        #self.spend_money(piece_to_play.get_bribe())

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        return application,player

    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application):
        palace = board[self.colour.value]

        print(palace)
        print("\nChoose which square to place the piece",application[0],". It must be unocupied:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)")
        square_i = int(input())
        while palace[square_i].piece:
            print("\nThat index is occupied. Please select another.")
            square_i = int(input())
        return palace[square_i]
    
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], external_conflicts:list[Application]):
        print("\nOut of the applicants, choose one. Type the index of the applicant:")
        chosen = external_conflicts[int(input())]
        return chosen

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, piece:Piece):
        print("\nOut of the two pieces, choose one. Type the index of the piece:")
        return [board_square.piece,piece][int(input())]

run()