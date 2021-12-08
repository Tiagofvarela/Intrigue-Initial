from __future__ import annotations
from intrigue_datatypes import Piece_Type, MINIMUM_BRIBE

class Piece:    
    owner:player.Player
    type:Piece_Type
    bribe:int
    bribe_history:list[int]

    def __init__(self, player:player.Player, type:Piece_Type):
        """Creates a piece for Player player of Type type."""
        self.owner = player      #Piece's owner.
        self.type = type     #Type of piece
        #self.money_earned:int = 0      #Money accumulated by this piece.
        self.bribe = MINIMUM_BRIBE  #How much the owner will pay to get the piece where it is requesting.
        self.bribe_history = []
    
    #def earn_money(self, money: int):
        #"""Increases amount of money this piece has earned."""
        #self.money_earned += money
        #TODO: Consider having the pieces automatically increase their player's money when this value is updated.
        #Or, having the player walk through their pieces, earn money in each and receive it.

    def collect_bribe(self) -> int:
        """The caller collects the bribe from this piece, setting it to minimum and removing the money from the piece's owner."""
        self.owner.money -= self.bribe #Owner pays
        self.bribe_history.append(self.bribe)
        self.bribe = MINIMUM_BRIBE
        return self.bribe_history[-1]

    def __eq__(self, other):
        """WARNING: Only checks the piece type, not the owner! This is by design."""
        if isinstance(other, Piece):
            return self.type == other.type
    
    def __lt__(self, other):
        if isinstance(other, Piece):
            return self.type.value < other.type.value

    def __str__(self):
        return self.__repr__()#+" Earned: "+str(0)
    def __repr__(self):
        return str(self.owner.colour.name) + " " +str(self.type.name)

    
import player