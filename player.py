from __future__ import annotations
from piece import Piece
from intrigue_datatypes import Piece_Type, Player_Colour, STARTING_MONEY
from square import Square
import abc

Application = tuple[Piece,Square]
Gameboard = list[list[Square]]

class Player(metaclass=abc.ABCMeta):
    """This class should hold only the information that's unique to it, and receive all other information it needs from Game.
    \nTo create new behaviours, extend this class and implement play_piece, place_uncontested, resolve_external_conflict, and
    resolve_internal_conflict."""

    pieces:list[Piece]
    money:int
    colour:Player_Colour
    palace_applicants:list[Application]     #List of current applications.
    history_applications:list[tuple[Application,Player]]  #List of previous applications.
    
    def __init__(self, colour:Player_Colour):
        """Creates a new player with their colour, money, pieces and palace."""
        def generate_initial_pieces() -> list[Piece]:
            """Generates 8 pieces, two of each type, returned as a list."""
            pieces:list[Piece] = []
            def generate_two_pieces(piece_type:Piece_Type) -> list[Piece]:
                return [Piece(self, piece_type), Piece(self, piece_type)]
            pieces += generate_two_pieces(Piece_Type.SCIENTIST)
            pieces += generate_two_pieces(Piece_Type.DOCTOR)
            pieces += generate_two_pieces(Piece_Type.PRIEST)
            pieces += generate_two_pieces(Piece_Type.CLERK)
            return pieces

        self.pieces = generate_initial_pieces()
        self.money = STARTING_MONEY
        self.colour = colour
        self.palace_applicants = []     #List of current applications.
        self.history_applications = []  #List of previous applications.

    def collect_earnings(self, board:Gameboard):
        """Player sweeps through each square and collects their earnings.
        Earnings include salaries and bribes from applicants."""
        print("\n# Collect Salaries #\n")
        for i in range(len(board)):
            if Player_Colour(i) != self.colour: #Checks only others' palaces.
                for j in range(4):
                    square = board[i][j]
                    if square.piece and square.piece.owner == self:
                        #square.get_piece().earn_money(square.get_value())
                        self.money += square.value
                        print(self.colour.name+" collected "+str(square.value)+" from "+str(square)+" in "+Player_Colour(i).name+"'s palace.")

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
    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:dict[Application,int]) -> Piece:
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""
    @abc.abstractmethod
    def decide_bribe(self, application:Application, previous_bribes:dict[Application,int]) -> int:
        """Decide bribe to give to player so they accept the application. 
        \nAmount is subtracted from account."""
    ###################

    def resolve_applications(self, board:Gameboard, players:list[Player]):
        """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
        and finally placing the remaining pieces. \nBribes are collected during this phase."""
        print("\n# Resolve Conflicts #\n")
        print(self.colour.name+" applications:"+str(self.palace_applicants))
        
        palace = board[self.colour.value]

        #Check external conflicts. 
        for type in range(100,104):
            external_conflicts:list[Application] = []
            for application in self.palace_applicants:
                if Piece_Type(type) == application[0].type:
                    external_conflicts.append(application)

            #Picks an application to keep if there are several conflicting ones.
            if len(external_conflicts) > 1:
                bribes = self.collect_bribes(external_conflicts)
                chosen_application = self.resolve_external_conflict(board, players, bribes)
                external_conflicts.remove(chosen_application)
                self.palace_applicants = [a for a in self.palace_applicants if a not in external_conflicts]
                print(self.colour.name+" discarded "+str(external_conflicts))

        #Check internal conflicts.
        for board_square in palace:
            if board_square.piece:
                for application in self.palace_applicants.copy():
                    #Chooses which of the two pieces to keep.
                    if board_square.piece.type == application[0].type:
                        bribes = self.collect_bribes([application,(board_square.piece,board_square)])
                        chosen_piece = self.resolve_internal_conflict(board, players, board_square, bribes)
                        print(self.colour.name+" chose "+str(chosen_piece)+" out of "+str(board_square.piece)+" and "+str(application[0]))
                        board_square.piece = chosen_piece                    
                        self.palace_applicants.remove(application)

        #Resolve remainder.
        bribes = self.collect_bribes(self.palace_applicants)
        for application in self.palace_applicants.copy():
            square = self.select_square_to_place(board, players, application, bribes)
            print(self.colour.name+" took "+str(application)+" request and placed piece at "+repr(square))
            square.piece = application[0]
            self.palace_applicants.remove(application)
        
        if len(self.palace_applicants) > 0:
            raise(Exception("Not all applications were handled."))

    def collect_bribes(self, applications:list[Application]) -> dict[Application,int]:
        """Collects all bribes from a list of applications and returns a dictionary of how much each application paid."""
        previous_bribes:dict[Application,int] = {application:-1 for application in applications}
        #Ask for bribe from each player.
        for application in applications:
            bribe = application[0].owner.decide_bribe(application, self, previous_bribes)
            self.money += bribe
            print(application[0].owner.colour.name+" has paid "+str(bribe)+" for "+str(application))
            previous_bribes[application] = bribe
        return previous_bribes
    
    # def log_bribe(self, bribe:int, application:Application) -> int:
    #     """Registers the bribe as having been received, increasing own money."""
    #     self.money += bribe
    #     print(application[0].owner.colour.name+" has paid "+str(bribe)+" for "+str(application))    
        
    def get_max_bribe_application(self, bribes:dict[Application,int]):
        """Gets the application with the highest corresponding bribe."""
        max_application:Application
        max_bribe = 0
        print(bribes)
        for application,bribe in bribes.items():
            if bribe > max_bribe:
                max_bribe = bribe
                max_application = application
        return max_application

    def applicants_string(self) -> str:
        """Returns a string representing the applicants."""
        string = ""
        for piece,square in self.palace_applicants:
            string += str(piece)+"; "
        return string
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.colour == other.colour
    
    def __hash__(self) -> int:
        return hash(self.colour)
    def __str__(self):
        return "\n"+str(self.colour.name)+" Pieces: "+str(self.pieces)+" Money: "+str(self.money)
    def __repr__(self):
        return str(self.colour)