from __future__ import annotations
from piece import Piece
from intrigue_datatypes import MINIMUM_BRIBE, Piece_Type, Player_Colour, STARTING_MONEY
from square import Square
import abc

Application = tuple[Piece,Square,int]
Gameboard = list[list[Square]]

def copy_application(application:Application) -> Application:
    return (application[0].copy(),application[1].copy(),application[2])
def copy_gameboard(board:Gameboard) -> Gameboard:
    copy:list[list[Square]] = []
    for palace in board:
        palace_copy:list[Square] = []
        for square in palace:
            palace_copy.append(square.copy())
        copy.append(palace_copy)
    return copy

class Player():
    """This class should hold only the information that's unique to it, and receive all other information it needs from Game.
    \nTo create new behaviours, extend this class and implement play_piece, place_uncontested, resolve_external_conflict, and
    resolve_internal_conflict."""

    pieces:list[Piece]
    money:int
    colour:Player_Colour
    palace_applicants:list[Application]                         #List of current applications.
    #opinionModel:dict[Player_Colour,dict[Player_Colour,int]]    #Dict of Player_Colour:{Player_Colour:(myOpinion,opinionOfMe)}
    
    def __init__(self, colour:Player_Colour, copy:Player = None):
        """Creates a new player with their colour, money, pieces and palace."""
        def generate_initial_pieces() -> list[Piece]:
            """Generates 8 pieces, two of each type, returned as a list."""
            pieces:list[Piece] = []
            def generate_two_pieces(piece_type:Piece_Type) -> list[Piece]:
                return [Piece(self.colour, piece_type), Piece(self.colour, piece_type)]
            pieces += generate_two_pieces(Piece_Type.SCIENTIST)
            pieces += generate_two_pieces(Piece_Type.DOCTOR)
            pieces += generate_two_pieces(Piece_Type.PRIEST)
            pieces += generate_two_pieces(Piece_Type.CLERK)
            return pieces
        # def generate_opinion_model() -> dict[Player_Colour,dict[Player_Colour,int]]:
        #     """Generates an opinion model, which models RED, BLUE, GREEN, YELLOW's opinions of others.\n
        #     model[Player][Target] = Player's opinion of Target"""
        #     model:dict[Player_Colour,dict[Player_Colour,int]] = {}
        #     for i in range(0,4):
        #         model[Player_Colour(i)] = {}
        #         for j in range(0,4):
        #             model[Player_Colour(i)][Player_Colour(j)] = 0
        #     return model
        
        #This instance should be a copy of the above player.
        if copy:
            self.money = copy.money
            self.colour = copy.colour
            self.pieces = []
            for piece in copy.pieces:
                self.pieces += [Piece(self.colour,piece.type)]
            self.palace_applicants = []
            for app_piece,app_square,bribe in copy.palace_applicants:
                self.palace_applicants += [(app_piece.copy(), app_square.copy(), bribe)]
            return
                

        self.money = STARTING_MONEY
        self.colour = colour
        self.pieces = generate_initial_pieces()
        self.palace_applicants = []     #List of current applications.
        #self.opinionModel = generate_opinion_model()

    def collect_earnings(self, board:Gameboard) -> list[Square]:
        """Player sweeps through each square and collects their earnings.
        Earnings include salaries and bribes from applicants."""
        collected_salaries: list[Square] = []
        print("\n# Collect Salaries #\n")
        for i in range(len(board)):
            if Player_Colour(i) != self.colour: #Checks only others' palaces.
                for j in range(4):
                    square = board[i][j]
                    if square.piece and square.piece.owner == self:
                        self.money += square.value
                        print(self.colour.name+" collected "+str(square.value*1000)+" from "+str(square)+" in "+square.owner.name+"'s palace.")
                        collected_salaries.append(square.copy())
        return collected_salaries

    ###TO IMPLEMENT###
    @abc.abstractmethod
    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        """Chooses a piece to send and a player to send it to. Returns Application and Player to send it to. Piece is removed from hand.
        \nRegisters which square and piece they have sent sent."""  
    @abc.abstractmethod      
    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application, bribes:dict[Application,int]) -> Square:
        """Resolves an uncontested application, placing the piece in the palace."""
    @abc.abstractmethod
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], bribes:dict[Application,int]) -> Application:
        """Given list of conflicting applications, picks one to keep and returns it."""
    @abc.abstractmethod
    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:dict[Application,int]) -> Application:
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""
    # @abc.abstractmethod
    # def decide_bribe(self, application:Application, previous_bribes:dict[Application,int]) -> int:
    #     """Decide bribe to give to player so they accept the application. 
    #     \nAmount is subtracted from account."""
    @abc.abstractmethod
    def decide_bribe(self, piece:Piece, square:Square) -> int:
        """Decide bribe to give to player so they accept the application. 
        \nAmount is subtracted from account."""
    ###################

    def resolve_applications(self, board:Gameboard, players:list[Player]) -> tuple[list[tuple[dict[Application, int], Application]], list[tuple[Application, int, Square]]]:
        """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
        and finally placing the remaining pieces. \nBribes are collected during this phase. Returns conflict_log and placement_log.
        conflict_log: List of (dictionary of conflict applications and corresponding bribe, chosen application)
        placement_log: List of (application, bribe, square_placed_in)"""
        print("\n# Resolve Conflicts #\n")
        print(self.colour.name+" applications:"+str(self.palace_applicants))
        
        palace = board[self.colour.value]

        conflicts_log:list[ tuple[dict[Application,int],Application] ] = [] #Logs all resolved conflicts: List of apps and bribes and chosen one.
        placement_log:list[tuple[Application, int, Square]]= []             #Logs all placements: App, bribe, square.
        bribes:dict[Application,int] = {}                                   #Saves resolved external applications for handling at the end.

        #Check external conflicts. 
        for type in range(100,104):
            external_conflicts:list[Application] = []
            for application in self.palace_applicants:
                if Piece_Type(type) == application[0].type:
                    external_conflicts.append(application)

            #Picks an application to keep if there are several conflicting ones.
            if len(external_conflicts) > 1:
                external_bribes = self.collect_bribes(external_conflicts)
                chosen_application = self.resolve_external_conflict(board, players, external_bribes)
                external_conflicts.remove(chosen_application)
                self.palace_applicants = [a for a in self.palace_applicants if a not in external_conflicts]
                #Save application to resolve later.
                bribes[chosen_application] = external_bribes[chosen_application]
                #Log Conflict Resolution
                print(self.colour.name+" discarded "+str(external_conflicts))
                conflicts_log.append( (external_bribes,copy_application(chosen_application)) )

        #Check internal conflicts.
        for board_square in palace:
            if board_square.piece:
                for application in self.palace_applicants.copy():
                    #Chooses which of the two pieces to keep.
                    if board_square.piece.type == application[0].type:
                        internal_bribes = self.collect_bribes([application,(board_square.piece,board_square, MINIMUM_BRIBE)])
                        #TODO: Figure out solution to asking players for a bribe.
                        chosen_application = self.resolve_internal_conflict(board, players, board_square, internal_bribes)
                        #random_app = PlayerRandom.resolve_internal_conflict(board, players, board_square, internal_bribes)
                        #Log placement
                        print(self.colour.name+" chose "+str(chosen_application[0])+" out of "+str(board_square.piece)+" and "+str(application[0]))
                        conflicts_log.append( (internal_bribes,copy_application(chosen_application)) )
                        placement_log.append( (copy_application(chosen_application),internal_bribes[chosen_application],board_square.copy()) )
                        #Place piece.
                        board_square.piece = chosen_application[0]                    
                        self.palace_applicants.remove(application)


        #Resolve remainder (bribes for already bribed taken from earlier). 
        applicants_not_already_bribed = [a for a in self.palace_applicants if a not in [app for app in bribes]]
        bribes.update(self.collect_bribes(applicants_not_already_bribed))
        for application in self.palace_applicants.copy():
            square = self.select_square_to_place(board, players, application, bribes)
            #Log placement
            print(self.colour.name+" took "+str(application)+" request and placed piece at "+repr(square))
            placement_log.append( (copy_application(application),bribes[application],square.copy()) )
            #Place piece
            square.piece = application[0]
            self.palace_applicants.remove(application)
        
        if len(self.palace_applicants) > 0:
            raise(Exception("Not all applications were handled."))

        return conflicts_log, placement_log

    def collect_bribes(self, applications:list[Application]) -> dict[Application,int]:
        """Collects all bribes from a list of applications and returns a dictionary of how much each application paid."""
        previous_bribes:dict[Application,int] = {application:-1 for application in applications}
        #Ask for bribe from each player.
        for application in applications:
            #bribe:int = application[0].owner.decide_bribe(application, previous_bribes)
            self.money += application[2]
            print(application[0].owner.name+" has paid "+str(application[2]*1000)+" for "+str(application))
            previous_bribes[application] = application[2]
        return previous_bribes    

    def get_max_value_unoccupied_squares(self, board:Gameboard):
        """Returns the most valuable and valid squares available on the board, or an empty list if there's no unoccupied square.
        \nA Square is invalid if it's impossible for self to send a Piece to it. (Ex: |Clerk||Doctor||None||Priest| 
        A player that cannot send a Scientist can never obtain the None Square in this palace, so it's an invalid Square.)"""
        most_valuable_squares:list[Square] = []
        current_max_value = 0
        #Look for most valuable Squares.
        for i in range(len(board)):
            if Player_Colour(i) == self.colour:
                continue
            for j in range(len(board[i])):
                square = board[i][j]
                #Valid if player has a Piece Type to send not already on the board.
                valid = len([p for p in self.pieces if p.type not in self.get_row_types(board[i]) ]) > 0
                #Square is occupied or invalid.
                if square.piece or not valid:
                    continue
                #Create new tier of max value or append to current tier.
                if square.value > current_max_value:
                    current_max_value = square.value
                    most_valuable_squares = [square]
                elif square.value == current_max_value:
                    most_valuable_squares.append(square)
        return most_valuable_squares  
        
    def get_max_bribe_application(self, bribes:dict[Application,int]):
        """Gets the application with the highest corresponding bribe."""
        max_application:Application
        max_bribe = 0
        #print(bribes)
        for application,bribe in bribes.items():
            if bribe > max_bribe:
                max_bribe = bribe
                max_application = application
        return max_application

    def get_row_pieces(self, row:list[Square]):
        """Given a row of squares, returns the pieces within."""
        return [s.piece for s in row if s.piece != None]

    def get_row_types(self, row:list[Square]):
        """Given a row of Squares, returns the types for all pieces within."""
        return [p.type for p in self.get_row_pieces(row)]

    def applicants_string(self) -> str:
        """Returns a string representing the applicants."""
        string = ""
        for piece,square,bribe in self.palace_applicants:
            string += str(piece)+"; "
        return string

    def copy(self):
        return Player(self.colour,self) #Copy of my self.

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.colour == other.colour
    
    def __hash__(self) -> int:
        return hash(self.colour)
    def __str__(self):
        return "\n"+str(self.colour.name)+" Pieces: "+str(self.pieces)+" Money: "+str(self.money*1000)
    def __repr__(self):
        return str(self.colour)