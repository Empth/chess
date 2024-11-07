import unittest
import unittest.mock

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from movement_zone import get_movement_zone
from helpers.general_helpers import algebraic_uniconverter


class TestRookZone(unittest.TestCase):
    '''
    Tests Rook zone of movement is in straight directions up to (and including) first collision
    '''

    def test_rook_zone_vanilla(self):

        '''
        Tests that on otherwise blank board, rook takes all positions straight from it, on all possible positions.
        '''
        for a in range(8):
            for b in range(8):
                true_a, true_b = a+1, b+1
                game = Game(debug=set_up_debug(white_pieces=['R-'+str(algebraic_uniconverter([true_a,true_b]))]))
                board = game.board
                movement_zone = (get_movement_zone(board=board, piece=board.get_piece([true_a, true_b])))
                for i in range(8):
                    for j in range(8):
                        x, y = i+1, j+1
                        if x == true_a and y == true_b:
                            self.assertFalse((x, y) in movement_zone)
                        elif x==true_a or y==true_b:
                            self.assertTrue((x, y) in movement_zone)
                        else:
                            self.assertFalse((x, y) in movement_zone)

    def test_rook_enemy_collider_zone(self):

        '''
        Tests that rook's straight zone tiles includes enemy colliding tiles.
        '''
        black_pieces = ['P-D3', 'R-D6', 'N-G4', 'Q-A4']
        game = Game(debug=set_up_debug(white_pieces=['R-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4, 3), (4, 5), (4, 6), (1, 4), (2, 4), (3, 4), (5, 4), (6, 4), (7, 4)])
        self.assertEqual(movement_zone, expected_zone)

    def test_rook_zone_stress_test(self):

        '''
        Stress test for rook collision
        '''
        whites = ['R-D5', 'Q-F4']
        black_pieces = ['P-D2', 'N-G4', 'Q-A4', 'Q-B4']
        game = Game(debug=set_up_debug(white_pieces=['R-D4']+whites, black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,2),(4,3),(2,4),(3,4),(5,4)])
        self.assertEqual(movement_zone, expected_zone)

    def test_rook_cannot_teamkill_zone(self):

        '''
        Tests that rooks cannot teamkill movement zone.
        '''
        
        game = Game(debug=set_up_debug(white_pieces=['R-D4', 'P-D5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,1),(4,2),(4,3),(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)])
        self.assertEqual(movement_zone, expected_zone)

    def test_rook_can_move_between_collision_zone(self):

        '''
        Tests movement zone for inbetween collision against enemy pieces
        '''
        game = Game(debug=set_up_debug(white_pieces=['R-D4'], black_pieces=['P-A4', 'P-G4', 'P-D5', 'P-D2']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,2),(4,3),(4,5),(1,4),(2,4),(3,4),(5,4),(6,4),(7,4)])
        self.assertEqual(movement_zone, expected_zone)


class TestBishopZone(unittest.TestCase):
    '''
    Tests Bishop zone of movement is in diagonal directions up to (and including) first collision
    '''

    def test_bishop_vanilla_zone(self):

        '''
        Tests that on otherwise blank board, bishop takes all positions diagonal from it, on all possible positions.
        '''
        for a in range(8):
            for b in range(8):
                true_a, true_b = a+1, b+1
                game = Game(debug=set_up_debug(white_pieces=['B-'+str(algebraic_uniconverter([true_a,true_b]))]))
                board = game.board
                movement_zone = (get_movement_zone(board=board, piece=board.get_piece([true_a, true_b])))
                for i in range(8):
                    for j in range(8):
                        x, y = i+1, j+1
                        x_diff, y_diff = abs(x-true_a), abs(y-true_b)
                        if x_diff == y_diff == 0:
                            self.assertFalse((x, y) in movement_zone)
                        elif x_diff == y_diff:
                            self.assertTrue((x, y) in movement_zone)
                        else:
                            self.assertFalse((x, y) in movement_zone)


    def test_bishop_captures_zone(self):

        '''
        Test diagonal capture against enemies zone.
        '''
        black_pieces = ['P-C3', 'R-C5', 'N-G1', 'B-G7']
        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(6,6),(7,7),(7,1),(6,2),(5,3),(3,5)])
        self.assertEqual(movement_zone, expected_zone)

    def test_bishop_collision_zone(self):

        '''
        Bishop zone stress test.
        '''
        whites = ['R-E5', 'Q-E3']
        black_pieces = ['P-G7', 'R-F2', 'N-C3', 'Q-B6', 'Q-B2']
        game = Game(debug=set_up_debug(white_pieces=['B-D4']+whites, black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(3,5),(2,6)])
        self.assertEqual(movement_zone, expected_zone)

    def test_bishop_cannot_team_kill_zone(self):

        '''
        Bishop no teamkill zone.
        '''
        game = Game(debug=set_up_debug(white_pieces=['B-D4', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(1,1),(2,2),(3,3),(1,7),(2,6),(3,5),(5,3),(6,2),(7,1)])
        self.assertEqual(movement_zone, expected_zone)

    def test_bishop_can_move_between_collision_zone(self):

        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=['P-B2', 'P-G7', 'P-B6', 'P-F2']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(2,2),(3,3),(5,5),(6,6),(7,7),(2,6),(3,5),(5,3),(6,2)])
        self.assertEqual(movement_zone, expected_zone)

    def test_bishop_cannot_move_past_collision_zone(self):

        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=['P-C3', 'P-C5', 'P-E3', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(3,5),(5,3)])
        self.assertEqual(movement_zone, expected_zone)

class TestQueenZone(unittest.TestCase):
    '''
    Tests Queen zone of movement is in straight, diagonal directions up to (and including) first collision
    '''

    def test_queen_vanilla_zone(self):

        '''
        Tests that queens, in absense of other pieces, can precisely move in straight or diagonal directions, for all pieces.
        '''

        for a in range(8):
            for b in range(8):
                true_a, true_b = a+1, b+1
                game = Game(debug=set_up_debug(white_pieces=['Q-'+str(algebraic_uniconverter([true_a,true_b]))]))
                board = game.board
                movement_zone = (get_movement_zone(board=board, piece=board.get_piece([true_a, true_b])))
                for i in range(8):
                    for j in range(8):
                        x, y = i+1, j+1
                        x_diff, y_diff = abs(x-true_a), abs(y-true_b)
                        if x == true_a and y == true_b:
                            self.assertFalse((x, y) in movement_zone)
                        elif x==true_a or y==true_b:
                            self.assertTrue((x, y) in movement_zone)
                        elif x_diff == y_diff:
                            self.assertTrue((x, y) in movement_zone)
                        else:
                            self.assertFalse((x, y) in movement_zone)
                            
    def test_queen_diagonal_captures_zone(self):
        '''
        Tests that queens can capture correctly in diagonal directions.
        Unbypassed straight means full straight range.
        '''

        black_pieces = ['P-C3', 'R-C5', 'N-G1', 'B-G7']
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(6,6),(7,7),(7,1),(6,2),(5,3),(3,5)]
                            +[(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)]
                            +[(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_straight_captures_zone(self):
        '''
        Tests that queens can capture correctly in straight directions.
        Unbypassed diagonally means full diagonal range.
        '''
        black_pieces = ['P-D3', 'R-D6', 'N-G4', 'Q-A4']
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,3),(4,5),(4,6),(1,4),(2,4),(3,4),(5,4),(6,4),(7,4)]
                            +[(1,1),(2,2),(3,3),(5,5),(6,6),(7,7),(8,8)]
                            +[(7,1),(6,2),(5,3),(3,5),(2,6),(1,7)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_straight_diagonal_captures_zone(self):
        '''
        Tests that queens can capture correctly in straight directions.
        '''
        black_pieces = ['P-D3', 'R-D6', 'N-G4', 'Q-A4'] + ['P-C3', 'R-C5', 'N-G1', 'B-G7']
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,3),(4,5),(4,6),(1,4),(2,4),(3,4),(5,4),(6,4),(7,4)] +
                            [(3,3),(5,5),(6,6),(7,7),(7,1),(6,2),(5,3),(3,5)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_straight_collision_zone(self):

        '''
        Tests that a queen cannot capture a piece straight if there is another piece blocking its straight direction.
        '''
        whites = ['R-D5', 'Q-E4']
        black_pieces = ['P-D2', 'R-D6', 'N-G4', 'Q-A4', 'Q-B4']
        game = Game(debug=set_up_debug(white_pieces=['Q-D4']+whites, black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(2,4),(3,4),(4,3),(4,2)]
                            +[(1,1),(2,2),(3,3),(5,5),(6,6),(7,7),(8,8)]
                            +[(7,1),(6,2),(5,3),(3,5),(2,6),(1,7)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_diagonal_collision_zone(self):

        '''
        Tests that a queen cannot capture a piece diagonally if there is another piece blocking its diagonal direction.
        '''
        whites = ['R-E5', 'Q-E3']
        black_pieces = ['P-G7', 'R-F2', 'N-C3', 'Q-B6', 'Q-B2']
        game = Game(debug=set_up_debug(white_pieces=['Q-D4']+whites, black_pieces=black_pieces))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(3,5),(2,6)]
                            +[(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)]
                            +[(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_cannot_team_kill_zone(self):

        '''
        Tests that queens cannot teamkill in straight or diagonal directions.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4', 'P-D5', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(1,1),(2,2),(3,3)]
                            +[(7,1),(6,2),(5,3),(3,5),(2,6),(1,7)]
                            +[(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)]
                            +[(4,1),(4,2),(4,3)])
        self.assertEqual(movement_zone, expected_zone)


    def test_queen_can_move_straight_between_collision_zone(self):

        '''
        Tests that queens can move straight to a position that is
        between its initial position and the first colliding piece in the 
        cardinal direction of movement.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=['P-A4', 'P-G4', 'P-D5', 'P-D2']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(4,2),(4,3),(4,5)]
                            +[(1,1),(2,2),(3,3),(5,5),(6,6),(7,7),(8,8)]
                            +[(7,1),(6,2),(5,3),(3,5),(2,6),(1,7)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_can_move_diagonally_between_collision_zone(self):

        '''
        Tests that queens can move diagonally to a position that is
        between its initial position and the first colliding piece in the 
        ordinal direction of movement.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=['P-B2', 'P-G7', 'P-B6', 'P-F2']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(2,2),(3,3),(5,5),(6,6),(7,7),(2,6),(3,5),(5,3),(6,2)]
                            +[(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)]
                            +[(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_cannot_move_straight_past_collision_zone(self):

        '''
        Tests that a queen can't move straight past a piece that blocks its way.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=['P-C4', 'P-E4', 'P-D5', 'P-D3']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,4),(5,4),(4,3),(4,5)]
                            +[(1,1),(2,2),(3,3),(5,5),(6,6),(7,7),(8,8)]
                            +[(7,1),(6,2),(5,3),(3,5),(2,6),(1,7)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_cannot_move_diagonally_past_collision_zone(self):

        '''
        Tests that a queen can't move diagonally past a piece that blocks its way.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=['P-C3', 'P-C5', 'P-E3', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(3,5),(5,3)]
                            +[(1,4),(2,4),(3,4),(5,4),(6,4),(7,4),(8,4)]
                            +[(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8)])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_team_bordered_zone(self):

        '''
        Tests queen blocked in all directions by team members can not move at all.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4']+['P-C4', 'P-E4', 'P-D5', 'P-D3']+['P-C3', 'P-C5', 'P-E3', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([])
        self.assertEqual(movement_zone, expected_zone)

    def test_queen_enemy_bordered_zone(self):

        '''
        Tests queen blocked in all directions can only move like a king in that turn.
        '''
        game = Game(debug=set_up_debug(white_pieces=['Q-D4'], black_pieces=['P-C4', 'P-E4', 'P-D5', 'P-D3']+['P-C3', 'P-C5', 'P-E3', 'P-E5']))
        board = game.board
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(3,5),(5,3)] + [(3,4),(5,4),(4,3),(4,5)])
        self.assertEqual(movement_zone, expected_zone)


class TestKnightZone(unittest.TestCase):

    def test_knight_vanilla_zone(self):

        '''
        Tests that knights move precisely in an L shape.
        '''

        game = Game(debug=set_up_debug(white_pieces=['N-D4']))
        board = game.board
        expected_zone = set([(2, 3), (3, 2), (6, 5), (5, 6), (3, 6), (6, 3), (2, 5), (5, 2)])
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        self.assertEqual(movement_zone, expected_zone)


    def test_knight_capture_zone(self):
        '''
        Superfluous test.
        '''
        game = Game(debug=set_up_debug(white_pieces=['N-D4'], black_pieces=['P-E2']))
        board = game.board
        expected_zone = set([(2, 3), (3, 2), (6, 5), (5, 6), (3, 6), (6, 3), (2, 5), (5, 2)])
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        self.assertEqual(movement_zone, expected_zone)

    def test_knight_jump_zone(self):
        '''
        Tests that knights can jump to its destination and bypass all collision.
        In this test, a square of pieces blocks the knight from making an L move, 
        but the knight can jump over them anyways.
        '''
        game = Game(debug=set_up_debug(white_pieces=['N-D4'], 
                                       black_pieces=['P-E2', 'P-C3', 'P-C4', 'P-C5', 'P-D5',
                                                     'P-E5', 'P-E4', 'P-E3', 'P-D3']))
        board = game.board
        expected_zone = set([(2, 3), (3, 2), (6, 5), (5, 6), (3, 6), (6, 3), (2, 5), (5, 2)])
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        self.assertEqual(movement_zone, expected_zone)

    def test_knight_cannot_team_kill(self):

        '''
        Tests that knights cannot teamkill.
        '''
        game = Game(debug=set_up_debug(white_pieces=['N-D4', 'P-E2']))
        board = game.board
        expected_zone = set([(2, 3), (3, 2), (6, 5), (5, 6), (3, 6), (6, 3), (2, 5)])
        movement_zone = (get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        self.assertEqual(movement_zone, expected_zone)

if __name__ == '__main__':
    unittest.main()
