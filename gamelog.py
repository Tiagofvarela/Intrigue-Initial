from __future__ import annotations
from player import Application, Gameboard, Player
from square import Square

#List of rounds.
#Each Round:
    #Actions taken that round. (RED,GREEN,BLUE,YELLOW)
    #Game state end of round.

EarningsLog = list[Square]
ApplicationLog = list[tuple[Application, Player]]
ConflictLog = list[tuple[dict[Application, int], Application]]
PlacementLog = list[tuple[Application, int, Square]]

class GameLog():
    #Given player number, get corresponding player's log.
    player_logs:dict[int,PlayerLog]

    def __init__(self) -> None:
        self.player_logs = {}
        for i in range(4):
            self.player_logs[i] = PlayerLog()

    def log_turn(self,turn:int,player:int,earnings_log:EarningsLog,conflict_log:ConflictLog,
    placement_log:PlacementLog,application_log:ApplicationLog,gameboard:Gameboard):
        self.player_logs[player].log_turn(turn,earnings_log,conflict_log,placement_log,application_log,gameboard)


class PlayerLog():
    #Given turn number, get player's log for that turn.
    earnings_turn_log:dict[int,EarningsLog]
    conflicts_turn_log:dict[int,ConflictLog]
    placements_turn_log:dict[int,PlacementLog]
    applications_turn_log:dict[int,ApplicationLog]
    board_turn_log:dict[int,Gameboard]

    def __init__(self) -> None:
        self.earnings_turn_log = {}
        self.conflicts_turn_log = {}
        self.placements_turn_log = {}
        self.applications_turn_log = {}
        self.board_turn_log = {}

    def log_turn(self,turn:int,earnings_log:EarningsLog,conflict_log:ConflictLog,
    placement_log:PlacementLog,application_log:ApplicationLog,gameboard:Gameboard):
        self.earnings_turn_log[turn] = earnings_log
        self.conflicts_turn_log[turn] = conflict_log
        self.placements_turn_log[turn] = placement_log
        self.applications_turn_log[turn] = application_log
        self.board_turn_log[turn] = gameboard
        print("Turn logged.")
        # if(turn > 3):
        #      print(self.board_turn_log[3])
    

import square,intrigue