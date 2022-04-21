from __future__ import annotations
from intrigue_datatypes import Player_Colour
from player import Application, Gameboard, Player, EarningsLog, ConflictLog, PlacementLog, ApplicationLog
from square import Square

#List of rounds.
#Each Round:
    #Actions taken that round. (RED,GREEN,BLUE,YELLOW)
    #Game state end of round.

class GameLog():
    #Given player number, get corresponding player's log.
    player_logs:dict[int,PlayerLog]

    def __init__(self) -> None:
        self.player_logs = {}
        for i in range(4):
            self.player_logs[i] = PlayerLog()

    def log_turn(self,turn:int,player:int,earnings_log:EarningsLog,conflict_log:ConflictLog,
    placement_log:PlacementLog,application_log:ApplicationLog,gameboard:Gameboard):
        """Logs all the information pertaining to a turn."""
        self.player_logs[player].log_turn(turn,earnings_log,conflict_log,placement_log,application_log,gameboard)

    def get_conflicts_involving_player(self, player:Player_Colour, pertaining_to:Player_Colour = None) -> ConflictLog:
        """Gets all conflicts involving the Player player resolved by Player pertaining_to."""
        if pertaining_to:
            return self.player_logs[pertaining_to.value].get_conflicts_involving_player(player)
        else:
            conflict_list:list[ConflictLog] = []
            for playerLog in self.player_logs.values():
                conflict_list.append( playerLog.get_conflicts_involving_player(player) )
            return join_into_single_log(conflict_list)
    
    def count_conflicts(self, conflicts:ConflictLog, player:Player_Colour = None):
        """Given a list of conflicts, counts:
        \n  -Total conflicts.
        \n  -Times Player player is chosen or 0 if no player is given.
        \n  -Times Player player is not chosen or 0 if no player is given."""
        total = len(conflicts)
        wins = len([conflict for conflict in conflicts if conflict[1][0].owner == player]) if player else 0
        return total, wins, (total-wins if player else 0)


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

    def get_conflicts_involving_player(self, player:Player_Colour) -> ConflictLog:
        all_conflicts = join_into_single_log(self.conflicts_turn_log)
        desired_conflicts:ConflictLog = []
        for bribes,chosen_app in all_conflicts:
            if [app for app in bribes.keys() if app[0].owner.colour == player]:
                desired_conflicts.append( (bribes,chosen_app) )
        return desired_conflicts
    
def join_into_single_log(logs):
    """Given a dictionary or list of logs, joins them into a single list."""
    if isinstance(logs, dict):
        list_of_lists = [list for list in logs.values()]
    else:
        list_of_lists = logs
    #Turns list of lists into flat list.
    return [element for list in list_of_lists for element in list]