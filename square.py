from __future__ import annotations
from piece import Piece

INDEX_VALUE_DICT = {0:1, 1:6, 2: 10, 3:3}
VALUE_INDEX_DICT = {1:0, 6:1, 10:2, 3:3}

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
        return "|"+str(self.piece)+" Value: "+str(self.value*1000)+"|"

import player