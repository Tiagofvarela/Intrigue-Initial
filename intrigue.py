from intrigue_datatypes import Player_Colour, MINIMUM_BRIBE
from player import Player
from piece import Piece
from square import Square
from random import choice, randint
import sys

class Game():
    def __init__(self, player_types):
        self.boards = []
        self.players = []
        for i in range(4):
            self.boards.append([Square(0),Square(1),Square(2),Square(3)])
            print("Creating player of type",player_types[i],"(TODO)")
            if player_types[i] == 'random':
                self.players.append(PlayerRandom(Player_Colour(i)))
            elif player_types[i] == 'human':
                self.players.append(PlayerHuman(Player_Colour(i)))
            elif player_types[i] == 'honest':
                self.players.append(PlayerHonest(Player_Colour(i)))
            else:   #Implements a class that does nothing.
                self.players.append(Player(Player_Colour(i)))
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
        counter = 1
        while counter <= 6:
            print("\n############# ROUND ",counter," #############\n")
            for p in self.players:
                p:Player
                print("\n###",p.colour.name,"TURN ###\n")
                p.collect_earnings(self.boards)  
                p.resolve_applications(self.boards, self.players)
                if counter <= 4:
                    p.play_piece(self.boards, self.players)
                    p.play_piece(self.boards, self.players)
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

    def play_piece(self, board, players):
        #Choose random player and square.
        player_i = randint(0,3)
        while Player_Colour(player_i) == self.colour:
            player_i = randint(0,3)
        square_i = randint(0,3)

        #Select random piece.
        piece_to_play:Piece = choice(self.pieces)
        self.pieces.remove(piece_to_play)

        #Add piece and preferred square (Piece,Square) to application.
        player:Player = players[player_i]
        application = (piece_to_play, board[player_i][square_i])
        player.add_application(application)

        #Bribe is set to random value between min and a fourth of total.
        piece_to_play.set_bribe(randint(MINIMUM_BRIBE, max(round(self.money/4),MINIMUM_BRIBE) ))

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        #print(str(self.history_applications))

    def place_uncontested(self, board, players, application):
        #Choose random unocupied square and place piece in it.
        palace = board[self.colour.value]

        print(self.colour.name,": Placing application ",application,"in palace",palace)

        square_i = randint(0,3)
        while palace[square_i].piece:
            square_i = randint(0,3)
        palace[square_i].piece = application[0]
    
    def resolve_external_conflict(self, board, players, external_conflicts):   
        #Chooses random application.
        chosen = choice(external_conflicts)
        external_conflicts.remove(chosen)
        print(self.colour.name,": For this external conflict I choose ",chosen,"compared to",external_conflicts)
        return external_conflicts

    def resolve_internal_conflict(self, board, players, board_square, piece):
        #Randomly choose to replace or not.
        print(self.colour.name,": Resolving internal conflict with ",board_square.piece,"versus",piece)
        return choice([board_square.piece, piece])

class PlayerHonest(Player):
    def __init__(self, colour:Player_Colour):
        Player.__init__(self, colour)

    def play_piece(self, board, players):
        #Choose random player and square.
        player_i = randint(0,3)
        while Player_Colour(player_i) == self.colour:
            player_i = randint(0,3)
        square_i = randint(0,3)

        #Select random piece.
        piece_to_play:Piece = choice(self.pieces)
        self.pieces.remove(piece_to_play)

        #Add piece and preferred square (Piece,Square) to application.
        player:Player = players[player_i]
        square:Square = board[player_i][square_i]
        application = (piece_to_play, square)
        player.add_application(application)
        #TODO: Add action indicators for each action.

        #Bribe is set to the value of the square, or the as high as possible otherwise.
        piece_to_play.set_bribe(min(square.get_value(), self.money) )

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        #print(str(self.history_applications))

    def place_uncontested(self, board, players, application):
        #Attempts to place the piece in the requested square, else random.
        palace = board[self.colour.value]
        piece:Piece = application[0]
        square:Square = application[1]

        print(self.colour.name,": Placing application ",application,"in palace",palace)

        if not square.has_piece():
            square.set_piece(piece)
        else:
            #Set the piece at a random spot.
            square_i = randint(0,3)
            while palace[square_i].piece:
                square_i = randint(0,3)
            palace[square_i].piece = piece
    
    def resolve_external_conflict(self, board, players, external_conflicts):   
        #Chooses highest bribing piece.
        max_application = self.get_highest_bribe_application(external_conflicts)
        
        external_conflicts.remove(max_application)
        print(self.colour.name,": For this external conflict I choose ",max_application,"compared to",external_conflicts)
        return external_conflicts

    def resolve_internal_conflict(self, board, players, board_square, piece):
        #Chooses highest bribing piece.
        highest_piece, square = self.get_highest_bribe_application([(board_square.piece,board_square),(piece,board_square)])
        print(self.colour.name,": Resolving internal conflict with ",board_square.piece,"versus",piece)
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

    def play_piece(self, board, players):
        #Choose player, square and piece.
        player_i = self.colour.value
        while player_i == self.colour.value:
            print("Choose to which player you will send a piece. Type one of the following numerical values:"
            +"\n0 (Red), 1 (Green), 2 (Blue), 3 (Yellow)\n")
            player_i = int(input())

        print("Choose which square you want your piece to go to. Type one of the following numerical values:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)\n")
        square_i = int(input())

        print(self.pieces)
        print("Choose which piece you will send. Type the index corresponding to the piece:")
        piece_to_play:Piece = self.pieces.pop(int(input()))

        #Add piece and preferred square (Piece,Square) to application.
        player:Player = players[player_i]
        application = (piece_to_play, board[player_i][square_i])
        player.add_application(application)

        #Bribe is set to random value between min and a fourth of total.
        print("Select bribe amount. Min",MINIMUM_BRIBE,"Max",self.money)
        bribe = min(int(input()), self.money)
        piece_to_play.set_bribe(max(bribe, MINIMUM_BRIBE))
        
        #TODO: Adjust current money everytime a bribe is set, so future calculations don't overshoot available amount.
        #Bribe value is stored in piece.
        #self.spend_money(piece_to_play.get_bribe())

        #Saves square and piece each time they make a request.
        self.history_applications.append(application)
        #print(str(self.history_applications))

    def place_uncontested(self, board, players, application):
        palace = board[self.colour.value]

        print(palace)
        print("Choose which square to place the piece",application[0],". It must be unocupied:"
        +"\n0 (1000), 1 (6000), 2 (10000), 3 (3000)\n")
        square_i = int(input())
        while palace[square_i].has_piece():
            print("\nThat index is occupied. Please select another.")
            square_i = int(input())

        palace[square_i].piece = application[0]
    
    def resolve_external_conflict(self, board, players, external_conflicts):   
        print(repr(external_conflicts))
        print("Out of the applicants, choose one. Type the index of the applicant:\n")
        external_conflicts.pop(int(input()))
        return external_conflicts

    def resolve_internal_conflict(self, board, players, board_square, piece):
        print(self.colour.name,": Resolving internal conflict with ",[board_square.piece,piece])
        print("Out of the two pieces, choose one. Type the index of the piece:\n")        
        return [board_square.piece,piece][int(input())]

run()

#Game has board, Player has palace.
#Play piece: Check throught the board, select Square (set on Piece) and send to correct Player's palace.
#Resolve_External: Go through palace for each type (S,C,D,P) and pick all that are of same type. Use whatever criteria to pick one.
#Resolve_Internal: For each in palace, check all squares, if there's conflict, select one of the two and put/keep them on the Square.
#Uncontested: If no contest, place on table.