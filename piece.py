from __future__ import annotations
from intrigue_datatypes import Piece_Type

class Piece:    
    owner:player.Player_Colour
    type:Piece_Type

    def __init__(self, player_colour:player.Player_Colour, type:Piece_Type):
        """Creates a piece for Player player of Type type."""
        self.owner = player_colour      #Piece's owner.
        self.type = type                #Type of piece

    # def copy(self) -> Piece:
    #     return Piece(self.owner, self.type)

    def __eq__(self, other) -> bool:
        """Checks type and owner."""
        if isinstance(other, Piece):
            return self.type == other.type and self.owner == other.owner
        return False
    
    def __lt__(self, other):
        """Compares the sum of the type and owner values."""
        if isinstance(other, Piece):
            return (self.type.value+self.owner.value) < (other.type.value+other.owner.value)

    def __hash__(self):
        """If two objects are considered equal, then their hash is equal."""
        return self.type.value*31**1+self.owner.value*31**2

    def __str__(self):
        return self.__repr__()#+" Earned: "+str(0)
        
    def __repr__(self):
        return str(self.owner.name) + " " +str(self.type.name)
    
import player