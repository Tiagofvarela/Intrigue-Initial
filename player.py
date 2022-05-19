from __future__ import annotations
import copy
from itertools import combinations, product, permutations
import random
from xmlrpc.client import Boolean
from piece import Piece
from intrigue_datatypes import MINIMUM_BRIBE, PLAYER_COUNT, Piece_Type, Player_Colour, STARTING_MONEY
from square import Square
from random import choice, randint

class Player():
    """This class should hold only the information that's unique to it, and receive all other information it needs from Game.
    \nTo create new behaviours, extend this class and implement play_piece, place_uncontested, resolve_external_conflict, and
    resolve_internal_conflict."""

    pieces:list[Piece]
    money:int
    colour:Player_Colour
    palace_applicants:list[Application]                         #List of current applications.
    #opinionModel:dict[Player_Colour,dict[Player_Colour,int]]    #Dict of Player_Colour:{Player_Colour:(myOpinion,opinionOfMe)}
    
    def __init__(self, colour:Player_Colour):#, copy:Player|None = None):
        """Creates a new player with their colour, money, pieces and palace."""
        def generate_initial_pieces() -> list[Piece]:
            """Generates 8 pieces, two of each type, returned as a list."""
            pieces:list[Piece] = []
            def generate_two_pieces(piece_type:Piece_Type) -> list[Piece]:
                return [Piece(self.colour, piece_type), Piece(self.colour, piece_type)]
            pieces += generate_two_pieces(Piece_Type.SCIENTIST)
            pieces += generate_two_pieces(Piece_Type.DOCTOR)
            pieces += generate_two_pieces(Piece_Type.PRIEST)
            pieces += generate_two_pieces(Piece_Type.CLERK)
            return pieces
        # def generate_opinion_model() -> dict[Player_Colour,dict[Player_Colour,int]]:
        #     """Generates an opinion model, which models RED, BLUE, GREEN, YELLOW's opinions of others.\n
        #     model[Player][Target] = Player's opinion of Target"""
        #     model:dict[Player_Colour,dict[Player_Colour,int]] = {}
        #     for i in range(0,4):
        #         model[Player_Colour(i)] = {}
        #         for j in range(0,4):
        #             model[Player_Colour(i)][Player_Colour(j)] = 0
        #     return model                

        self.money = STARTING_MONEY
        self.colour = colour
        self.pieces = generate_initial_pieces()
        self.palace_applicants = []     #List of current applications.
        #self.opinionModel = generate_opinion_model()

    def collect_earnings(self, board:Gameboard) -> list[Square]:
        """Player sweeps through each square and collects their earnings. Returns list of squares to collect from.
        Player money value is not changed."""
        collected_salaries: list[Square] = []
        for i in range(len(board)):
            if Player_Colour(i) != self.colour: #Checks only others' palaces.
                for j in range(4):
                    square = board[i][j]
                    if square.piece and square.piece.owner == self.colour:
                        collected_salaries.append( copy.deepcopy(square) )
        return collected_salaries

    ###Random Implementation###

    def play_piece(self, board:Gameboard, players:list[Player]) -> tuple[Application,Player]:
        """Chooses a piece to send and a player to send it to. Returns Application and Player to send it to. Piece is removed from hand.
        \nRegisters which square and piece they have sent sent."""  
        #Choose random player and square.
        player_i = randint(0,3)
        while Player_Colour(player_i) == self.colour:
            player_i = randint(0,3)
        square_i = randint(0,3)
        #Select random piece.
        piece_to_play = choice(self.pieces)
        #Add piece and preferred square (Piece,Square) to application.
        player = players[player_i]
        square_to_send_to = board[player_i][square_i]

        application = (piece_to_play, square_to_send_to, self.decide_bribe(piece_to_play,square_to_send_to))
        return application,player
   
    def select_square_to_place(self, board:Gameboard, players:list[Player], application:Application, bribes:list[Application]) -> Square:
        """Resolves an uncontested application, placing the piece in the palace."""
        #Choose random unocupied square and place piece in it.
        palace = board[self.colour.value]
        square_i = randint(0,3)
        while palace[square_i].piece:
            square_i = randint(0,3)
        #palace[square_i].piece = application[0]
        return palace[square_i]

    def resolve_external_conflict(self, board:Gameboard, players:list[Player], bribes:list[Application]) -> Application:
        """Given list of conflicting applications, picks one to keep and returns it."""
        #Chooses random application.
        chosen = choice(bribes)
        return chosen

    def resolve_internal_conflict(self, board:Gameboard, players:list[Player], board_square:Square, bribes:list[Application]) -> Application:
        """Given the conflicting square and piece, chooses a piece to keep and returns it."""
        #Randomly choose to replace or not.
        return choice(bribes)

    def decide_bribe(self, piece:Piece, square:Square) -> int:
        """Decide bribe to give to player so they accept the application. 
        \nAmount is subtracted from account."""
        #Bribe is set to random value between min and a fourth of total.
        bribe = randint(MINIMUM_BRIBE, max(round(self.money/4),MINIMUM_BRIBE) )
        #self.money -= bribe
        return 1#bribe
    ###################

    # def resolve_applications(self, board:Gameboard, players:list[Player]) -> tuple[list[tuple[list[Application], Application]], list[tuple[Application, int, Square]]]:
    #     """Resolves applications, first detecting and resolving external conflicts, then internal conflicts,
    #     and finally placing the remaining pieces. \nBribes are collected during this phase. Returns conflict_log and placement_log.
    #     conflict_log: List of (list of conflict applications and corresponding bribe, chosen application)
    #     placement_log: List of (application, bribe, square_placed_in)"""
        # print("\n# Resolve Conflicts #\n")
        # print(self.colour.name+" applications:"+str(self.palace_applicants))
        
        # palace = board[self.colour.value]

        # conflicts_log:list[ tuple[list[Application],Application] ] = [] #Logs all resolved conflicts: List of apps and bribes and chosen one.
        # placement_log:list[tuple[Application, int, Square]]= []             #Logs all placements: App, bribe, square.
        # bribes:list[Application] = []                                       #Saves resolved external applications for handling at the end.

        # #Check external conflicts. 
        # for type in range(100,104):
        #     applications_of_type:list[Application] = self.__find_type_applications(Piece_Type(type), self.palace_applicants)

        #     #Picks an application to keep if there are several conflicting ones.
        #     if len(applications_of_type) > 1:
        #         external_bribes = self.collect_bribes(applications_of_type)
        #         chosen_application = self.resolve_external_conflict(board, players, external_bribes)
        #         applications_of_type.remove(chosen_application)
        #         self.palace_applicants = [a for a in self.palace_applicants if a not in applications_of_type]
        #         #Save application to resolve later.
        #         bribes.append(chosen_application)
        #         #Log Conflict Resolution
        #         print(self.colour.name+" discarded "+str(applications_of_type))
        #         conflicts_log.append( (external_bribes,copy_application(chosen_application)) )

        # #Check internal conflicts.
        # for board_square in palace:
        #     if board_square.piece:
        #         for application in self.palace_applicants.copy():
        #             #Chooses which of the two pieces to keep.
        #             if board_square.piece.type == application[0].type:
        #                 internal_bribes = self.collect_bribes([application,(board_square.piece,board_square, MINIMUM_BRIBE)])
        #                 #TODO: Figure out solution to asking players for a bribe.
        #                 chosen_application = self.resolve_internal_conflict(board, players, board_square, internal_bribes)
        #                 #random_app = PlayerRandom.resolve_internal_conflict(board, players, board_square, internal_bribes)
        #                 #Log placement
        #                 print(self.colour.name+" chose "+str(chosen_application[0])+" out of "+str(board_square.piece)+" and "+str(application[0]))
        #                 conflicts_log.append( (internal_bribes,copy_application(chosen_application)) )
        #                 placement_log.append( (copy_application(chosen_application),chosen_application[2],board_square.copy()) )
        #                 #Place piece.
        #                 board_square.piece = chosen_application[0]                    
        #                 self.palace_applicants.remove(application)


        # #Resolve remainder (bribes for already bribed taken from earlier). 
        # applicants_not_already_bribed = [a for a in self.palace_applicants if a not in [app for app in bribes]]
        # bribes = self.collect_bribes(applicants_not_already_bribed)
        # for application in self.palace_applicants.copy():
        #     square = self.select_square_to_place(board, players, application, bribes)
        #     #Log placement
        #     print(self.colour.name+" took "+str(application)+" request and placed piece at "+repr(square))
        #     placement_log.append( (copy_application(application),application[2],square.copy()) )
        #     #Place piece
        #     square.piece = application[0]
        #     self.palace_applicants.remove(application)
        
        # if len(self.palace_applicants) > 0:
        #     raise(Exception("Not all applications were handled."))

        # return conflicts_log, placement_log

    # def collect_bribes(self, applications:list[Application]) -> list[Application]:
    #     """Collects all bribes from a list of applications and returns a list with how much each application paid."""
    #     #Ask for bribe from each player.
    #     for application in applications:
    #         #bribe:int = application[0].owner.decide_bribe(application, previous_bribes)
    #         self.money += application[2]
    #         print(application[0].owner.name+" has paid "+str(application[2]*1000)+" for "+str(application))
    #     return applications    

    # def get_max_value_unoccupied_squares(self, board:Gameboard):
    #     """Returns the most valuable and valid squares available on the board, or an empty list if there's no unoccupied square.
    #     \nA Square is invalid if it's impossible for self to send a Piece to it. (Ex: |Clerk||Doctor||None||Priest| 
    #     A player that cannot send a Scientist can never obtain the None Square in this palace, so it's an invalid Square.)"""
    #     most_valuable_squares:list[Square] = []
    #     current_max_value = 0
    #     #Look for most valuable Squares.
    #     for i in range(len(board)):
    #         if Player_Colour(i) == self.colour:
    #             continue
    #         for j in range(len(board[i])):
    #             square = board[i][j]
    #             #Valid if player has a Piece Type to send not already on the board.
    #             valid = len([p for p in self.pieces if p.type not in self.get_row_types(board[i]) ]) > 0
    #             #Square is occupied or invalid.
    #             if square.piece or not valid:
    #                 continue
    #             #Create new tier of max value or append to current tier.
    #             if square.value > current_max_value:
    #                 current_max_value = square.value
    #                 most_valuable_squares = [square]
    #             elif square.value == current_max_value:
    #                 most_valuable_squares.append(square)
    #     return most_valuable_squares  

    def get_valid_applications(self, board:Gameboard) -> list[tuple[Application, Application]]:
        """Returns all the logically valid squares a player can send a piece to, 
        and the pieces that can be sent for each square."""
        valid_applications:ApplicationLog = []
        for i in range(len(board)):
            if Player_Colour(i) == self.colour:
                continue
            for j in range(len(board[i])):
                square = board[i][j]
                valid_pieces = self.get_valid_pieces_for_square(board,i,j)

                #For each piece, create entry of it as a possible move.
                for piece in valid_pieces:
                    application = (piece, square, self.decide_bribe(piece,square))
                    valid_applications.append( application )

        #Get every possible combination of two pieces to be sent. [(Application1,Application2), ..., ]
        #Note: (Application1,Application2) == (Application2,Application1), and therefore only one of these is counted.
        combs:set[tuple[Application, Application]] = set()
        for i in range(len(valid_applications)):
            j = i+1
            while j < len(valid_applications):
                #The target palace is different or the pieces being sent are different. The target square must be different.
                if ((valid_applications[i][1].owner != valid_applications[j][1].owner) or (valid_applications[i][0] != valid_applications[j][0])) and valid_applications[i][1] != valid_applications[j][1]:
                    #If the pieces are the same, skip if the player can't send two of those.
                    if valid_applications[i][0] == valid_applications[j][0] and list.count(self.pieces,valid_applications[i][0]) < 2:
                        j += 1
                        continue
                    combs.add( (valid_applications[i], valid_applications[j]) )
                j += 1
        return list(combs)

    def get_random_valid_application(self, board:Gameboard) -> ApplicationLog:
        """Randomly returns one valid ApplicationLog for current state."""
        #TODO: Investigate performance of maintaining a static list of possible application target and picking one randomly.
        applications:list[Application] = []
        valid_board_indexes = [i for i in list(range(0,len(board))) if i != self.colour.value]
        my_pieces = self.pieces.copy()
        if not my_pieces:
            return []

        repeat_i = -1
        repeat_j = -1
        while True:
            i = random.choice(valid_board_indexes)
            j = randint(0, len(board[i])-1)
            if i == repeat_i and j == repeat_j:
                continue
            square = board[i][j]

            if square.piece:    #Occupied: Send of the same type, else restart random search.
                my_valid_pieces = [piece for piece in my_pieces if (piece.type == square.piece.type and piece.owner != square.piece.owner)]
            else:   #Empty: Find occupied types, filter self pieces and choose one. Restart if filtered list is empty.
                my_valid_pieces = [piece for piece in my_pieces if piece.type not in self.get_row_types(board[i])]

            if not my_valid_pieces:
                continue
            chosen_piece = random.choice(my_valid_pieces)
            my_pieces.remove(chosen_piece)
            applications.append( (chosen_piece, square, self.decide_bribe(chosen_piece,square)) )
            if len(applications) > 1:
                break
            repeat_i = i
            repeat_j = j
        return applications

    def get_valid_resolutions(self, board:Gameboard) -> list[ConflictLog]:
        """Returns all valid conflict resolutions for this player's turn."""

        conflicts:list[list[Application]] = []
        #Check conflicts. 
        for piece_type_int in range(100,104):
            applications_of_type:list[Application] = self.__find_type_applications__(Piece_Type(piece_type_int), self.palace_applicants)            

            #If internal conflict exists, adds them to the list of contenders.
            for square in board[self.colour.value]:
                if square.piece and Piece_Type(piece_type_int) == square.piece.type:
                    applications_of_type.append( (square.piece,square,0) )
                    break

            #First save each group of conflicts. Once all are stored, start making the combinations.
            if len(applications_of_type) > 1:
                conflicts.append(applications_of_type)

        #For each application list select one and combine all instances.
        conflict_combinations:list[ConflictLog] = []
        depth_combinations(conflicts,[],conflict_combinations)
        
        return conflict_combinations

    def get_random_valid_resolution(self,board:Gameboard) -> ConflictLog:
        """Randomly returns one valid ConflictLog for current state."""
        resolution:list[tuple[list[Application],Application]] = []
        applicants = self.palace_applicants.copy()
        if not applicants:
            return []
        
        for piece_type_int in range(100,104):
            applications_of_type:list[Application] = self.__find_type_applications__(Piece_Type(piece_type_int), applicants)            
            #TODO: Sort list to optimise finding conflicts.

            #If internal conflict exists, adds them to the list of contenders.
            for square in board[self.colour.value]:
                if square.piece and Piece_Type(piece_type_int) == square.piece.type:
                    applications_of_type.append( (square.piece,square,0) )
                    break
            #If conflict exists, add it.
            if len(applications_of_type) > 1:
                chosen_application = random.choice(applications_of_type)
                resolution.append( (applications_of_type, chosen_application) )
                applicants = [app for app in applicants if app not in applications_of_type]

        #Applicants contains the applications with no conflicts. Applicants is local and has no further use.
        return resolution
        

    def get_valid_placements(self, board:Gameboard, external_conflict_resolution:ConflictLog) -> list[PlacementLog]:
        """Given a ConflictLog, returns all valid PlacementLogs for that conflict resolution."""

        applicants:list[Application] = self.palace_applicants.copy()   #List of valid palace applicants for this external conflict resolution.
        for conflict, chosen_application in external_conflict_resolution:
            applicants = [app for app in applicants if app not in conflict]
            applicants.append(chosen_application)    

        #Generate the valid internal plays.
        internal_conflicts:list[list[Application]] = []
        #Check internal conflicts.
        for board_square in board[self.colour.value]:
            if board_square.piece:
                applications_of_type = self.__find_type_applications__(board_square.piece.type, applicants)   
                #There are applications of the same type as in square.  
                if len(applications_of_type) > 0:
                    # if len(applications_of_type) > 1:
                    #     raise Exception(applications_of_type)
                    applications_of_type.append( (board_square.piece,board_square,0) )  #Each list has two applications, the square app and the new one.
                    internal_conflicts.append(applications_of_type)
        
        valid_internal_combinations:list[tuple[Application,...]] = list(product(*internal_conflicts))
        #valid_internal_resolutions:list[ConflictLog] = self.generate_conflict_log(internal_conflicts, valid_internal_combinations)

        #PLACEMENTS
        valid_placements:list[PlacementLog] = []
        empty_squares = [square for square in board[self.colour.value] if not square.piece]
        
        #Internal applications are forcibly placed.
        forced_placement:PlacementLog = []
        for app in applicants:
            occupied_squares = [square for square in board[self.colour.value] if square.piece]
            # print(occupied_squares)
            for square in occupied_squares:
                assert square.piece
                if app[0].type == square.piece.type:
                    #square.piece = app[0]
                    forced_placement.append( (app, square) )
                    break
        for app1, square in forced_placement:
            # print(applicants)
            # print(app1)
            applicants.remove(app1)
        
        #Each permutation has ordered squares in different orders. Ordered applicants receive a square in this order.
        for permutation in permutations(empty_squares, len(applicants)):
            placement:PlacementLog = []
            square_list = list(permutation)
            for app in applicants:
                placement.append( (app, square_list.pop()) )  

            valid_placements.append(placement+forced_placement)          
        
        return valid_placements
    
    def get_random_valid_placement(self, board:Gameboard, external_conflict_resolution:ConflictLog) -> PlacementLog:
        """Randomly returns one valid PlacementLog for current state."""
        placements:PlacementLog = []

        #Remove applications that will not be placed.
        applicants:list[Application] = self.palace_applicants.copy()   
        for conflict, chosen_application in external_conflict_resolution:
            applicants = [app for app in applicants if app not in conflict]
            #Place internal conflicts immediately.(Assumes internal conflict application has correct square in app.)
            if chosen_application[1].piece:# and chosen_application[0].type == chosen_application[1].piece.type: 
                placements.append( (chosen_application, chosen_application[1]) )
            else:
                applicants.append(chosen_application) 

        valid_squares = [square for square in board[self.colour.value] if not square.piece]
        if len(valid_squares) < len(applicants):
            print("Start of loop:")
            print(valid_squares)
            print(applicants)
            print("---")
        for app in applicants:
            chosen_square = random.choice(valid_squares)
            valid_squares.remove(chosen_square)
            placements.append( (app, chosen_square) )
        
        return placements          

    def generate_conflict_log(self, conflict:list[list[Application]], valid_combinations:list[tuple[Application,...]]) -> list[ConflictLog]:
        """Given the list of conflicts and resulting combinations, generates a list of ConflictLog. 
        Each ConflictLog is a resolution for the turn."""
        valid_external_resolutions:list[ConflictLog] = []

        #Note: len(combination) = len(external_conflicts)
        for combination in valid_combinations:
            resolution:ConflictLog = []
            for i in range(len(combination)):
                resolution.append( (conflict[i],combination[i]) )
            valid_external_resolutions.append(resolution)

        # print(valid_external_resolutions)
        # for elem in valid_external_resolutions:
        #     print(elem)

        return valid_external_resolutions

    def get_valid_pieces_for_square(self, board:Gameboard, i:int, j:int) -> list[Piece]:
        """Returns all pieces that can be sent to the given square."""
        valid_pieces:list[Piece] = []
        square = board[i][j]
        if square.piece:    #Occupied: Send of the same type.
            valid_pieces = [piece for piece in self.pieces if (piece.type == square.piece.type and piece.owner != square.piece.owner)]
        else:   #Empty: Find occupied types, filter self pieces.
            valid_pieces = [piece for piece in self.pieces if piece.type not in self.get_row_types(board[i])]
        
        #remove duplicates 
        return list(set(valid_pieces)) 
                
        
    def get_max_bribe_application(self, bribes:list[Application]):
        """Gets the application with the highest corresponding bribe."""
        max_applications:list[Application] = []
        max_bribe = 0
        #print(bribes)
        for application in bribes:
            if application[2] > max_bribe:
                max_bribe = application[2]
                max_applications = [application]
            elif application[2] == max_bribe:
                max_applications.append(application)
        return choice(max_applications)

    def __find_type_applications__(self, type:Piece_Type, applicants:list[Application]):
        """Returns all applications of type in application list."""
        applications_of_type:list[Application] = []
        for application in applicants:
            if type == application[0].type:
                applications_of_type.append(application)
        return applications_of_type

    def get_row_pieces(self, row:list[Square]):
        """Given a row of squares, returns the pieces within."""
        return [s.piece for s in row if s.piece != None]

    def get_row_types(self, row:list[Square]):
        """Given a row of Squares, returns the types for all pieces within."""
        return [p.type for p in self.get_row_pieces(row)]

    # def applicants_string(self) -> str:
    #     """Returns a string representing the applicants."""
    #     string = ""
    #     for piece,square,bribe in self.palace_applicants:
    #         string += str(piece)+"; "
    #     return string

    # def copy(self):
    #     return Player(self.colour,self) #Copy of my self.

    def __eq__(self, other):
        "Players are equal if they have the same colour."
        if isinstance(other, Player):
            return self.colour == other.colour

    def __lt__(self, other):
        """Players are ordered not just on the colour, but they money and pieces."""
        if isinstance(other, Player):    
            self_sum = 0
            other_sum = 0
            for piece in self.pieces:
                self_sum += hash(piece)   
            for opiece in other.pieces:
                other_sum += hash(opiece) 

            for p,s,b in self.palace_applicants:
                self_sum += p.type.value + s.value + b
            for op,os,ob in other.palace_applicants:
                self_sum += op.type.value + os.value + ob

            return self.colour.value+self.money+self_sum < other.colour.value+self.money+other_sum
    
    def __hash__(self) -> int:
        """If two players have the same colour, they have the same hash."""
        return self.colour.value
    def __str__(self):
        def piece_list(piece_list:list[Piece]):
            representation = "["
            for p in self.pieces:
                representation += str(p)+", "
            representation = representation[:-2]
            representation += "]"
            return representation
        return str(self.colour.name)+" Pieces: "+piece_list(self.pieces)+" Money: "+str(self.money*1000)
    def __repr__(self):
        return self.colour.clean_name()+" Pieces: "+repr(self.pieces)+" Money: "+str(self.money*1000)

            ##########################
            ### AUXILARY FUNCTIONS ###
            ##########################  


Application = tuple[Piece,Square,int]
"""The Piece being sent, the Square sent to, and the bribe."""
Gameboard = list[list[Square]]
"""Representation of the gameboard where first index corresponds to player numbers and second to square numbers."""
EarningsLog = list[Square]
"""Squares to collect earnings for this turn."""
ConflictLog = list[tuple[list[Application], Application]]
"""Tuples with conflicts and corresponding bribes, as well as the chosen application."""
PlacementLog = list[tuple[Application, Square]]
"""Tuples with the chosen application, and its placement."""
ApplicationLog = list[Application]
"""Tuples with the applications to be sent."""

def print_application(app:Application):
    print(app[0])
def print_application_list(apps:list[Application]):
    for app in apps:
        print_application(app)
    print("\n")

def recursive_hash_object(element) -> int:
    """Given an object, converts the object into a hash, taking into acount lists and tuples within."""
    counter = 0
    sum = 1
    if isinstance(element, tuple):   #Order matters
        for el in element:
            counter += 1
            sum *= recursive_hash_object(el)*3**counter 
            #The new element's value in a tuple should change tuple id depending on previous values.
    elif isinstance(element, list):    #Order does not matter
        for el in element:
            sum += recursive_hash_object(el)
    else:
        sum += hash(element)
    # print(str(element),"Value:",str(sum),"No of elements in tuple:",str(counter))
    return sum

#Create recursive function that
#[a,b][c,d,e][f,g] -> to_select
#a -> a in selected
#1) combinations.add(function(selected,to_select))
#a,c -> c in selected
#2) combinations.add(function(selected,to_select))
#a,c,f -> f in selected
#3) combinations.add(function(selected,to_select))
#a,c,g next loop iteration: -> g in selected
#3) combinations.add(function(selected,to_select))
#a,d
#a,d,f
#a,d,g
#a,e
#a,e,f
#a,e,g
#B
def depth_combinations(to_select:list[list[Application]], current:ConflictLog, combinations:list[ConflictLog]):
    """Given a list of conflicts (to_select), generates all possible combinations of picking one element from each conflict.\n
    Given to_select, take the first conflict and goes through each element. Each element is a branch, and in each branch, 
    recursively does the same to the next conflict."""

    if not to_select:
        #If branch is empty, append combination.
        combinations.append(current)
        return
    for elem in copy.copy(to_select[0]):
        depth_combinations(to_select[1:],current+[(to_select[0],elem)],combinations)

# def app_get_piece(app:Application) -> Piece:
#     return app[0]

# def conflict_get_piece_val(conflict_log:tuple[list[Application], Application]) -> int:
#     first_piece:Piece = conflict_log[0][0][0]
#     selected_piece:Piece = conflict_log[1][0]
#     return first_piece.type.value+first_piece.owner.value+selected_piece.type.value+selected_piece.owner.value

# def conflict_log_get_val(conflict_log:ConflictLog) -> int:
#     count = 0
#     for conflict in conflict_log:
#         count += conflict_get_piece_val(conflict)
#     return count

# def sort_ConflictLog(conflict_log:ConflictLog) -> ConflictLog:
#         new_conflict_log:ConflictLog = []
#         sorted_log = sorted(conflict_log,key=conflict_get_piece_val)
#         for conflict, selected in sorted_log:
#             new_conflict:list[Application] = sorted(conflict,key=app_get_piece)
#             new_conflict_log.append( (new_conflict, selected) )
#         return new_conflict_log

# def hash_application(app:Application) -> tuple[int,int,int]:
#     return (app[0].__hash__(), app[1].__hash__(), app[2])

# def hash_ConflictLog(conflict_log:ConflictLog) -> list[tuple[list[tuple[int, int, int]], tuple[int, int, int]]]:
#         new_conflict_log:list[tuple[list[tuple[int, int, int]], tuple[int, int, int]]] = []
#         for conflict, selected in conflict_log:
#             new_conflict:list[tuple[int,int,int]] = []
#             for app in conflict:
#                 new_conflict.append( hash_application(app) )
#             new_conflict_log.append( (new_conflict, hash_application(selected)) )
#         return new_conflict_log
# def copy_application(application:Application) -> Application:
#     return (application[0].copy(),application[1].copy(),application[2])
# def copy_gameboard(board:Gameboard) -> Gameboard:
#     copy:list[list[Square]] = []
#     for palace in board:
#         palace_copy:list[Square] = []
#         for square in palace:
#             palace_copy.append(square.copy())
#         copy.append(palace_copy)
#     return copy