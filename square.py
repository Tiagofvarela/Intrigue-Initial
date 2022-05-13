from __future__ import annotations
from piece import Piece

INDEX_VALUE_DICT = {0:1, 1:6, 2: 10, 3:3}
VALUE_INDEX_DICT = {1:0, 6:1, 10:2, 3:3}

class Square:
    """Represents a square in a player board, having an inherent value and a piece."""
    value:int
    piece:Piece|None
    owner:player.Player_Colour

    def __init__(self, index:int, owner_colour:player.Player_Colour):
        """Creates a square of a given index (of the four available)."""         
        self.value = INDEX_VALUE_DICT[index]
        self.piece = None
        self.owner = owner_colour

    
    # def copy(self) -> Square:
    #     piece:Piece|None
    #     if self.piece:
    #         piece = self.piece.copy()
    #     else:
    #         piece = None
    #     square = Square(VALUE_INDEX_DICT[self.value], self.owner)
    #     square.piece = piece
    #     return square

    def get_index(self) -> tuple[int,int]:
        return self.owner.value,VALUE_INDEX_DICT[self.value]
    
    def __eq__(self, other: object) -> bool:
        """Checks the square value, owner, and piece."""
        if isinstance(other, Square):
            return self.value == other.value and self.owner == other.owner and self.piece == other.piece
        return False
    def __lt__(self, other):
        """Order isn't based just on value, but also on owner and piece."""
        if isinstance(other, Square):
            self_piece_value = 0 
            other_piece_value = 0
            if self.piece:
                self_piece_value = self.piece.type.value
            if other.piece:
                other_piece_value = other.piece.type.value
            return (self.value+self.owner.value+self_piece_value) < (other.value+other.owner.value+other_piece_value)
    def __hash__(self):
        piece_hash = -17
        if self.piece:
            piece_hash = hash(self.piece)
        return self.value*31**1 + self.owner.value*32**2 + piece_hash*31**3
    def __str__(self):
        return "|"+str(self.piece)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value*1000)+"|"

import player