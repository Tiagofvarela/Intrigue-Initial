from __future__ import annotations
from intrigue_datatypes import Piece_Type

class Piece:    
    owner:player.Player
    type:Piece_Type

    def __init__(self, player:player.Player, type:Piece_Type):
        """Creates a piece for Player player of Type type."""
        self.owner = player      #Piece's owner.
        self.type = type     #Type of piece

    def copy(self) -> Piece:
        return Piece(self.owner, self.type)

    def __eq__(self, other):
        """Checks type and owner, making for a unique piece (with a clone)."""
        if isinstance(other, Piece):
            return self.type == other.type and self.owner == other.owner
    
    def __lt__(self, other):
        if isinstance(other, Piece):
            return self.type.value < other.type.value

    def __hash__(self):
        return hash((self.type, self.owner))

    def __str__(self):
        return self.__repr__()#+" Earned: "+str(0)
    def __repr__(self):
        return str(self.owner.colour.name) + " " +str(self.type.name)
    
import player