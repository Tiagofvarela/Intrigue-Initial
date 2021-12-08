from piece import Piece

class Square:
    
    def __init__(self, index):
        """Creates a square of a given index (of the four available)."""    
        def get_value_from_index(i) -> int:
            """Given a square index, returns its value."""
            if i == 0:
                return 1000
            elif i == 1:
                return 6000
            elif i == 2:
                return 10000
            else:
                return 3000        
        self.value = get_value_from_index(index)
        self.piece:Piece = None         #Piece in this square.

    def has_piece(self) -> bool:
        return self.piece != None
    def get_piece(self) -> Piece:
        """Returns the piece in this square."""
        return self.piece
    def get_value(self) -> int:
        """Returns this square's value."""
        return self.value
    def set_piece(self, piece:Piece):
        """Sets a piece to this square."""
        self.piece = piece
    
    def __str__(self):
        return "|"+str(self.piece)+" Value: "+str(self.value)+"|"
    def __repr__(self):
        return "|"+str(self.piece)+"|"