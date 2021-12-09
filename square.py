from piece import Piece

class Square:
    """Represents a square in a player board, having an inherent value and a piece."""
    value:int
    piece:Piece

    def __init__(self, index:int):
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
        self.value = get_value_from_index(index)
        self.piece = None
    
    def __str__(self):
        return "|"+str(self.piece)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value)+"|"