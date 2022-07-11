from intrigueAI import IntrigueAI

class Honest(IntrigueAI):
    """Honest AI rewards fair bribes, and makes fair offers."""

    #PRIORITIES:
    #Square - How much this individual deal is good or bad, regardless of the bigger picture.
    PRIORITY_SQUARE:float = 1
    #Opinion - How much profit they've made or lost me.
    PRIORITY_OPINION:float = 0
    #Ownership - Difference between all my assets and all their assets.
    PRIORITY_OWNERSHIP:float = 0

    #BRIBE
    BRIBE_SQUARE_MULTIPLIER:float = 1.5
    BRIBE_MIN_SQUARE_MULTIPLIER:float = 1
    BRIBE_RANDOMNESS_FACTOR:float = 0.3
    BRIBE_MIN_COMPETE:int = 1
    BRIBE_OPINION_MULTIPLIER: float = 0

    #CONFLICT

    #PLACEMENT
    PLACEMENT_FAIRNESS = 1

    #APPLICATIONS
    APPLICATION_AVOID_REPEAT:float = 1
    APPLICATION_COMPETE:float = 0

    # def get_play(self) -> GameMove:
    #     """Returns a play for the current state. \nUpdates log accordingly."""
    #     file = open(self.filename,"a")
    #     file.write(repr(self.states[-1])+"\n")
    #     log_info = "Round:"+str(self.states[-1].turn_counter+1)+" "+Player_Colour(self.states[-1].get_player_turn()).clean_name()+" Turn\n"
    #     file.write(log_info)

    #     state = self.get_current_state()
    #     player = state.players[state.get_player_turn()]

    #     earnings_log:EarningsLog = player.collect_earnings(state.boards)

    #     file.write("\nConflicts:\n")
    #     conflict_log:ConflictLog = []
    #     for conflict in player.get_conflicts(state.boards):
    #         highest_bribe_app = player.get_max_bribe_application(conflict)
    #         file.write("Selected "+repr(highest_bribe_app)+ "because they pay more.\n")
    #         conflict_log.append( (conflict,highest_bribe_app) )

    #     file.write("\nPlacements:\n")
    #     internal_placements, applications_to_place = player.get_applications_to_place(conflict_log)    
    #     #It's assumed requested square is a valid one.
    #     empty_squares = [square for square in state.boards[player.colour.value] if not square.piece]
    #     placement_log:PlacementLog = []
    #     self.place_according_to_bribe(state, internal_placements, applications_to_place, empty_squares, placement_log,file)
    #     file.write("Remaining placements are automatic: \n"+repr(internal_placements)+"\n\n")
    #     placement_log += internal_placements

    #     file.write("Applications:\n")
    #     application_log:ApplicationLog = []
    #     if player.pieces:
    #         application_log = self.select_applications(state, player, file)

    #     chosen_play = (earnings_log, conflict_log, placement_log, application_log)
    #     file.write("Play chosen: \n"+repr(chosen_play)+"\n")
    #     print(log_info)
    #     file.close()
    #     return chosen_play

    # def select_applications(self, state:Game, player:Player, file:TextIO):
    #     """Selects two applications given the current state according to Honest Player logic.
    #     Prioritise sending to players who sent to self, prioritise empty squares, pay as much as square is worth."""
    #     application_log:ApplicationLog = []
    #     apps = player.palace_applicants.copy()

    #     piece_list:list[Piece] = player.pieces.copy()
    #     repeat_square = None

    #     max_spending_allowed = player.money - MINIMUM_BRIBE
    #     while len(application_log) < 2:
    #             #Choose player - Chosen in order of highest bribes received or random if none available.
    #         chosen_player_val:int
    #         if not apps:
    #             random_app = player.get_random_valid_application(state.boards)[0]
    #             file.write("Considering random: "+repr(random_app)+"\n")
    #             sending_impossible_piece = random_app[0] not in piece_list
    #             #Check forces two different pieces to be randomly sent.
    #             if (not application_log or (application_log and random_app != application_log[0])) and not sending_impossible_piece and repeat_square != random_app[1]:
    #                 piece, square, bribe = random_app

    #                 bribe = min(square.value+1, max_spending_allowed)#TODO: Send this function to get_random_valid as argument.
    #                 max_spending_allowed = player.money - bribe #Remainder used for application two.
    #                 file.write("Sending bribe with value "+str(bribe)+". "+str(max_spending_allowed)+" left over for another bribe.\n")

    #                 application_log.append( (piece,square,bribe) )
    #                 file.write("No player applications. Random application chosen: "+repr( (piece,square,bribe) )+"\n")
    #                 piece_list.remove(piece)
    #                 repeat_square = square
    #             continue
    #         else:
    #             highest_bribe_app = player.get_max_bribe_application(apps)
    #             chosen_player_val = highest_bribe_app[0].owner.value
    #             file.write("\n"+highest_bribe_app[0].owner.clean_name()+" sent application to me. Sending one to them.\n")
                
    #         chosen_square:Square|None = None
    #         chosen_piece:Piece|None = None
    #             #Choose square - Choses empty square from target, or occupied if no empty are available.
    #         empty_squares = [s for s in state.boards[chosen_player_val] if not s.piece and s != repeat_square]
    #         shuffle(empty_squares)
    #         file.write("Checking empty available squares: "+repr(empty_squares)+"\n")
    #         for s in empty_squares:
    #             chosen_square = s
    #             i, j = chosen_square.get_index()
    #                 #Choose piece - Chooses random valid piece.
    #             valid_pieces = player.get_valid_pieces_for_square(state.boards, i, j, piece_list=piece_list)
    #             file.write("Out of "+repr(piece_list)+" ")
    #             file.write(repr(valid_pieces)+" are valid for "+repr(chosen_square)+"\n")
    #             if not valid_pieces:
    #                 file.write("Chose "+repr(chosen_square)+", but no piece available to send. Rechosing...\n")
    #                 continue
    #             chosen_piece = choice(valid_pieces)
    #             break

    #             #Choose square - Couldn't find empty, checking occupied.
    #         if not chosen_piece:
    #             occupied_squares = [s for s in state.boards[chosen_player_val] 
    #             if s.piece and s.piece.type in [p.type for p in player.pieces] and s != repeat_square]
    #             shuffle(occupied_squares)

    #             file.write("Couldn't find valid empty square, checking occupied available squares: "+repr(occupied_squares)+"\n")
    #             for s in occupied_squares:
    #                 chosen_square = s
    #                 i, j = chosen_square.get_index()
    #                     #Choose piece - Chooses random valid piece.
    #                 valid_pieces = player.get_valid_pieces_for_square(state.boards, i, j, piece_list=piece_list)
    #                 file.write("Out of "+repr(piece_list)+" ")
    #                 file.write(repr(valid_pieces)+" are valid for "+repr(chosen_square)+"\n")
    #                 if not valid_pieces:
    #                     file.write("Chose "+repr(chosen_square)+", but no piece available to send. Rechosing...\n")
    #                     continue
    #                 chosen_piece = choice(valid_pieces)
    #                 break

    #         #Moves to next highest application player, doesn't repeat pieces.
    #         apps.remove(highest_bribe_app)

    #         if not chosen_piece or chosen_square:
    #             file.write("\nCouldn't send to "+highest_bribe_app[0].owner.clean_name()+", checking next option...\n")
    #             continue
    #         assert chosen_piece
    #         assert chosen_square
    #         file.write("Chose "+repr(chosen_piece)+" to "+repr(chosen_square)+"\n")
                
    #         #Choose bribe
    #         chosen_bribe = min(chosen_square.value+1, max_spending_allowed)
    #         max_spending_allowed = player.money - chosen_bribe #Remainder used for application two.
    #         file.write("Sending bribe with value "+str(chosen_bribe)+". "+str(max_spending_allowed)+" left over for another bribe.")
    #         application_log.append( (chosen_piece, chosen_square, chosen_bribe ) )
    #         file.write("Considered application chosen: "+repr(application_log[-1])+"\n")
    #         #Doesn't repeat pieces.
    #         repeat_square = chosen_square
    #         piece_list.remove(chosen_piece)
    #     return application_log

    # def place_according_to_bribe(self, state, internal_placements, applications_to_place:list[Application], empty_squares, placement_log:PlacementLog,file:TextIO):
    #     """Find a square to place the applications according to their bribes."""
        
    #     #Check empty spots in descending order of their value.
    #     empty_squares = sorted(empty_squares,key=lambda s : s.value,reverse=True)
    #     file.write("Checking available placements in the following order: "+repr(empty_squares)+"\n")

    #     #Check applications randomly. TODO: Instead reward in order of highest value bribes.
    #     shuffle(applications_to_place)
    #     file.write("Checking applications in the following order: "+repr(applications_to_place)+"\n")

    #     for app in applications_to_place:
    #         file.write("Application "+repr(app)+": ")
    #         piece, square, bribe = app
    #         placement_len = len(placement_log)
    #         if square in empty_squares:
    #             #Good bribe, place in requested location.
    #             if bribe > square.value:
    #                 placement_log.append( (app, square) )
    #                 empty_squares.remove(square)
    #                 file.write("Pays well for requested square, accepted.")
    #                 continue
    #         else:
    #             file.write("Requested square is unavailable. Checking for others.")
            
    #         #Bad bribe or unavailable, find appropriate value to place.                
    #         for e_square in [s for s in empty_squares if s != square]:
    #             if bribe > e_square.value:
    #                 placement_log.append( (app, e_square) )
    #                 empty_squares.remove(e_square)
    #                 file.write("Requested square couldn't be bought, redirected to "+repr(e_square)+"\n")
    #                 break
    #         #The bribe matches no square value. Place at lowest value.
    #         if placement_len == len(placement_log):
    #             placement_log.append( (app, empty_squares[-1]) )
    #             file.write("Pays a pittance. Placing in lowest value: "+repr(empty_squares[-1])+"\n")
    #             empty_squares.remove(empty_squares[-1])