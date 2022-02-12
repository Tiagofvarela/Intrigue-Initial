from __future__ import annotations
from piece import Piece

INDEX_VALUE_DICT = {0:1000, 1:6000, 2: 10000, 3:3000}
VALUE_INDEX_DICT = {1000:0, 6000:1, 10000:2, 3000:3}

class Square:
    """Represents a square in a player board, having an inherent value and a piece."""
    value:int
    piece:Piece|None
    owner:player.Player

    def __init__(self, index:int, owner:player.Player):
        """Creates a square of a given index (of the four available)."""         
        self.value = INDEX_VALUE_DICT[index]
        self.piece = None
        self.owner = owner

    
    def copy(self) -> Square:
        piece:Piece|None
        if self.piece:
            piece = self.piece.copy()
        else:
            piece = None
        square = Square(VALUE_INDEX_DICT[self.value], self.owner)
        square.piece = piece
        return square
    
    def __str__(self):
        return "|"+str(self.piece)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value)+"|"

import player