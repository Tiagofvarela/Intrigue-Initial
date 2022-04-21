import copy
from tkinter.messagebox import NO
import unittest

from intrigue import Game
from intrigue_datatypes import Piece_Type, Player_Colour
from piece import Piece
from player import ApplicationLog, ConflictLog, EarningsLog, PlacementLog, Player#, Application, ConflictLog, Player, app_get_piece, conflict_log_get_val, hash_ConflictLog, sort_ConflictLog
from square import Square


def set_piece(player, index, square):
    "Sets the piece at the given index in the given square."
    square.piece = player.pieces[index]
    player.pieces.remove(player.pieces[index])


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
        a5 = (blue.pieces[1], green_squares[2], 0)
        a6 = (blue.pieces[1], yellow_squares[2], 0)

        #Order of combination is irrelevant.
        valid_combinations = [
            (a1,a4),(a1,a5),(a1,a6),
            (a2,a4),(a2,a5),(a2,a6),
            (a3,a4),(a3,a5),(a3,a6)
            ]
        valid_combinations2 = [(e2,e1) for e1, e2 in valid_combinations]

        found_combinations = blue.get_valid_applications(game.boards)
        self.assertTrue(len(found_combinations) == len(valid_combinations))
        for app1, app2 in found_combinations:
            #Bribe value is irrelevant for check.
            app1_0 = (app1[0], app1[1], 0) 
            app2_0 = (app2[0], app2[1], 0) 

            self.assertIn( (app1_0, app2_0), valid_combinations+valid_combinations2)

    # def test_get_valid_placements(self):
    #     game = Game()
    #     red,green,blue,yellow = game.players
    #     red_squares,green_squares,blue_squares,yellow_squares = game.boards

    #     red_squares[0].piece = None
    #     red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
    #     red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
    #     red_squares[3].piece = None  

    #     #Internal
    #     a1 = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
    #     # External then Internal BUG: For now, these are lost.
    #     # a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
    #     # a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
    #     #External 3
    #     a4 = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
    #     a5 = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
    #     #Independent
    #     a6 = (Piece(Player_Colour.YELLOW, Piece_Type.SCIENTIST), red_squares[3], 0)

    #     #Jumbled
    #     red.palace_applicants.append( a5 )
    #     red.palace_applicants.append( a1 )
    #     # red.palace_applicants.append( a2 )
    #     red.palace_applicants.append( a4 )
    #     red.palace_applicants.append( a6 )
    #     # red.palace_applicants.append( a3 )

    #     conflict_log:list[ConflictLog] = [
    #         [([a1,(red_squares[1].piece, red_squares[1], 0)],a1),
    #         ([a4,a5],a4)],
    #         [([a1,(red_squares[1].piece, red_squares[1], 0)],(red_squares[1].piece, red_squares[1], 0)),
    #         ([a4,a5],a4)]
    #     ]
    #     conflict_log_practical = red.get_valid_resolutions2(game.boards)


    #     found_placement_log = red.get_valid_placements(game.boards, conflict_log[0])
    #     valid_placements:list[PlacementLog] = [
    #         [(a1,red_squares[1]),(a4,red_squares[3]),(a6,red_squares[1])],
    #         [(a1,red_squares[1]),(a4,red_squares[1]),(a6,red_squares[3])]
    #     ]
    #     self.assertTrue(len(found_placement_log) == len(valid_placements))
    #     for placement in found_placement_log:
    #         self.assertIn(placement, valid_placements)

    # def test_get_valid_resolutions(self):
    #     game = Game()
    #     red,green,blue,yellow = game.players
    #     red_squares,green_squares,blue_squares,yellow_squares = game.boards

    #     red_squares[0].piece = None
    #     red_squares[1].piece = Piece(Player_Colour.BLUE, Piece_Type.DOCTOR)
    #     red_squares[2].piece = Piece(Player_Colour.GREEN, Piece_Type.CLERK)
    #     red_squares[3].piece = None

    #     #Internal
    #     a1 = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
    #     #External then Internal
    #     a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
    #     a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
    #     #External 3
    #     a4 = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
    #     a5 = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
    #     a6 = (Piece(Player_Colour.YELLOW, Piece_Type.PRIEST), red_squares[3], 0)

    #     #Jumbled
    #     red.palace_applicants.append( a5 )
    #     red.palace_applicants.append( a1 )
    #     red.palace_applicants.append( a2 )
    #     red.palace_applicants.append( a4 )
    #     red.palace_applicants.append( a6 )
    #     red.palace_applicants.append( a3 )

    #     #Possible Resolutions
    #     internal_app = (red_squares[1].piece, red_squares[1], 0)
    #     res1_1 = [a1, internal_app ], a1
    #     res1_2 = [a1, internal_app ], internal_app

    #     res2_1 = [a2,a3],a2
    #     internal_app = (red_squares[2].piece, red_squares[2], 0)
    #     res2_1_1 = [a2, internal_app], a2
    #     res2_1_2 = [a2, internal_app], internal_app

    #     res2_2 = [a2,a3],a3
    #     res2_2_1 = [a3, internal_app], a3
    #     res2_2_2 = [a3, internal_app], internal_app

    #     res3_1 = [a4,a5,a6], a4
    #     res3_2 = [a4,a5,a6], a5
    #     res3_3 = [a4,a5,a6], a6

    #     valid_combinations = [
    #         #RES1_1
    #         #res2-1
    #         [res1_1,res2_1,res2_1_1,res3_1],
    #         [res1_1,res2_1,res2_1_1,res3_2],
    #         [res1_1,res2_1,res2_1_1,res3_3],
    #         #res2-1-2
    #         [res1_1,res2_1,res2_1_2,res3_1],
    #         [res1_1,res2_1,res2_1_2,res3_2],
    #         [res1_1,res2_1,res2_1_2,res3_3],
    #         #res2-2
    #         [res1_1,res2_2,res2_2_1,res3_1],
    #         [res1_1,res2_2,res2_2_1,res3_2],
    #         [res1_1,res2_2,res2_2_1,res3_3],
    #         #res2-2-2
    #         [res1_1,res2_2,res2_2_2,res3_1],
    #         [res1_1,res2_2,res2_2_2,res3_2],
    #         [res1_1,res2_2,res2_2_2,res3_3],

    #         #RES1_2
    #         #res2-1
    #         [res1_2,res2_1,res2_1_1,res3_1],
    #         [res1_2,res2_1,res2_1_1,res3_2],
    #         [res1_2,res2_1,res2_1_1,res3_3],
    #         #res2-1-2
    #         [res1_2,res2_1,res2_1_2,res3_1],
    #         [res1_2,res2_1,res2_1_2,res3_2],
    #         [res1_2,res2_1,res2_1_2,res3_3],
    #         #res2-2
    #         [res1_2,res2_2,res2_2_1,res3_1],
    #         [res1_2,res2_2,res2_2_1,res3_2],
    #         [res1_2,res2_2,res2_2_1,res3_3],
    #         #res2-2-2
    #         [res1_2,res2_2,res2_2_2,res3_1],
    #         [res1_2,res2_2,res2_2_2,res3_2],
    #         [res1_2,res2_2,res2_2_2,res3_3],
    #     ]

    #     middle_combinations = [
    #         #RES1_1
    #         #res2-1
    #         [res1_1,res2_1,res3_1],
    #         [res1_1,res2_1,res3_2],
    #         [res1_1,res2_1,res3_3],
    #         #res2-2
    #         [res1_1,res2_2,res3_1],
    #         [res1_1,res2_2,res3_2],
    #         [res1_1,res2_2,res3_3],

    #         #RES1_2
    #         #res2-1
    #         [res1_2,res2_1,res3_1],
    #         [res1_2,res2_1,res3_2],
    #         [res1_2,res2_1,res3_3],
    #         #res2-2
    #         [res1_2,res2_2,res3_1],
    #         [res1_2,res2_2,res3_2],
    #         [res1_2,res2_2,res3_3],

    #     ]

    #     simple_combinations = [
    #         [res2_1,res3_1],
    #         [res2_1,res3_2],
    #         [res2_1,res3_3],

    #         [res2_2,res3_1],
    #         [res2_2,res3_2],
    #         [res2_2,res3_3]
    #     ]


    #     found_combinations = red.get_valid_resolutions2(game.boards)

    #     #First Element: res2_1, res3_2
    #     # print_application_list(found_combinations[0])
    #     #BUG: List with one green doctor, from which a green doctor is selected.

    #     # self.assertEqual( len(found_combinations), len(simple_combinations) )
    #     # for comb in found_combinations:
    #     #     self.assertIn(comb, simple_combinations)
    #     new_middle_combinations:list = []
    #     new_found_combinations:list = []
    #     # new_middle_combinations = sorted(middle_combinations, key=conflict_log_get_val)
    #     # new_found_combinations = sorted(found_combinations, key=conflict_log_get_val)
    #     for i in range(len(middle_combinations)):
    #         new_middle_combinations.append(hash_ConflictLog(middle_combinations[i]))
    #         new_found_combinations.append(hash_ConflictLog(found_combinations[i]))
    #     # for i in range(len(middle_combinations)):
    #     #     new_middle_combinations.append(sort_ConflictLog(middle_combinations[0]))
    #     #     new_found_combinations.append(sort_ConflictLog(found_combinations[0]))

    #     # print("\n")
    #     # print(new_middle_combinations[0][1])
    #     # print(sorted(new_middle_combinations[0][1]))
    #     # print("\n")
    #     # print(new_found_combinations[0][1])
    #     # print(sorted(new_found_combinations[0][1]) )
    #     # print("\n")
        
    #     # self.assertEqual(new_middle_combinations, new_found_combinations)
    #     # print("\n")
    #     # for i in range(len(middle_combinations)):
    #     #     print(new_middle_combinations[i])
    #     #     print(new_found_combinations[i])
    #     #     print("\n")
    #     self.assertEqual( len(new_found_combinations), len(new_middle_combinations) )
    #     for comb in new_found_combinations:
    #         for el in comb:
    #             self.assertIn(el, new_middle_combinations[0])
    #         self.assertIn(comb, new_middle_combinations)

    #     self.assertEqual( len(found_combinations), len(middle_combinations) )
    #     for comb in found_combinations:
    #         for el in comb:
    #             self.assertIn(el, middle_combinations[0])
    #         self.assertIn(comb, middle_combinations)
            

    #     #Green Doctor, Blue Doctor ->Green Doctor   res1_1
    #     #Green Priest, Blue Priest, Yellow Priest -> Green Priest   res3_2
    #     #Blue Clerk, Yellow Clerk -> Blue Clerk res2_2

    #     # self.assertEqual( len(found_combinations), len(valid_combinations) )
    #     # for comb in found_combinations:
    #     #     self.assertIn(comb, valid_combinations)

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
        a1 = (Piece(Player_Colour.GREEN, Piece_Type.DOCTOR), red_squares[1], 0)
        # External then Internal BUG: For now, these are lost.
        # a2 = (Piece(Player_Colour.BLUE, Piece_Type.CLERK), red_squares[2], 0)
        # a3 = (Piece(Player_Colour.YELLOW, Piece_Type.CLERK), red_squares[2], 0)
        #External 3
        a4 = (Piece(Player_Colour.BLUE, Piece_Type.PRIEST), red_squares[3], 0)
        a5 = (Piece(Player_Colour.GREEN, Piece_Type.PRIEST), red_squares[3], 0)
        #Independent
        a6 = (Piece(Player_Colour.YELLOW, Piece_Type.SCIENTIST), red_squares[3], 0)

        #Jumbled
        red.palace_applicants.append( a5 )
        red.palace_applicants.append( a1 )
        # red.palace_applicants.append( a2 )
        red.palace_applicants.append( a4 )
        red.palace_applicants.append( a6 )
        # red.palace_applicants.append( a3 )

        set_piece(red,4,yellow_squares[2])
        earnings_log:EarningsLog = [yellow_squares[2]]
        applications_log:ApplicationLog = [(red.pieces[0], green_squares[0], 0), (red.pieces[-1], yellow_squares[0], 0)]
        conflict_log:ConflictLog = [
            ([a1,(red_squares[1].piece, red_squares[1], 0)],a1),
            ([a4,a5],a4)
        ]
        placement_log:PlacementLog = [
            (a1,red_squares[1]),(a4,red_squares[3]),(a6,red_squares[2])
        ]
        play = (earnings_log,conflict_log,placement_log,applications_log)
        new_game = game.get_next_state(play)

        #Earnings Log
        red.money += earnings_log[0].value
        #Conflict Log
        red.palace_applicants = []
        #Placement Log
        red_squares[1].piece = a1[0]
        red_squares[3].piece = a4[0]
        red_squares[2].piece = a6[0]
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
        

if __name__ == '__main__':
    unittest.main()
