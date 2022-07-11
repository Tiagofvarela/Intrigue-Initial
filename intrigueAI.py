from decimal import ROUND_UP
from email.mime import application
from math import ceil
from random import Random, choice, random
from typing import Any, TextIO
from xmlrpc.client import MAXINT
from board import Board, GameMove
from game import Game
from intrigue_datatypes import MINIMUM_BRIBE, PLAYER_COUNT, TOTAL_ROUNDS, Player_Colour
from piece import Piece
from player import Application, ApplicationLog, ConflictLog, EarningsLog, PlacementLog, recursive_hash_object
from square import Square


class IntrigueAI():
    """Main class for intrigue AI agents. \n
    Receive an intrigue Board instance, and implement the get_play() and update(game_state) methods."""   

#PRIORITIES:
    #Square - How much this individual deal is good or bad, regardless of the bigger picture.
    PRIORITY_SQUARE:float = 0
    """From [0, infinity]. How much the player cares about the value of the square. 0 does not take it into consideration."""
    #Opinion - How much profit they've made or lost me.
    PRIORITY_OPINION:float = 0
    """How much the AI values sending applications to players that have been good to them. 0 does not take it into consideration."""
    #Ownership - Difference between all my assets and all their assets.
    PRIORITY_OWNERSHIP:float = 0
    """How much the player values the difference between their assets and the opponents assets."""
    

    #BIAS
    BIAS_PLAYER:list[Player_Colour] = []
    """List of players this AI is biased towards."""
    BIAS_PRIORITY_PLAYER:float = 0
    """How much priority is placed on players this AI is biased towards."""
    
    def __init__(self, board:Board):
        self.board:Board = board
        self.states:list[Game] = []
        self.filename = ""
        self.gain_loss_model = {Player_Colour.RED:0,Player_Colour.GREEN:0,Player_Colour.BLUE:0,Player_Colour.YELLOW:0}

        self.previous_application_log:ApplicationLog = []

    def update(self, state:Game):
        """Takes a game state, and appends it to the history. \nUpdates log accordingly."""
        self.states.append(state)
        # file = open(self.filename,"a")
        # file.write(repr(self.states[-1])+"\n")
        # file.close()

    def update_gain_loss_model(self, state:Game):
        """Compare memory of last action with what others did to establish how much money I've gained or lost.
        Analyses earnings, and how much I'm giving to whom from each square."""
        player = state.players[state.get_player_turn()]
        #Count gain squares.
        for square in player.collect_earnings(state.boards):
            self.gain_loss_model[square.owner] += square.value
        #Count loss squares.
        for square in state.boards[state.get_player_turn()]:
            if square.piece:
                self.gain_loss_model[square.piece.owner] -= square.value

        #For each app sent, assign target player profit. Absolute values only.
        for piece, square, bribe in self.previous_application_log:
            target_player = square.owner
            value = 0
            for target_square in state.boards[target_player.value]:
                if target_square.piece and target_square.piece == piece:
                    value = target_square.value
                    break
            self.gain_loss_model[target_player] += value - square.value 
        #For each application received, add bribe to profit. (Value of square is subtracted elsewhere.)
        for piece, square, bribe in player.palace_applicants:
            sender = piece.owner
            self.gain_loss_model[sender] += bribe

    def get_play(self) -> GameMove:
        """Returns a play for the current state. \nUpdates log accordingly."""
        file = open(self.filename,"a")
        file.write(repr(self.states[-1])+"\n")
        log_info = "Round:"+str(self.states[-1].turn_counter+1)+" "+Player_Colour(self.states[-1].get_player_turn()).clean_name()+" Turn\n"
        file.write(log_info)

        state = self.get_current_state()
        player = state.players[state.get_player_turn()]
        self.update_gain_loss_model(state)
        file.write("\nGain Loss Model: \n")
        for colour, profit in self.gain_loss_model.items():
            if colour != player.colour:
                file.write(colour.clean_name()+" has profited me "+str(profit)+" thousand.\n")

        earnings_log:EarningsLog = player.collect_earnings(state.boards)

        file.write("\nConflicts:\n")
        conflict_log:ConflictLog = self.rank_conflicts(file, player.get_conflicts(state.boards))
        # for conflict in player.get_conflicts(state.boards):
        #     highest_bribe_app = player.get_max_bribe_application(conflict)
        #     file.write("Selected "+repr(highest_bribe_app)+ "because they pay more.\n")
        #     conflict_log.append( (conflict,highest_bribe_app) )

        file.write("\nPlacements:\n")
        internal_placements, applications_to_place = player.get_applications_to_place(conflict_log)    
        placement_log:PlacementLog = []
        if applications_to_place:
            placement_log += self.rank_placements(file, applications_to_place)
        file.write("Remaining placements are automatic: \n"+repr(internal_placements)+"\n\n")
        placement_log += internal_placements

        file.write("Applications:\n")
        application_log:ApplicationLog = []
        if player.pieces:
            valid_applications = player.get_valid_applications_list(state.boards, self.decide_bribe)
            application_log.append(self.rank_applications(file, valid_applications))
            #Remove piece.
            available_pieces = player.pieces.copy()
            available_pieces.remove(application_log[0][0])
            valid_applications = [a for a in valid_applications if a[0] in available_pieces]
            application_log.append(self.rank_applications(file, valid_applications))

        chosen_play = (earnings_log, conflict_log, placement_log, application_log)
        file.write("Play chosen: \n"+repr(chosen_play)+"\n")
        print(log_info)
        file.close()
        self.previous_application_log = application_log
        return chosen_play
    
    def get_current_state(self):
        """Gets the last state in the state history."""
        return self.states[-1]

    #Bribe decision.
    BRIBE_SQUARE_MULTIPLIER:float = 0
    """From [0, infinity], represents the percentage of the square's original value the AI is willing to pay.
    \nIf this value is 1 or greater, then that is the lower bound for bribe value unless there's another bound rule."""
    BRIBE_MIN_SQUARE_MULTIPLIER:float = 0
    """The percentage of the original square that's the minimum amount they're willing to pay. 0 means no lower bound."""
    BRIBE_RANDOMNESS_FACTOR:float = 0.2
    """From [0, 1], how much the amount can deviate from the decided value, positively and negatively. (From 0% to 100%)"""
    BRIBE_MIN_COMPETE:int = 0
    """Minimum amount above previous highest offer that this bribe should be. Negative values ignore other offers."""
    BRIBE_OPINION_MULTIPLIER: float = 0
    """How much the player is liked or disliked increases or reduces the base payment by this percentage."""
    # BRIBE_PLAYER_PENALTY:float = 0
    # """The penalty imposed on how much the player is paid given how much money the player already has."""
    # BRIBE_PLAYER_OWNERSHIP_PENALTY:float = 0
    # """The penalty imposed on how much the player is paid given the money they'll make next round."""

    def opinion_to_increment_converter(self, opinion:int) -> int:
        """Converts profit into a smaller increment for smaller calculations. (Arbitrarily, 3 times smaller.)"""
        #TODO: What factor best to use here for pricings?
        counting_factor = 3
        counter = 0
        #Each 5 thousand profit is one counter increment.
        while opinion > counting_factor:
            counter += 1
            opinion -= counting_factor
        #Each 5 thousand loss is one counted decrement.
        while opinion < -counting_factor:
            counter -= 1
            opinion += counting_factor
        return counter

    def decide_bribe(self, piece:Piece, square:Square, max_spendable:int = None) -> int:
        """Function that given the state of the game and the application, decides on a bribe for it.
        \nShould always return the same value for the exact same conditions."""

        #Always randomly produce the same result for equivalent states.
        rand = Random()
        rand.seed( recursive_hash_object(self.states[-1]) )
        #Set base bribe
        new_bribe = square.value * self.BRIBE_SQUARE_MULTIPLIER

        #Opinion increments of base bribe.
        opinion_increments = self.opinion_to_increment_converter(self.gain_loss_model[square.owner])
        new_bribe += (new_bribe * self.BRIBE_OPINION_MULTIPLIER) * opinion_increments

        #Random variation
        random_factor = new_bribe*self.BRIBE_RANDOMNESS_FACTOR
        new_bribe = rand.uniform(new_bribe - random_factor, new_bribe + random_factor)

        #Lower bound should be MIN_COMPETE_BRIBE higher than the current highest bribe.
        if self.BRIBE_MIN_COMPETE >= 0:
            other_player = self.states[-1].players[square.owner.value]
            competitors = [app for app in other_player.palace_applicants if app[0].type == piece.type]
            if competitors:
                max_competitor = max(competitors, key= lambda a : a[2])
                new_bribe = max(new_bribe, max_competitor[2] + self.BRIBE_MIN_COMPETE)

        #Lower bound is MIN_SQUARE_MULTIPLAYER percent of original value.
        new_bribe = max(new_bribe, square.value * self.BRIBE_MIN_SQUARE_MULTIPLIER)

        #Always sends at least MINIMUM_BRIBE, but never all money unless all money is MINIMUM_BRIBE.
        return max( min(round(new_bribe), self.states[-1].players[piece.owner.value].money-MINIMUM_BRIBE), MINIMUM_BRIBE )

#### CONFLICT RESOLUTION ####

    #Conflict decision.

    def eval_conflict_application(self, application:Application) -> float:
        """Returns a value corresponding to the priority given to accepting the given application in the conflict."""
        piece, square, bribe = application
        priority:float = 1

        #Square - How fair this individual trade is.
        if self.PRIORITY_SQUARE > 0:
            priority += bribe - square.value * self.PRIORITY_SQUARE

        #Opinion - How much my opinion on the other player influences the decision.
        priority += self.gain_loss_model[piece.owner] * self.PRIORITY_OPINION

        #Ownership - How much this deal is valued in the overall picture.
        if self.PRIORITY_OWNERSHIP > 0:
            piece_ownership, square_ownership = self.calculate_ownership(piece.owner, square.owner)
            priority += (-piece_ownership + square_ownership) * self.PRIORITY_OWNERSHIP

        return priority

    def rank_conflicts(self, file:TextIO, conflicts:list[list[Application]]) -> ConflictLog:
        """For each conflict, rank all application choices and choose one oft he highest priority value."""
        conflict_log:ConflictLog = []

        for conflict in conflicts:
            conflict_eval = [(c, self.eval_conflict_application(c)) for c in conflict]
            conflict_eval = sorted(conflict_eval, key=lambda tupl : tupl[1])

            file_string = ""
            for app, p in conflict_eval:
                file_string += repr(app[0])+" to "+repr(app[1])+" for "+repr(app[2]*1000)+" has priority "+str(p)+"\n"
            file.write( file_string+"\n")

            chosen_app = choice( [tupl for tupl in conflict_eval if tupl[1] == conflict_eval[-1][1]] )[0]
            file.write( "Chose "+repr(chosen_app) +"\n\n")

            conflict_log.append( (conflict, chosen_app) )
        return conflict_log

#### CHOOSING PLACEMENT ####

    #Placement Priority
    PLACEMENT_FAIRNESS = 0
    """How much placing the piece in a square fair for the price is valued."""

    def eval_placement_square(self, application:Application, chosen_square:Square) -> float:
        """For the given application and square, assign a priority to that placement."""
        piece, square, bribe = application
        priority:float = 1

        #Square - How good the individual deal is.
        if self.PRIORITY_SQUARE > 0:
            priority += bribe - chosen_square.value * self.PRIORITY_SQUARE

        #Opinion - How much we want to do the other player a favour.
        priority += self.gain_loss_model[square.owner] * self.PRIORITY_OPINION

        #Ownership - How this deal fares in the big picture.
        if self.PRIORITY_OWNERSHIP > 0:
            piece_ownership, square_ownership = self.calculate_ownership(piece.owner, square.owner)
            priority += (-piece_ownership + square_ownership) * self.PRIORITY_OWNERSHIP

        #Fairness - Penalises unfair placements (or rewards them with negative fairness).
        if self.PLACEMENT_FAIRNESS:
            bribe_tier, square_value_tier = self.calculate_value_tier(square, bribe)
            #Negative penalty according to unfairness tier.
            if square_value_tier > bribe_tier:
                priority += (bribe_tier - square_value_tier)*self.PLACEMENT_FAIRNESS
            #Bonus greater for the exact tier.
            else:
                priority += (3 - (bribe_tier - square_value_tier))*self.PLACEMENT_FAIRNESS

        return priority

    #TODO: Could separate this function to take a single value and return a single tier, but there's less loops this way.
    def calculate_value_tier(self, square, bribe):
        """Given a value, return its tier in terms of Square values.\n
        <  3000 is tier 0\n
        <  6000 is tier 1\n
        < 10000 is tier 2\n
        >=10000 is tier 3 """
        bribe_tier = 0
        square_value_tier = 0
        for index in range(3):
            if Square.INDEX_VALUE_DICT[index] <= bribe < Square.INDEX_VALUE_DICT[index+1]:
                bribe_tier = index
            if Square.INDEX_VALUE_DICT[index] <= square.value < Square.INDEX_VALUE_DICT[index+1]:
                square_value_tier = index
        if Square.INDEX_VALUE_DICT[3] <= bribe:
            bribe_tier = 3
        if Square.INDEX_VALUE_DICT[3] <= square.value:
            square_value_tier = 3
        return bribe_tier,square_value_tier

    def rank_placements(self, file:TextIO, applications_to_place:list[Application]) -> PlacementLog:
        """Ranks the priority of each application being placed in each square, and places them in order from highest to lowest priority.
        \nReturns the pairs of placements with highest priority, each square once."""

        placement_log:PlacementLog = []

        all_priorities:list[tuple[Application, Square, float]] = []
        my_player = self.states[-1].players[applications_to_place[0][1].owner.value]

        for app in applications_to_place:
            empty_squares = [s for s in self.states[-1].boards[my_player.colour.value] if not s.piece]
            for square in empty_squares:
                all_priorities.append( (app, square, self.eval_placement_square(app, square)) )

        file_string = ""
        for app, square, p in all_priorities:
            file_string += "Placing "+repr(app[0])+" in "+repr(square)+" for "+repr(app[2]*1000)+" has priority "+str(p)+"\n"
        file.write( file_string+"\n")
        
        while all_priorities:
            all_priorities = sorted(all_priorities, key= lambda tupl : tupl[2])
            chosen_placement = choice( [tupl for tupl in all_priorities if tupl[2] == all_priorities[-1][2]] )
            placement_log.append( (chosen_placement[0], chosen_placement[1]) )

            file.write("Chose to place "+ repr(chosen_placement[0])+" in "+ repr(chosen_placement[1])+"\n")

            #Remove given application and square from priority list.
            all_priorities = [tupl for tupl in all_priorities if tupl[0] != chosen_placement[0] and tupl[1] != chosen_placement[1]]
        
        return placement_log

#### APLICATIONS TO SEND ####

    #Application priority.
    APPLICATION_AVOID_REPEAT:float = 1
    """Penalty that reduces priority to this percentage of original value when two applications are sent to same player."""
    APPLICATION_COMPETE:float = 0
    """How combative the AI is. At higher values they place priority on taking other players' squares.
    At negative values prefers empty squares which can't be rejected."""
    
    def eval_application(self, application:Application, prev:Application=None) -> float:
        """Receives an application and returns a value corresponding to the priority of sending this application.
        Generic function that's affected by the contants. \n
        Example: AVOID_REPEAT_PENALTY which penalises the same player from being chosen twice."""
        piece, square, bribe = application
        priority:float = 1

        #Square
        if self.PRIORITY_SQUARE > 0:
            priority += square.value * self.PRIORITY_SQUARE - bribe #TODO: Make sure it matches bribe logic, so it doesn't disprioritise own bribes.
        #Square Competition
        if square.piece:
            priority += self.APPLICATION_COMPETE
            #Incentivises taking over squares of players that I dislike more.
            if self.APPLICATION_COMPETE >= 0:
                priority -= self.opinion_to_increment_converter(self.gain_loss_model[square.piece.owner])*self.PRIORITY_OPINION
            #Incentivises taking over squares of players that own more.
                ownership, other_ownership = self.calculate_ownership(piece.owner, square.piece.owner)
                priority += (other_ownership - ownership)*self.PRIORITY_OWNERSHIP
            
            #TODO: Consider increasing priority for empty spaces the turn immediately after.

        #Opinion
        priority += self.gain_loss_model[square.owner] * self.PRIORITY_OPINION

        #Ownership
        if self.PRIORITY_OWNERSHIP > 0:
            piece_ownership, square_ownership = self.calculate_ownership(piece.owner, square.owner)
            priority += (piece_ownership - square_ownership) * self.PRIORITY_OWNERSHIP

        if prev: 
            if prev[1].owner == application[1].owner:
                #Don't send same type to same person in the same run.
                if prev[0].type == application[0].type:
                    priority = -9999
                else:
                    priority *= self.APPLICATION_AVOID_REPEAT
        return priority

    def rank_applications(self, file:TextIO, applications:list[Application]) -> Application:
        """Returns the application with highest ranked value according to parameters."""
        valid_applications:list = applications

        #Get app1 - Randomly select one of the top evals when multiple exist.
        valid_applications = [(app, self.eval_application(app)) for app in valid_applications]
        valid_applications = sorted(valid_applications, key=lambda tupl : tupl[1])

        file_string = ""
        for app, p in valid_applications:
            file_string += "Sending "+repr(app[0])+" to "+repr(app[1])+" for "+repr(app[2]*1000)+" has priority "+str(p)+"\n"
        file.write( file_string+"\n")

        tupl1 = choice( [tupl for tupl in valid_applications if tupl[1] == valid_applications[-1][1]] )

        file.write("Will send "+repr(tupl1[0])+"\n")

        # #Get app2 - Randomly select one of the top evals when multiple exist. Remove already sent piece.
        # valid_applications = [(tupl[0], self.eval_application(tupl[0], prev=tupl1[0])) for tupl in valid_applications if tupl[0][0] != tupl1[0][0]]
        # valid_applications = sorted(valid_applications, key=lambda tupl : tupl[1])
        # tupl2 = choice( [tupl for tupl in valid_applications if tupl[1] == valid_applications[-1][1]] )

        # file.write("Will send "+repr(tupl2[0])+"\n")

        return tupl1[0]

    def calculate_ownership(self, player_c:Player_Colour, other_player_c:Player_Colour):
        """Calculates the ownership for player and other_player, returning them in that order."""
        player = self.states[-1].players[player_c.value]
        earnings = sum([s.value for s in player.collect_earnings(self.states[-1].boards)])
        ownership = earnings * self.get_rounds_remaining_for_player(player.colour.value) + player.money

        other_player = self.states[-1].players[other_player_c.value]
        other_earnings = sum([s.value for s in other_player.collect_earnings(self.states[-1].boards)])
        other_ownership = other_earnings * self.get_rounds_remaining_for_player(other_player.colour.value) + other_player.money

        return ownership,other_ownership

    def get_rounds_remaining_for_player(self, other_player:int):
        """Returns the amount of rounds the player will still play in the game. 
        Does differentiate between players that already played this round."""
        current_player = self.states[-1].get_player_turn()

        already_played_this_turn = 0
        if current_player >= other_player:
            already_played_this_turn = 1

        return ceil( (TOTAL_ROUNDS - self.states[-1].turn_counter) / PLAYER_COUNT ) - already_played_this_turn