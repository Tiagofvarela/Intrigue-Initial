from __future__ import annotations
import copy
from gamelog import GameLog
from intrigue_datatypes import PLAYER_COUNT, Player_Colour, MINIMUM_BRIBE
from player import Application, Gameboard, Player, EarningsLog, ConflictLog, PlacementLog, ApplicationLog#, copy_application, copy_gameboard
from piece import Piece
from square import Square
from random import choice, randint
import sys
#from colorama import Fore, Style

class Game():
    boards:Gameboard
    players:list[Player]
    turn_counter:int

    def __init__(self):
        self.boards = []
        self.players = []
        self.turn_counter = 0
        for i in range(PLAYER_COUNT):
            self.players.append( Player(Player_Colour(i)) )
            #Line of Squares owned by Player i.
            self.boards.append([Square(0,self.players[-1].colour),Square(1,self.players[-1].colour),Square(2,self.players[-1].colour),Square(3,self.players[-1].colour)])


    def get_legal_moves(self) -> list[tuple[EarningsLog,ConflictLog,PlacementLog,ApplicationLog]]:
        """Returns all possible moves the current player can make in the current state."""
        player = self.players[self.get_player_turn()]
        plays:list[tuple[EarningsLog,ConflictLog,PlacementLog,ApplicationLog]] = []

        earnings_log:EarningsLog = player.collect_earnings(self.boards)
        conflict_logs:list[ConflictLog] = player.get_valid_resolutions(self.boards)

        for conflict_log in conflict_logs:
            placement_logs = player.get_valid_placements(self.boards, conflict_log)
            for placement_log in placement_logs:
                application_logs = player.get_valid_applications(self.boards)
                for two_applications in application_logs:
                    application_log:ApplicationLog = list(two_applications)
                    plays.append( (earnings_log, conflict_log, placement_log, application_log) )
                if not application_logs:
                    plays.append( (earnings_log, conflict_log, placement_log, []) )
        return plays
        def uniq(lst):
            last = object()
            for item in lst:
                if item == last:
                    continue
                yield item
                last = item
        def sort_and_deduplicate(l):
            return list(uniq(sorted(l, reverse=True)))
        return sort_and_deduplicate(plays)
        clean_plays = []
        for play in plays:
            if play not in clean_plays:
                clean_plays.append(play)
            
        return clean_plays

    def get_random_legal_move(self) -> tuple[EarningsLog,ConflictLog,PlacementLog,ApplicationLog]:
        """Generates a random legal move and returns it. Only one move is generated."""
        player = self.players[self.get_player_turn()]
        board = self.boards
        conflict_log = player.get_random_valid_resolution(self.boards)
        return (player.collect_earnings(board), conflict_log, player.get_random_valid_placement(board,conflict_log), player.get_random_valid_application(board))

    def get_next_state(self, play:tuple[EarningsLog,ConflictLog,PlacementLog,ApplicationLog], debug=False) -> Game:
        """Applies the play to create a new state, which is returned. \n Current state is not modified."""
        state = copy.deepcopy(self)
        if debug:
            print(state)
        state.__play_move(play)
        return state

    def get_winner(self) -> int:
        "Return value of the winning player, or -1if it's not ended."
        if self.turn_counter < 20:
            return -1
        #TODO: Detect who is tying.
        winner = self.players[0]
        max_money = self.players[0].money
        tie = False
        for player in self.players:
            if player.money == max_money:
                tie = True
            if player.money > max_money:
                tie = False
                winner = player
                max_money = player.money
        if tie:
            return PLAYER_COUNT+1
        return winner.colour.value

    def __play_move(self, play:tuple[EarningsLog,ConflictLog,PlacementLog,ApplicationLog]) -> None:
        """Applies the play to the current state."""

        def collect_money(player:Player, app:Application):
            """Player collects money from Application."""
            # print(str(player.money) + " + " + str(app) + " = " + str(player.money + app[2]))
            player.money += app[2]
            self.players[app[0].owner.value].money -= app[2]

        earnings_log, conflicts_log, placement_log, application_log = play
        player = self.players[self.get_player_turn()]

        #Collect Earnings
        for square in earnings_log:
            player.money += square.value
        #Collect bribes from rejected entries
        for conflict_list, chosen_application in conflicts_log:
            for app in conflict_list:
                # print(app)
                if app is not chosen_application:
                    collect_money(player,app)

        #Collect from and place accepted pieces.
        for app, square in placement_log:
            collect_money(player, app)
            i,j = square.get_index()
            self.boards[i][j].piece = copy.deepcopy(app[0])
        player.palace_applicants = []

        #Send Pieces
        for app_piece, app_square, app_bribe in application_log:
            recipient = self.players[app_square.owner.value]
            recipient.palace_applicants.append( copy.deepcopy( (app_piece, app_square, app_bribe) ) )
            #Remove pieces from player sending application.
            player.pieces.remove(app_piece)

        self.turn_counter += 1

    def get_player_turn(self):
        """Returns the number of the player whose turn it is."""
        return (self.turn_counter) % PLAYER_COUNT
        self.player_counter = (self.player_counter+1) % PLAYER_COUNT
        self.turn_counter += 1

    def __str__(self):
        def line_str(squares:list[Square]) -> str:
            """Given a row of squares, prints their simple strings in a line."""
            line = ""
            for square in squares:
                line += str(square)
            return line
        
        board_rep = "________________________________________________________________________"
        for row in range(len(self.boards)):
            board_rep += "\n"+line_str(self.boards[row])+Player_Colour(row).name+" \nApplicants: "
            for piece, square, bribe in self.players[row].palace_applicants:
                board_rep += repr(piece)+" [Bribe "+str(bribe*1000)+"]; "
            board_rep +="\n"
        board_rep += "\n"
        for p in self.players:
            board_rep += str(p)
        board_rep += "\n________________________________________________________________________"
        return board_rep

    def __repr__(self):
        return self.__str__()
        
    # def play_game(self):
    #     """
    #     For each player:
    #         Collect earnings. (Sweep board and get money from each own piece.)\n
    #         Sweep and register each applicant.\n
    #         Accept applicants.\n
    #             Place uncontested ones.\n
    #             resolve_external_conflict()\n
    #             resolve_internal_conflict()\n
    #         play_piece() * 2
    #     """
    #     def player_send_piece(p:Player) -> tuple[Application,Player]:
    #         """Player p sends a piece to a player of their choosing."""
    #         app, player = p.play_piece(self.boards, self.players)
    #         #Remove piece from p and send to player.
    #         print(p.colour.name+" sent "+str(app[0])+" to "+player.colour.name)
    #         p.pieces.remove(app[0])
    #         player.palace_applicants.append(app)   
    #         return copy.deepcopy(app), copy.deepcopy(player)#copy_application(app), copy.deepcopy(player)

    #     #game_log:list[dict[str,Any]] = [{"earnings_log":[], }]
    #     gamelog = GameLog()
        
    #     counter = 1
    #     while counter <= 6:
    #         print("\n############# ROUND ",counter,"#############\n")
    #         for p in self.players:
    #             print("\n###",p.colour.name,"TURN ###\n")

    #             application_log:list[tuple[Application,Player]] = []
    #             earnings_log = p.collect_earnings(self.boards)  
    #             conflict_log, placement_log = p.resolve_applications(self.boards, self.players)
    #             if counter <= 4:
    #                 print("\n# Send Pieces #\n")
    #                 application_log.append( player_send_piece(p) )
    #                 application_log.append( player_send_piece(p) )
    #             print(self)
    #             gamelog.log_turn(counter,p.colour.value,earnings_log,conflict_log,placement_log,application_log,copy_gameboard(self.boards))
    #             #print(gamelog.count_conflicts(gamelog.get_conflicts_involving_player(p.colour), p.colour))    #Conflict methods debug
    #             print("\n###",p.colour.name,"TURN  End ###\nPress enter to continue.")
    #             input()
    #         counter += 1

    # def __deepcopy__(self, memo):
    #     empty:list = []
    #     existing = memo.get(self, empty)
    #     if existing is not empty:
    #         print ('  ALREADY COPIED TO', repr(existing))
    #         return existing

    #     #Deep copy each existing attribute.
    #     dup = Graph(copy.deepcopy(self.name, memo), [])
    #     print ('  COPYING TO', repr(dup))
    #     memo[self] = dup
    #     for c in self.connections:
    #         dup.addConnection(copy.deepcopy(c, memo))
    #     return dup
    #     return Game(copy.deepcopy(self.name, memo))

def run():
    player_types = sys.argv
    player_types.pop(0)

    game = Game(player_types)
    game.play_game()
    print("\nGame end!\n")
    # game2 = Game(player_types, game.boards, game.players, game.player_counter)
    # print("Running!")

    # print(game)
    # print(game2)

# run()