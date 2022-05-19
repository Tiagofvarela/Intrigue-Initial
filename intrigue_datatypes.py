from enum import Enum
import colorama                     # type: ignore
from colorama import Fore, Style    # type: ignore
colorama.init()

MINIMUM_BRIBE = 1
STARTING_MONEY = 32
PLAYER_COUNT = 4

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

    def clean_name(self) -> str:
        if self.value == 0:
            return "RED"
        elif self.value == 1:
            return "GREEN"
        elif self.value == 2:
            return "BLUE"
        else:
            return "YELLOW"