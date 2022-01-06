from enum import Enum
import colorama
from colorama import Fore, Style
colorama.init()

MINIMUM_BRIBE = 1000
STARTING_MONEY = 32000

class Piece_Type(Enum):
    SCIENTIST = 100
    DOCTOR = 101
    PRIEST = 102
    CLERK = 103

class Player_Colour(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3

    @property
    def name(self):
        return eval('Fore.'+super().name)+super().name+Style.RESET_ALL