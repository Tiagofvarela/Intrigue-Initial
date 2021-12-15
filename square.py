from __future__ import annotations
from piece import LogPiece, Piece
import copy

INDEX_VALUE_DICT = {0:1000, 1:6000, 2: 10000, 3:3000}

class Square:
    """Represents a square in a player board, having an inherent value and a piece."""
    value:int
    piece:Piece|None
    owner:player.Player

    def __init__(self, index:int, owner:player.Player):
        """Creates a square of a given index (of the four available)."""    
        def get_value_from_index(i) -> int:
            """Given an index for a Square, returns its value."""
            if i == 0:
                return 1000
            elif i == 1:
                return 6000
            elif i == 2:
                return 10000
            else:
                return 3000        
        self.value = INDEX_VALUE_DICT[index]
        self.piece = None
        self.owner = owner

    
    def __deepcopy__(self, memo) -> LogSquare:
        piece:LogPiece|None
        if self.piece:
            copied = copy.deepcopy(self.piece)
            if isinstance(copied, LogPiece):
                piece = copied
        else:
            piece = None
        return LogSquare(self.value, piece, self.owner.colour)
    
    def __str__(self):
        return "|"+str(self.piece)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value)+"|"

class LogSquare(Square):
    def __init__(self, value, piece, owner_colour):
        self.value = value
        self.piece = piece
        self.owner_colour = owner_colour

import player