from enum import Enum
from random import choice, randint, random
import sys

MINIMUM_BRIBE = 1000
STARTING_MONEY = 32000

class Piece_Type(Enum):
    SCIENTIST = 100
    DOCTOR = 101
    PRIEST = 102
    CLERK = 103
class Player_Colour(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3

class Player:
    """This class should hold only the information that's unique to it, and receive all other information it needs from Game.
    \nTo create new behaviours, extend this class and implement play_piece, place_uncontested, resolve_external_conflict, and
    resolve_internal_conflict."""
    
    def __init__(self, colour:Player_Colour):
        """Creates a new player with their colour, money, pieces and palace."""
        def generate_initial_pieces() -> list[Piece]:
            """Generates 8 pieces, two of each type, returned as a list."""
            pieces:list[Piece] = []
            def generate_two_pieces(piece_type:Piece_Type):
                return [Piece(self, piece_type), Piece(self, piece_type)]
            pieces += generate_two_pieces(Piece_Type.SCIENTIST)
            pieces += generate_two_pieces(Piece_Type.DOCTOR)
            pieces += generate_two_pieces(Piece_Type.PRIEST)
            pieces += generate_two_pieces(Piece_Type.CLERK)
            return pieces

        self.pieces:list[Piece] = generate_initial_pieces()
        self.money = STARTING_MONEY
        self.colour = colour
        self.palace_applicants = []     #List of pieces that are applying to palace.
        self.history_applications = []  #List of applications

    def collect_earnings(self, board):
        """Player sweeps through each square and collects their earnings.
        Earnings include salaries and bribes from applicants."""
        #Collect salaries.
        for i in range(len(board)):
            if Player_Colour(i) != self.colour: #Checks only others' palaces.
                for j in range(4):
                    square:Square = board[i][j]
                    if square.has_piece() and square.get_piece().get_player() == self:
                        #square.get_piece().earn_money(square.get_value())
                        self.receive_money(square.get_value())

        #Collect bribes.
        for piece, square in self.palace_applicants:
            piece:Piece
            piece.collect_bribe()

    
    def receive_money(self, money):
        """Increases current money by given money."""
        self.money += money
    def spend_money(self, money):
        """Player spends money amount of their money."""
        self.money -= money
    
    def play_piece(self, board, players):
        """Chooses a single piece and sends application to another player's palace, requesting a specific square.
        Piece disappears from hand. Registers which square and piece they sent."""
    def resolve_applications(self, board, players):
        """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
        and finally placing the remaining pieces."""
        palace = board[self.colour.value]

        print("Before external:",self.applicants_string())

        #Check external conflicts. 
        for type in range(100,104):
            external_conflicts = []
            for application in self.palace_applicants:
                if Piece_Type(type) == application[0].type:
                    external_conflicts.append(application)
            if len(external_conflicts) > 1:
                #Resolve external conflict for single conflict:
                external_conflicts = self.resolve_external_conflict(board, players, external_conflicts)
                #Remove current conflict from applications.
                self.palace_applicants = [a for a in self.palace_applicants if a not in external_conflicts]
        
        print("After external:",self.applicants_string())

        #Check internal conflicts.        
        for board_square in palace:
            board_piece:Piece = board_square.piece
            if not board_piece:
                continue
            resolved_applications = []
            for piece, square in self.palace_applicants.copy():
                if board_piece.type == piece.type:
                    #Resolve internal conflict for single conflict:
                    board_square.piece = self.resolve_internal_conflict(board, players, board_square, piece)
                    self.palace_applicants.remove( (piece,square) )

        print("After internal:",self.applicants_string())

        #Place remainder.
        for application in self.palace_applicants:
            self.place_uncontested(board, players, application)
            self.palace_applicants.remove( application )
        
    def place_uncontested(self, board, players, application):
        """Resolves an uncontested application, placing the piece in the palace."""
    def resolve_external_conflict(self, board, players, external_conflicts):
        """Given list of conflicting applications, picks one to keep. Returns remainder."""
    def resolve_internal_conflict(self, board, players, board_square, piece):
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""

    def add_application(self, application):
        """Adds a (piece,square) tuple as an application to this player's palace."""
        self.palace_applicants.append(application)

    def applicants_string(self) -> str:
        """Returns a string representing the applicants."""
        string = ""
        for piece,square in self.palace_applicants:
            string += str(piece)+"; "
        return string
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.colour == other.colour
    
    def __str__(self):
        return "\n"+str(self.colour.name)+" Pieces: "+str(self.pieces)+" Money: "+str(self.money)
    def __repr__(self):
        return str(self.colour)

class Piece:    
    def __init__(self, player:Player, type:Piece_Type):
        """Creates a piece for Player player of Type type."""
        self.owner:Player = player      #Piece's owner.
        self.type:Piece_Type = type     #Type of piece
        #self.money_earned:int = 0      #Money accumulated by this piece.
        self.bribe:int = MINIMUM_BRIBE  #How much the owner will pay to get the piece where it is requesting.
        self.bribe_history = []
    
    #def earn_money(self, money: int):
        #"""Increases amount of money this piece has earned."""
        #self.money_earned += money
        #TODO: Consider having the pieces automatically increase their player's money when this value is updated.
        #Or, having the player walk through their pieces, earn money in each and receive it.

    def collect_bribe(self) -> int:
        """The caller collects the bribe from this piece, setting it to minimum and removing the money from the piece's owner."""
        self.owner.spend_money(self.bribe) #Owner pays
        self.bribe_history.append(self.bribe)
        self.bribe = MINIMUM_BRIBE
        return self.bribe_history[-1]
        
    def set_bribe(self, money:int):
        """Owner sets bribe to amount money."""
        self.bribe = money
    def get_bribe(self) -> int:
        """Returns the amount of money a player is willing to pay to get their piece where they want it."""
        return self.bribe
    #def get_money_earned(self) -> int:
        #"""Returns the amount of money this piece has earned."""
        #return self.money_earned
    def get_player(self) -> Player:
        """Returns this piece's owner."""
        return self.owner

    def __eq__(self, other):
        """WARNING: Only checks the piece type, not the owner! This is by design."""
        if isinstance(other, Piece):
            return self.type == other.type
    
    def __lt__(self, other):
        if isinstance(other, Piece):
            return self.type.value < other.type.value

    def __str__(self):
        return self.__repr__()#+" Earned: "+str(0)
    def __repr__(self):
        return str(self.owner.colour.name) + " " +str(self.type.name)

class Square:
    
    def __init__(self, index):
        """Creates a square of a given index (of the four available)."""    
        def get_value_from_index(i) -> int:
            """Given a square index, returns its value."""
            if i == 0:
                return 1000
            elif i == 1:
                return 6000
            elif i == 2:
                return 10000
            else:
                return 3000        
        self.value = get_value_from_index(index)
        self.piece:Piece = None         #Piece in this square.

    def has_piece(self) -> bool:
        return self.piece != None
    def get_piece(self) -> Piece:
        """Returns the piece in this square."""
        return self.piece
    def get_value(self) -> int:
        """Returns this square's value."""
        return self.value
    def set_piece(self, piece:Piece):
        """Sets a piece to this square."""
        self.piece = piece
    
    def __str__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+"|"

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
                if counter > 4:
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