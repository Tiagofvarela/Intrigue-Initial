import copy
import time
from tkinter.messagebox import NO
import unittest
from board import Board

from game import Game
from intrigueAI import IntrigueAI
from intrigueAI_greedy import Greedy
from intrigueAI_honest import Honest
from intrigueAI_titForTat import TitForTat
from intrigue_datatypes import MINIMUM_BRIBE, Piece_Type, Player_Colour
from intrigueAI_monteCarlo import MonteCarlo
from piece import Piece
from player import ApplicationLog, ConflictLog, EarningsLog, PlacementLog, Player, recursive_hash_object#, Application, ConflictLog, Player, app_get_piece, conflict_log_get_val, hash_ConflictLog, sort_ConflictLog
from square import Square


def set_piece(player, index, square):
    "Sets the piece at the given index in the given square."
    square.piece = player.pieces[index]
    player.pieces.remove(player.pieces[index])

class TestIntrigueAI(unittest.TestCase):

    def test_rank_application(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        #No valid moves
        for square in red_squares:
            set_piece(green, len(green.pieces)-1, square)
            green.pieces.pop()
        for square in green_squares:
            set_piece(blue, len(blue.pieces)-1, square)
            blue.pieces.pop()
        for square in blue_squares:
            set_piece(yellow, len(yellow.pieces)-1, square)
            yellow.pieces.pop()
        for square in yellow_squares:
            set_piece(red, len(red.pieces)-1, square)
            red.pieces.pop()

        red_squares[0].piece = None
        green_squares[0].piece = None
        blue_squares[0].piece = None
        yellow_squares[0].piece = None

        #Combination of multiple valid moves.

        # |None||GREEN Priest|  |GREEN Doctor|  |GREEN Scientist|   RED 
        # |None||BLUE Priest|   |BLUE Doctor|   |BLUE Scientist|    GREEN 
        # |None||YELLOW Priest| |YELLOW Doctor| |YELLOW Scientist|  BLUE 
        # |None||RED Priest|    |RED Doctor|    |RED Scientist|     YELLOW 
        # print(game.boards)
        
        # a1 = (blue.pieces[0], red_squares[0], 0)
        # a2 = (blue.pieces[0], green_squares[0], 0)
        # a3 = (blue.pieces[0], yellow_squares[0], 0)
        # a4 = (blue.pieces[1], red_squares[2], 0)
        # # a5 = (blue.pieces[1], green_squares[2], 0)  #INVALID
        # a6 = (blue.pieces[1], yellow_squares[2], 0)

        #SETUP 
        game.turn_counter = 2
        blue.pieces = [Piece(Player_Colour.BLUE, Piece_Type.CLERK), Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)]        

        board = Board()
        honest = Honest(board)
        honest.update(game)

        print("\nHonest:")
        priority = None
        #For honest, all applications to send are equally rated, and at least fair value is sent for each.
        for app in blue.get_valid_applications_list(game.boards,honest.decide_bribe):
            new_priority = honest.eval_application(app)
            if priority:
                self.assertAlmostEqual(priority, new_priority, delta=0.00001)
            self.assertGreaterEqual(app[2], app[1].value)
            print( repr(app)+" : "+str(honest.eval_application(app)) )
            priority = new_priority

        greedy = Greedy(board)
        greedy.update(game)
        print("\nGreedy:")
        #For greedy, all applications send minimum amount and aim for highest grossing.
        for app in blue.get_valid_applications_list(game.boards,greedy.decide_bribe):
            priority = greedy.eval_application(app)
            self.assertGreaterEqual(priority, app[1].value)
            self.assertEqual(app[2], MINIMUM_BRIBE)
            print( repr(app)+" : "+str(greedy.eval_application(app)) )

        tit_for_tat = TitForTat(board)
        tit_for_tat.update(game)
        tit_for_tat.gain_loss_model = {Player_Colour.GREEN:0, Player_Colour.RED:-3, Player_Colour.YELLOW:-3,Player_Colour.BLUE:0}
        print("\nTit for Tat:")
        priority = None
        #For tit for tat, green > red >= yellow due to prior profit.
        priorities = []
        for app in blue.get_valid_applications_list(game.boards,tit_for_tat.decide_bribe):
            priority = tit_for_tat.eval_application(app)
            priorities.append( (app[1].owner, priority) )
            print( repr(app)+" : "+str(tit_for_tat.eval_application(app)) )
        for player, p in priorities:
            if player == Player_Colour.GREEN:
                values = [t[1] for t in priorities]
                self.assertTrue( len([v for v in values if v>=p ])==1 )
            if player == Player_Colour.YELLOW:
                values = [t[1] for t in priorities]
                self.assertTrue( len([v for v in values if v==p ])==2 )

class TestPlayer(unittest.TestCase):

    def test_collect_earnings(self):
        game = Game()
        yellow = game.players[3]
        #red = game.players[0]  #Consider testing other players as well.
        testing_squares = [game.boards[0][0],game.boards[0][2],game.boards[1][0],game.boards[2][0]]

        set_piece(yellow, 7, testing_squares[0]) #Yellow at Red 1000
        set_piece(yellow, 5, testing_squares[1]) #Yellow at Red 10,000
        set_piece(yellow, 3, testing_squares[2]) #Yellow at Green 1000
        set_piece(yellow, 1, testing_squares[3]) #Yellow at Blue 1000

        initial_money = yellow.money
        squares = yellow.collect_earnings(game.boards)

        for square in squares:
            yellow.money += square.value

        self.assertEqual(yellow.money, initial_money+13, "Should be 45 after collecting.")

        #Note: The order shouldn't necessarily matter.
        for i in range(4):
            #The text (and therefore data) is correct.
            self.assertEqual(str(squares[i]),str(testing_squares[i]))
            #But the square should be a different object.
            self.assertFalse(squares[i] is testing_squares[i])

    def test_get_row_pieces(self):
        game = Game()
        yellow = game.players[3]
        red = game.players[0] 
        
        testing_squares_yellow = [game.boards[0][0],game.boards[0][2]]  #Red squares
        testing_squares_red = [game.boards[1][0],game.boards[1][1],game.boards[1][2],game.boards[1][3]] #Green squares

        set_piece(yellow, 7, testing_squares_yellow[0]) 
        set_piece(yellow, 5, testing_squares_yellow[1]) 
        yellow_pieces = yellow.get_row_pieces(game.boards[0])
        set_piece(red, 7, testing_squares_red[0])   
        set_piece(red, 5, testing_squares_red[1]) 
        set_piece(red, 3, testing_squares_red[2]) 
        set_piece(red, 1, testing_squares_red[3])  
        red_pieces = red.get_row_pieces(game.boards[1]) 
        
        testing_squares_yellow = [s.piece for s in testing_squares_yellow]
        for piece in yellow_pieces:
            self.assertIn(piece, testing_squares_yellow )
        testing_squares_red = [s.piece for s in testing_squares_red]
        for piece in red_pieces:
            self.assertIn(piece, testing_squares_red)

    def test_get_row_types(self):
        game = Game()
        yellow = game.players[3]
        red = game.players[0]  #Consider testing other players as well.
        
        testing_squares_yellow = [game.boards[3][0],game.boards[3][2]]
        testing_squares_red = [game.boards[0][0],game.boards[0][1],game.boards[0][2],game.boards[0][3]]

        set_piece(yellow, 7, testing_squares_yellow[0]) 
        set_piece(yellow, 5, testing_squares_yellow[1]) 
        yellow_types = yellow.get_row_types(game.boards[yellow.colour.value])
        set_piece(red, 7, testing_squares_red[0])   
        set_piece(red, 5, testing_squares_red[1]) 
        set_piece(red, 3, testing_squares_red[2]) 
        set_piece(red, 1, testing_squares_red[3])  
        red_types = red.get_row_types(game.boards[red.colour.value]) 
        
        testing_squares_yellow = [s.piece.type for s in testing_squares_yellow]
        for ptype in yellow_types:
            self.assertIn(ptype, testing_squares_yellow)
        testing_squares_red = [s.piece.type for s in testing_squares_red]
        for ptype in red_types:
            self.assertIn(ptype, testing_squares_red)

    def test_find_application_type(self):
        colour = Player_Colour(0)
        square = Square(0, colour)
        app_list = []
        for i in range(8):
            app_list.append( (Piece(colour,Piece_Type.CLERK),square,i) )
            app_list.append( (Piece(colour,Piece_Type.PRIEST),square,i) )
            app_list.append( (Piece(colour,Piece_Type.SCIENTIST),square,i) )
            app_list.append( (Piece(colour,Piece_Type.DOCTOR),square,i) )
        
        for j in range(100, 104):
            found = Player.__find_type_applications__(None, Piece_Type(j), app_list)
            self.assertTrue( len(found) == 8 )
            for app in found:
                self.assertEqual(app[0].type, Piece_Type(j))    #Correct type.
            self.assertNotEqual(found[0][2],found[-1][2])       #Two different apps are different.

    def test_get_max_bribe_application(self):
        colour = Player_Colour(0)
        square = Square(0, colour)
        app_list = []
        for i in range(8):
            app_list.append( (Piece(colour,Piece_Type.CLERK),square,i) )
            app_list.append( (Piece(colour,Piece_Type.PRIEST),square,i) )
            app_list.append( (Piece(colour,Piece_Type.SCIENTIST),square,i) )
            app_list.append( (Piece(colour,Piece_Type.DOCTOR),square,i) )

        found = Player.get_max_bribe_application(None, app_list)
        self.assertIn( found, app_list[-4:] )   #One of the last four elements was selected.

        counter = 0
        second_find = Player.get_max_bribe_application(None, app_list)
        self.assertIn( second_find, app_list[-4:] )
        while found == second_find:
            second_find = Player.get_max_bribe_application(None, app_list)
            self.assertIn( second_find, app_list[-4:] )
            
            counter += 1
            self.assertFalse(counter > 1000) #Two distinct max pieces should've reasonably been found in this sampling.

    def test_get_valid_pieces_for_square(self):
        game = Game()
        #Players
        yellow = game.players[3]
        red = game.players[0]  #Consider testing other players as well.
        #Squares
        blue_squares = game.boards[2]
        green_squares = game.boards[1]

        ############################################################
        ###Test finding piece for occupied and unnoccupied square###
        ############################################################
        set_piece(yellow, 7, blue_squares[0]) #CLERK
        set_piece(yellow, 5, blue_squares[2]) #PRIEST
        found = red.get_valid_pieces_for_square(game.boards,2,0)    #Should be 1 Clerk
        self.assertEqual( found, [Piece(Player_Colour.RED,Piece_Type.CLERK)] )
        
        found = red.get_valid_pieces_for_square(game.boards,2,1)    #Should be not Clerk or Priest
        self.assertTrue( len(found) == 2 )
        for p in found:
            self.assertTrue(p.type != Piece_Type.CLERK and p.type != Piece_Type.PRIEST)

        ##############################################################
        ###Test finding piece when limited or no valid piece exists###
        ##############################################################
        set_piece(red, 7, green_squares[0])   #Clerk
        set_piece(yellow, 5, green_squares[0])   #Clerk
        set_piece(red, 5, green_squares[1])   #Priest
        set_piece(red, 3, green_squares[2])   #Doctor
        set_piece(red, 1, green_squares[3])   #Scientist
        
        set_piece(red, 3, blue_squares[0]) #Clerk
        #Yellow has no clerks left, should return empty.
        found = yellow.get_valid_pieces_for_square(game.boards,2,0)    #Should be Empty
        self.assertEqual( found, [] )

        #The only valid piece is clerk, should return empty.
        blue_squares[0].piece = None
        set_piece(red, 2, blue_squares[2]) #Priest
        set_piece(red, 1, blue_squares[3]) #Doctor
        set_piece(red, 0, blue_squares[1]) #Scientist
        found = yellow.get_valid_pieces_for_square(game.boards,2,0)    #Should be Empty
        self.assertEqual( found, [] )

    def test_get_valid_applications(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        #No valid moves
        for square in red_squares:
            set_piece(green, len(green.pieces)-1, square)
            green.pieces.pop()
        for square in green_squares:
            set_piece(blue, len(blue.pieces)-1, square)
            blue.pieces.pop()
        for square in blue_squares:
            set_piece(yellow, len(yellow.pieces)-1, square)
            yellow.pieces.pop()
        for square in yellow_squares:
            set_piece(red, len(red.pieces)-1, square)
            red.pieces.pop()
        
        for player in game.players:
            self.assertEqual(player.get_valid_applications(game.boards), [])

        red_squares[0].piece = None
        green_squares[0].piece = None
        blue_squares[0].piece = None
        yellow_squares[0].piece = None
        for player in game.players:
            self.assertEqual(player.get_valid_applications(game.boards), [])

        #Combination of multiple valid moves.

        # |None||GREEN Priest|  |GREEN Doctor|  |GREEN Scientist|   RED 
        # |None||BLUE Priest|   |BLUE Doctor|   |BLUE Scientist|    GREEN 
        # |None||YELLOW Priest| |YELLOW Doctor| |YELLOW Scientist|  BLUE 
        # |None||RED Priest|    |RED Doctor|    |RED Scientist|     YELLOW 
        # print(game.boards)

        blue.pieces = [Piece(Player_Colour.BLUE, Piece_Type.CLERK), Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)]
        
        a1 = (blue.pieces[0], red_squares[0], 0)
        a2 = (blue.pieces[0], green_squares[0], 0)
        a3 = (blue.pieces[0], yellow_squares[0], 0)
        a4 = (blue.pieces[1], red_squares[2], 0)
        # a5 = (blue.pieces[1], green_squares[2], 0)  #INVALID
        a6 = (blue.pieces[1], yellow_squares[2], 0)

        #Order of combination is irrelevant.
        valid_combinations = [
            (a1,a4),(a1,a6),
            (a2,a4),(a2,a6),
            (a3,a4),(a3,a6)
            ]
        valid_combinations2 = [(e2,e1) for e1, e2 in valid_combinations]

        found_combinations = blue.get_valid_applications(game.boards)
        self.assertTrue(len(found_combinations) == len(valid_combinations))
        for app1, app2 in found_combinations:
            #Bribe value is irrelevant for check.
            app1_0 = (app1[0], app1[1], 0) 
            app2_0 = (app2[0], app2[1], 0) 

            self.assertIn( (app1_0, app2_0), valid_combinations+valid_combinations2)

    def test_get_random_valid_application(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        #No valid moves
        for square in red_squares:
            set_piece(green, len(green.pieces)-1, square)
            green.pieces.pop()
        for square in green_squares:
            set_piece(blue, len(blue.pieces)-1, square)
            blue.pieces.pop()
        for square in blue_squares:
            set_piece(yellow, len(yellow.pieces)-1, square)
            yellow.pieces.pop()
        for square in yellow_squares:
            set_piece(red, len(red.pieces)-1, square)
            red.pieces.pop()

        red_squares[0].piece = None
        green_squares[0].piece = None
        blue_squares[0].piece = None
        yellow_squares[0].piece = None

        #Combination of multiple valid moves.

        # |None||GREEN Priest|  |GREEN Doctor|  |GREEN Scientist|   RED 
        # |None||BLUE Priest|   |BLUE Doctor|   |BLUE Scientist|    GREEN 
        # |None||YELLOW Priest| |YELLOW Doctor| |YELLOW Scientist|  BLUE 
        # |None||RED Priest|    |RED Doctor|    |RED Scientist|     YELLOW 
        # print(game.boards)

        blue.pieces = [Piece(Player_Colour.BLUE, Piece_Type.CLERK), Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)]
        
        a1 = (blue.pieces[0], red_squares[0], 0)
        a2 = (blue.pieces[0], green_squares[0], 0)
        a3 = (blue.pieces[0], yellow_squares[0], 0)
        a4 = (blue.pieces[1], red_squares[2], 0)
        #a5 = (blue.pieces[1], green_squares[2], 0) #INVALID
        a6 = (blue.pieces[1], yellow_squares[2], 0)

        #Order of combination is irrelevant.
        valid_combinations:ApplicationLog = [
            (a1,a4),(a1,a6),
            (a2,a4),(a2,a6),
            (a3,a4),(a3,a6)
            ]
        valid_combinations2 = [(e2,e1) for e1, e2 in valid_combinations]

        # found_combinations = blue.get_valid_applications(game.boards)
        # self.assertTrue(len(found_combinations) == len(valid_combinations))
        # for app1, app2 in found_combinations:
        #     #Bribe value is irrelevant for check.
        #     app1_0 = (app1[0], app1[1], 0) 
        #     app2_0 = (app2[0], app2[1], 0) 

        #     self.assertIn( (app1_0, app2_0), valid_combinations+valid_combinations2)


        hashed_expected_combinations = []
        hashed_found_combinations = set()
        for comb in valid_combinations:
            hashed_expected_combinations.append(recursive_hash_object(comb))
            
        expected_found = set()
        
        i = 0
        while i < 10000:
            found_combination = blue.get_random_valid_application(game.boards)

            app1, app2 = found_combination
            #Bribe value is irrelevant for check. Order applications.
            if app1[1].piece:
                app1_0 = (app2[0], app2[1], 0) 
                app2_0 = (app1[0], app1[1], 0) 
            else:
                app1_0 = (app1[0], app1[1], 0) 
                app2_0 = (app2[0], app2[1], 0) 
            found_combination = (app1_0, app2_0)

            #self.assertIn(found_combination, valid_combinations)
            found_hash = recursive_hash_object(found_combination)
            self.assertIn(found_hash, hashed_expected_combinations)
            hashed_found_combinations.add(found_hash)
            expected_found.add(found_combination)
            if len(hashed_found_combinations) == len(hashed_expected_combinations):
                break
            i += 1
        # print("Found: ")
        # for el in expected_found:
        #     print(el)
        # print("Expected: ")
        # for el in valid_combinations:
        #     print(el)
        self.assertEqual(sorted(hashed_expected_combinations), sorted(list(hashed_found_combinations)))

    def test_get_valid_placements(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        red_squares[0].piece = None
        red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
        red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
        red_squares[3].piece = None  

        #Internal
        green_doctor_app = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
        # External then Internal BUG: For now, these are lost.
        # a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
        # a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
        #External 3
        blue_priest_app = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
        green_priest_app = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
        #Independent
        yellow_scientist_app = (Piece(Player_Colour.YELLOW, Piece_Type.SCIENTIST), red_squares[3], 0)

        #Jumbled
        red.palace_applicants.append( green_priest_app )
        red.palace_applicants.append( green_doctor_app )
        # red.palace_applicants.append( a2 )
        red.palace_applicants.append( blue_priest_app )
        red.palace_applicants.append( yellow_scientist_app )
        # red.palace_applicants.append( a3 )

        conflict_log:list[ConflictLog] = [
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],green_doctor_app),
            ([blue_priest_app,green_priest_app],blue_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],(red_squares[1].piece, red_squares[1], 0)),
            ([blue_priest_app,green_priest_app],blue_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],green_doctor_app),
            ([blue_priest_app,green_priest_app],green_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],(red_squares[1].piece, red_squares[1], 0)),
            ([blue_priest_app,green_priest_app],green_priest_app)]
        ]
        conflict_log_practical = red.get_valid_resolutions(game.boards)
        found_placement_log = red.get_valid_placements(game.boards, conflict_log[0])

        # RED Board:        |None||BLUE Doctor||GREEN Clerk||None| 
        # Applicants:       GREEN Doctor, BLUE Priest, GREEN Priest, YELLOW Scientist
        # Chosen Conflict Resolution: 
        #   red_squares[1] ->   ([GREEN Doctor, internal BLUE Doctor], GREEN Doctor) 
        #                       ([BLUE Priest, GREEN Priest], BLUE Priest)

        expected_valid_placements:list[PlacementLog] = [
            [(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[3]),(yellow_scientist_app,red_squares[0])],
            [(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[0]),(yellow_scientist_app,red_squares[3])]
        ]
        # Valid placements:
        # |YELLOW Scientist||GREEN Doctor||GREEN Clerk||BLUE Priest|
        # |BLUE Priest||GREEN Doctor||GREEN Clerk||YELLOW Scientist|

        
        # recursive_hash_object([(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[0]),(yellow_scientist_app,red_squares[3])]),
        # recursive_hash_object([(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[3]),(yellow_scientist_app,red_squares[0])]),
            

        test_hashes = [
            recursive_hash_object([(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[0]),(yellow_scientist_app,red_squares[3])]),
            recursive_hash_object([(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[3]),(yellow_scientist_app,red_squares[0])]),
            recursive_hash_object([(green_doctor_app,red_squares[1]),(yellow_scientist_app,red_squares[0]),(blue_priest_app,red_squares[3])]),
            recursive_hash_object([(blue_priest_app,red_squares[3]),(green_doctor_app,red_squares[1]),(yellow_scientist_app,red_squares[0])]),
            recursive_hash_object([(blue_priest_app,red_squares[3]),(yellow_scientist_app,red_squares[0]),(green_doctor_app,red_squares[1])]),
            recursive_hash_object([(yellow_scientist_app,red_squares[0]),(blue_priest_app,red_squares[3]),(green_doctor_app,red_squares[1])]),
            recursive_hash_object([(yellow_scientist_app,red_squares[0]),(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[3])])
        ]
        i = 1
        while i < len(test_hashes):
            self.assertNotEqual(test_hashes[0], test_hashes[i], ""+str(0)+" should be different from "+str(i))
            self.assertEqual(test_hashes[1], test_hashes[i])
            i += 1

        self.assertEqual(len(expected_valid_placements) , len(found_placement_log))
        self.assertEqual(recursive_hash_object(expected_valid_placements), recursive_hash_object(found_placement_log))
        # for placement in found_placement_log:
        #     self.assertIn(placement, expected_valid_placements)

    def test_get_random_valid_placement(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        red_squares[0].piece = None
        red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
        red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
        red_squares[3].piece = None  

        #Internal
        green_doctor_app = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
        # External then Internal BUG: For now, these are lost.
        # a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
        # a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
        #External 3
        blue_priest_app = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
        green_priest_app = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
        #Independent
        yellow_scientist_app = (Piece(Player_Colour.YELLOW, Piece_Type.SCIENTIST), red_squares[3], 0)

        #Jumbled
        red.palace_applicants.append( green_priest_app )
        red.palace_applicants.append( green_doctor_app )
        # red.palace_applicants.append( a2 )
        red.palace_applicants.append( blue_priest_app )
        red.palace_applicants.append( yellow_scientist_app )
        # red.palace_applicants.append( a3 )

        conflict_log:list[ConflictLog] = [
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],green_doctor_app),
            ([blue_priest_app,green_priest_app],blue_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],(red_squares[1].piece, red_squares[1], 0)),
            ([blue_priest_app,green_priest_app],blue_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],green_doctor_app),
            ([blue_priest_app,green_priest_app],green_priest_app)],
            [([green_doctor_app,(red_squares[1].piece, red_squares[1], 0)],(red_squares[1].piece, red_squares[1], 0)),
            ([blue_priest_app,green_priest_app],green_priest_app)]
        ]

        # RED Board:        |None||BLUE Doctor||GREEN Clerk||None| 
        # Applicants:       GREEN Doctor, BLUE Priest, GREEN Priest, YELLOW Scientist
        # Chosen Conflict Resolution: 
        #   red_squares[1] ->   ([GREEN Doctor, internal BLUE Doctor], GREEN Doctor) 
        #                       ([BLUE Priest, GREEN Priest], BLUE Priest)

        expected_valid_placements:list[PlacementLog] = [
            [(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[3]),(yellow_scientist_app,red_squares[0])],
            [(green_doctor_app,red_squares[1]),(blue_priest_app,red_squares[0]),(yellow_scientist_app,red_squares[3])]
        ]
        # Valid placements:
        # |YELLOW Scientist||GREEN Doctor||GREEN Clerk||BLUE Priest|
        # |BLUE Priest||GREEN Doctor||GREEN Clerk||YELLOW Scientist|        
        hashed_expected_placements = []
        hashed_found_placements = set()
        for placement in expected_valid_placements:
            hashed_expected_placements.append(recursive_hash_object(placement))
        
        i = 0
        while i < 10000:
            found_placement_log = red.get_random_valid_placement(game.boards, conflict_log[0])

            #self.assertIn(found_placement_log, expected_valid_placements)
            found_hash = recursive_hash_object(found_placement_log)
            self.assertIn(found_hash, hashed_expected_placements)
            hashed_found_placements.add(found_hash)
            if len(hashed_found_placements) == len(hashed_expected_placements):
                break
            i += 1
        self.assertEqual(sorted(hashed_expected_placements), sorted(list(hashed_found_placements)))

    def test_get_valid_resolutions(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        red_squares[0].piece = None
        red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
        red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
        red_squares[3].piece = None

        #Internal
        green_doctor_app = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
        #External then Internal
        blue_clerk_app = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
        yellow_clerk_app = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
        #External 3
        blue_priest_app = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
        green_priest_app = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
        yellow_priest_app = (Piece(Player_Colour.YELLOW, Piece_Type.PRIEST), red_squares[3], 0)

        #Jumbled
        red.palace_applicants.append( green_priest_app )
        red.palace_applicants.append( green_doctor_app )
        red.palace_applicants.append( blue_clerk_app )
        red.palace_applicants.append( blue_priest_app )
        red.palace_applicants.append( yellow_priest_app )
        red.palace_applicants.append( yellow_clerk_app )

        #Possible Resolutions
        internal_app = (red_squares[1].piece, red_squares[1], 0)    #Blue Doctor
        res1_1 = [green_doctor_app, internal_app ], green_doctor_app
        res1_2 = [green_doctor_app, internal_app ], internal_app
            
        internal_app = (red_squares[2].piece, red_squares[2], 0)    #Green Clerk
        res2_1 = [blue_clerk_app,yellow_clerk_app,internal_app],blue_clerk_app
        res2_2 = [blue_clerk_app,yellow_clerk_app,internal_app],yellow_clerk_app
        res2_3 = [blue_clerk_app,yellow_clerk_app,internal_app],internal_app

        res3_1 = [blue_priest_app,green_priest_app,yellow_priest_app], blue_priest_app
        res3_2 = [blue_priest_app,green_priest_app,yellow_priest_app], green_priest_app
        res3_3 = [blue_priest_app,green_priest_app,yellow_priest_app], yellow_priest_app

        valid_combinations = [
            #RES1_1
            #res2-1
            [res1_1,res2_1,res3_1],
            [res1_1,res2_1,res3_2],
            [res1_1,res2_1,res3_3],
            #res2-2
            [res1_1,res2_2,res3_1],
            [res1_1,res2_2,res3_2],
            [res1_1,res2_2,res3_3],
            #res2-3
            [res1_1,res2_3,res3_1],
            [res1_1,res2_3,res3_2],
            [res1_1,res2_3,res3_3],

            #RES1_2
            #res2-1
            [res1_2,res2_1,res3_1],
            [res1_2,res2_1,res3_2],
            [res1_2,res2_1,res3_3],
            #res2-2
            [res1_2,res2_2,res3_1],
            [res1_2,res2_2,res3_2],
            [res1_2,res2_2,res3_3],
            #res2-3
            [res1_2,res2_3,res3_1],
            [res1_2,res2_3,res3_2],
            [res1_2,res2_3,res3_3],
        ]

        found_combinations = red.get_valid_resolutions(game.boards)
        hash_valid_combinations:list = []
        hash_found_combinations:list = []
        for i in range(len(valid_combinations)):
            hash_valid_combinations.append(recursive_hash_object(valid_combinations[i]))
            hash_found_combinations.append(recursive_hash_object(found_combinations[i]))

        # print("\n")
        # print(hash_middle_combinations)
        # print(sorted(hash_middle_combinations))
        # print("\n")
        # print(hash_found_combinations)
        # print(sorted(hash_found_combinations) )
        # print("\n")

        self.assertEqual( len(hash_found_combinations), len(hash_valid_combinations) )
        for hash_el in hash_found_combinations:
            self.assertIn(hash_el, hash_valid_combinations)     

    def test_get_random_valid_resolutions(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        red_squares[0].piece = None
        red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
        red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
        red_squares[3].piece = None

        #Internal
        green_doctor_app = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
        #External then Internal
        blue_clerk_app = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
        yellow_clerk_app = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
        #External 3
        blue_priest_app = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
        green_priest_app = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
        yellow_priest_app = (Piece(Player_Colour.YELLOW, Piece_Type.PRIEST), red_squares[3], 0)

        #Jumbled
        red.palace_applicants.append( green_priest_app )
        red.palace_applicants.append( green_doctor_app )
        red.palace_applicants.append( blue_clerk_app )
        red.palace_applicants.append( blue_priest_app )
        red.palace_applicants.append( yellow_priest_app )
        red.palace_applicants.append( yellow_clerk_app )

        #Possible Resolutions
        internal_app = (red_squares[1].piece, red_squares[1], 0)    #Blue Doctor
        res1_1 = [green_doctor_app, internal_app ], green_doctor_app
        res1_2 = [green_doctor_app, internal_app ], internal_app
            
        internal_app = (red_squares[2].piece, red_squares[2], 0)    #Green Clerk
        res2_1 = [blue_clerk_app,yellow_clerk_app,internal_app],blue_clerk_app
        res2_2 = [blue_clerk_app,yellow_clerk_app,internal_app],yellow_clerk_app
        res2_3 = [blue_clerk_app,yellow_clerk_app,internal_app],internal_app

        res3_1 = [blue_priest_app,green_priest_app,yellow_priest_app], blue_priest_app
        res3_2 = [blue_priest_app,green_priest_app,yellow_priest_app], green_priest_app
        res3_3 = [blue_priest_app,green_priest_app,yellow_priest_app], yellow_priest_app

        valid_combinations = [
        #RES1_1
        #res2-1
        [res1_1,res2_1,res3_1],
        [res1_1,res2_1,res3_2],
        [res1_1,res2_1,res3_3],
        #res2-2
        [res1_1,res2_2,res3_1],
        [res1_1,res2_2,res3_2],
        [res1_1,res2_2,res3_3],
        #res2-3
        [res1_1,res2_3,res3_1],
        [res1_1,res2_3,res3_2],
        [res1_1,res2_3,res3_3],

        #RES1_2
        #res2-1
        [res1_2,res2_1,res3_1],
        [res1_2,res2_1,res3_2],
        [res1_2,res2_1,res3_3],
        #res2-2
        [res1_2,res2_2,res3_1],
        [res1_2,res2_2,res3_2],
        [res1_2,res2_2,res3_3],
        #res2-3
        [res1_2,res2_3,res3_1],
        [res1_2,res2_3,res3_2],
        [res1_2,res2_3,res3_3],
        ]

        hashed_expected_resolutions = []
        hashed_found_resolutions = set()
        for comb in valid_combinations:
            hashed_expected_resolutions.append(recursive_hash_object(comb))
        
        i = 0
        while i < 10000:
            found_conflict_log = red.get_random_valid_resolution(game.boards)
            found_hash = recursive_hash_object(found_conflict_log)
            self.assertIn(found_hash, hashed_expected_resolutions)
            hashed_found_resolutions.add(found_hash)
            if len(hashed_found_resolutions) == len(hashed_expected_resolutions):
                break
            i += 1
        self.assertEqual(sorted(hashed_expected_resolutions), sorted(list(hashed_found_resolutions)))

    def test_get_ordered_players(self):
        game = Game()
        red,green,blue,yellow = game.players
        red.money = 12
        green.money = 17
        blue.money = 9
        yellow.money = 13
        self.assertEqual([green,yellow,red,blue],game.get_ordered_players())
        yellow.money = 12

        order = game.get_ordered_players()
        self.assertTrue( order[0] == green and order[1].money == order[2].money and order[-1] == blue )

class TestGame(unittest.TestCase):
    def test_play_game(self):
        game = Game()
        red,green,blue,yellow = game.players
        red_squares,green_squares,blue_squares,yellow_squares = game.boards

        red_squares[0].piece = None
        red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
        red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
        red_squares[3].piece = None  

        #Internal
        a1 = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 1)
        # External then Internal BUG: For now, these are lost.
        a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 2)
        a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 3)
        #External 3
        a4 = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 4)
        a5 = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 5)
        #Independent
        a6 = (Piece(Player_Colour.YELLOW, Piece_Type.SCIENTIST), red_squares[3], 6)

        #Jumbled
        red.palace_applicants.append( a5 )
        red.palace_applicants.append( a1 )
        red.palace_applicants.append( a2 )
        red.palace_applicants.append( a4 )
        red.palace_applicants.append( a6 )
        red.palace_applicants.append( a3 )

        set_piece(red,4,yellow_squares[2])
        earnings_log:EarningsLog = [yellow_squares[2]]
        applications_log:ApplicationLog = [(red.pieces[0], green_squares[0], 0), (red.pieces[-1], yellow_squares[0], 0)]
        conflict_log:ConflictLog = [
            ([a1,(red_squares[1].piece, red_squares[1], 0)],a1),
            ([a4,a5],a4),
            ([a2,a3],a2),   #Implementation doesn't actually care about intermediate conflicts. 
            #TODO: Use this fact in implementation. Make external then-internal just a big internal.
            #Example: ([a2,a3,(red_squares[2].piece, red_squares[2], 0)],a2)
            ([a2,(red_squares[2].piece, red_squares[2], 0)],a2)
        ]
        placement_log:PlacementLog = [
            (a1,red_squares[1]),(a4,red_squares[3]),(a6,red_squares[0]),(a2,red_squares[2])
        ]
        play = (earnings_log,conflict_log,placement_log,applications_log)
        new_game = game.get_next_state(play)

        #Earnings Log
        red.money += earnings_log[0].value
        #Conflict Log
        for piece,square,bribe in red.palace_applicants:
            red.money += bribe
            game.players[piece.owner.value].money -= bribe
        red.palace_applicants = []
        #Placement Log
        red_squares[0].piece = a6[0]
        red_squares[1].piece = a1[0]
        red_squares[2].piece = a2[0]
        red_squares[3].piece = a4[0]
        #Application Log
        green.palace_applicants.append( applications_log[0] )
        red.pieces.remove(red.pieces[0])
        yellow.palace_applicants.append( applications_log[1] )
        red.pieces.remove(red.pieces[-1])

        game.turn_counter += 1

        self.assertEqual(game.turn_counter, new_game.turn_counter)
        self.assertEqual(game.players, new_game.players)

        ##DEBUG PRINTS##
        for i in range(len(game.players)):
            new_game_player = new_game.players[i]
            game_player = game.players[i]
            self.assertEqual(new_game_player, game_player)
            self.assertEqual(new_game_player.pieces, game_player.pieces)
            self.assertEqual(new_game_player.palace_applicants, game_player.palace_applicants)
            self.assertEqual(new_game_player.money, game_player.money)
            # print(new_game_player.palace_applicants)
            # print(new_game_player.pieces)
            # print("Should be:")
            # print(game_player.palace_applicants)
            # print(game_player.pieces)
            # print()

        for i in range(len(game.boards)):
            new_game_board = new_game.boards[i]
            game_board = game.boards[i]
            self.assertEqual(new_game_board, game_board)
            for j in range(len(game.boards[i])):
                self.assertEqual(new_game_board[j], game_board[j])
            # print(new_game_board)
            # print("Should be:")
            # print(game_board)
            # print()

        # print()
        # print(new_game)
        # print(game)
        
        # self.assertEqual(game.boards, new_game.boards)
        # self.assertEqual(game,new_game)

        # found_applciations_logs = red.get_valid_applications(game.boards)
        # found_conflict_logs = red.get_valid_resolutions2(game.boards)
        # found_placement_logs = red.get_valid_placements(game.boards, conflict_log)

    # def test_run_simulation(self):
    #     print()
    #     #Set up game board.
    #     board = Board()
    #     #Parameters (not used in simulation)
    #     args = {'time':1,'max_moves':120,'C':1.3}
    #     #Set up montecarlo.
    #     open('search-log.txt', 'w').close()
    #     montecarlo = MonteCarlo(board, **args)
    #     montecarlo.update(board.start())

    #     ### One Simulation ###

    #     print("Plays before: ",list(montecarlo.plays.values()))
    #     print("Wins before: ",list(montecarlo.wins.values()))
    #     tic = time.perf_counter()
    #     #Play a simulation.
    #     montecarlo.run_simulation()
    #     toc = time.perf_counter()
    #     print("Plays after: ",list(montecarlo.plays.values()))
    #     print("Wins after: ",list(montecarlo.wins.values()))

    #     taken_seconds = (toc - tic)
    #     print("It has taken",taken_seconds,"seconds.")

    #     ### Simulate and test Plays ###       
    #     # print("Plays before: ",list(montecarlo.plays.values()))
    #     # print("Wins before: ",list(montecarlo.wins.values()))

    #     # while 2 not in set(montecarlo.plays.values()):
    #     #     montecarlo.run_simulation()
    #     #     # print(set(montecarlo.plays.values()))
        
    #     # print("Plays after: ",list(montecarlo.plays.values()))
    #     # print("Wins after: ",list(montecarlo.wins.values()))

    #     print()

        
        

if __name__ == '__main__':
    unittest.main()
