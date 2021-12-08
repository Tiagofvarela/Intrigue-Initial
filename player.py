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
        #Collect salaries.
        for i in range(len(board)):
            if Player_Colour(i) != self.colour: #Checks only others' palaces.
                for j in range(4):
                    square = board[i][j]
                    if square.has_piece() and square.get_piece().get_player() == self:
                        #square.get_piece().earn_money(square.get_value())
                        self.receive_money(square.get_value())

        #Collect bribes.
        for piece, square in self.palace_applicants:
            piece.collect_bribe()
    
    def receive_money(self, money:int):
        """Increases current money by given money."""
        self.money += money
    def spend_money(self, money:int):
        """Player spends money amount of their money."""
        self.money -= money
    
    ###TO IMPLEMENT###
    @abc.abstractmethod
    def play_piece(self, board:Gameboard, players:list[Player]):
        """Chooses a single piece and sends application to another player's palace, requesting a specific square.
        Piece disappears from hand. Registers which square and piece they sent."""  
    @abc.abstractmethod      
    def place_uncontested(self, board:Gameboard, players:list[Player], application:Application):
        """Resolves an uncontested application, placing the piece in the palace."""
    @abc.abstractmethod
    def resolve_external_conflict(self, board:Gameboard, players:list[Player], external_conflicts:list[Application]) -> list[Application]:
        """Given list of conflicting applications, picks one to keep. Returns remainder."""
    @abc.abstractmethod
    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, piece:Piece) -> Piece:
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""
    ###################

    def resolve_applications(self, board:Gameboard, players:list[Player]):
        """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
        and finally placing the remaining pieces."""
        palace = board[self.colour.value]

        print("Before external:",self.applicants_string())

        #Check external conflicts. 
        for type in range(100,104):
            external_conflicts:list[Application] = []
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
            if board_square.has_piece():
                for piece, square in self.palace_applicants.copy():
                    if board_square.get_piece().type == piece.type:
                        #Resolve internal conflict for single conflict:
                        board_square.piece = self.resolve_internal_conflict(board, players, board_square, piece)
                        self.palace_applicants.remove( (piece,square) )

        print("After internal:",self.applicants_string())

        #Place remainder.
        for application in self.palace_applicants:
            self.place_uncontested(board, players, application)
            self.palace_applicants.remove( application )

    def add_application(self, application:Application):
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