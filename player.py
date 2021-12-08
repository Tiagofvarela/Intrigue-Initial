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
    history_applications:list[Application]  #List of previous applications.
    
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

        print("\n# Collect Bribes #\n")
        for piece, square in self.palace_applicants:
            print(self.colour.name+" collected "+str(piece.collect_bribe())+" bribe from "+piece.owner.colour.name+" to place "+str(piece)+" in "+str(square))            
    
    ###TO IMPLEMENT###
    @abc.abstractmethod
    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        """Chooses a piece to send and a player to send it to. Sets bribe on the piece. Returns Application and Player to send it to.
        \nRegisters which square and piece they have sent sent."""  
    @abc.abstractmethod      
    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application) -> Square:
        """Resolves an uncontested application, placing the piece in the palace."""
    @abc.abstractmethod
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], external_conflicts:list[Application]) -> Application:
        """Given list of conflicting applications, picks one to keep and returns it."""
    @abc.abstractmethod
    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, piece:Piece) -> Piece:
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""
    ###################

    def resolve_applications(self, board:Gameboard, players:list[Player]):
        """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
        and finally placing the remaining pieces."""
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
                chosen_application = self.resolve_external_conflict(board, players, external_conflicts)
                external_conflicts.remove(chosen_application)
                self.palace_applicants = [a for a in self.palace_applicants if a not in external_conflicts]
                print(self.colour.name+" discarded "+str(external_conflicts))

        #Check internal conflicts.
        for board_square in palace:
            if board_square.piece:
                for piece, square in self.palace_applicants.copy():
                    #Chooses which of the two pieces to keep.
                    if board_square.piece.type == piece.type:
                        chosen_piece = self.resolve_internal_conflict(board, players, board_square, piece)
                        print(self.colour.name+" chose "+str(chosen_piece)+" out of "+str(board_square.piece)+" and "+str(piece))
                        board_square.piece = chosen_piece                    
                        self.palace_applicants.remove( (piece,square) )

        #Place remainder.
        for application in self.palace_applicants.copy():
            square = self.select_square_to_place(board, players, application)
            print(self.colour.name+" took "+str(application)+" request and placed piece at "+str(square)+" in palace",palace)
            square.piece = application[0]
            self.palace_applicants.remove( application )
        
        if len(self.palace_applicants) > 0:
            raise(Exception("Not all applications were handled."))

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