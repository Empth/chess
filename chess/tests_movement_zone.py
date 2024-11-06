import unittest
import unittest.mock

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from movement_zone import get_movement_zone
from helpers.general_helpers import convert_to_movement_set, algebraic_uniconverter


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
                movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([true_a, true_b])))
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
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4, 3), (4, 5), (4, 6), (1, 4), (2, 4), (3, 4), (5, 4), (6, 4), (7, 4)])
        self.assertTrue(movement_zone, expected_zone)

    def test_rook_zone_stress_test(self):

        '''
        Stress test for rook collision
        '''
        whites = ['R-D5', 'Q-F4']
        black_pieces = ['P-D2', 'N-G4', 'Q-A4', 'Q-B4']
        game = Game(debug=set_up_debug(white_pieces=['R-D4']+whites, black_pieces=black_pieces))
        board = game.board
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,2),(4,3),(2,4),(3,4),(5,4)])
        self.assertTrue(movement_zone, expected_zone)

    def test_rook_cannot_teamkill_zone(self):

        '''
        Tests that rooks cannot teamkill movement zone.
        '''
        
        game = Game(debug=set_up_debug(white_pieces=['R-D4', 'P-D5']))
        board = game.board
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8),(1,4),(2,4),(3,4)])
        self.assertTrue(movement_zone, expected_zone)

    def test_rook_can_move_between_collision_zone(self):

        '''
        Tests movement zone for inbetween collision against enemy pieces
        '''
        game = Game(debug=set_up_debug(white_pieces=['R-D4'], black_pieces=['P-A4', 'P-G4', 'P-D5', 'P-D2']))
        board = game.board
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(2,4),(3,4),(5,4)])
        self.assertTrue(movement_zone, expected_zone)


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
                movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([true_a, true_b])))
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
        black_pieces = ['P-C3', 'R-C5', 'N-G2', 'B-G7']
        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=black_pieces))
        board = game.board
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        expected_zone = set([(3,3),(5,5),(6,6),(7,7),(3,5),()])
        self.assertTrue(movement_zone, expected_zone)


    def test_bishop_collision(self):

        '''
        Tests that Bishops cannot capture a piece if there is another piece blocking its direction.
        '''
        whites = ['R-E5', 'Q-E3']
        black_pieces = ['P-G7', 'R-F2', 'N-C3', 'Q-B6', 'Q-B2']
        game = Game(debug=set_up_debug(white_pieces=['B-D4']+whites, black_pieces=black_pieces))
        player_1 = game.p1
        player_2 = game.p2
        board = game.board
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[2,2])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[6,2])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[7,7])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[3,3])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[2,6])[0])


    def test_bishop_cannot_team_kill(self):

        '''
        Tests that bishops cannot teamkill.
        '''
        game = Game(debug=set_up_debug(white_pieces=['B-D4', 'P-E5']))
        player_1 = game.p1
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[5,5])[0])


    def test_bishop_fuzz(self):

        '''
        Tests that bishops on 'white' tiles (this distinction isn't implemented)
        cannot kill opponents on 'black' tiles.
        '''
        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=['K-B3', 'R-F5']))
        player_1 = game.p1
        player_2 = game.p2
        dirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

        for i in range(50000):
            new_pos_arr = []
            x, y = player_1.pieces['B-D4'].pos
            for d in dirs:
                new_pos_arr.append([x+d[0], y+d[1]])
            new_pos = random.choice(new_pos_arr)
            if new_pos[0]-1 not in range(8) or new_pos[1]-1 not in range(8):
                continue
            self.assertTrue(player_1.move_legal(pos=[x, y], dest=new_pos)[0])
            player_1.make_move(pos=[x, y], dest=new_pos)

        self.assertTrue(len(player_2.pieces), 2)


    def test_bishop_can_move_between_collision(self):

        '''
        Tests that bishops can move to a position that is
        between its initial position and the first colliding piece in the 
        ordinal direction of movement.
        '''
        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=['P-B2', 'P-G7', 'P-B6', 'P-F2']))
        player_1 = game.p1
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[3,3])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[2,2])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[1,1])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[5,5])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[6,6])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[7,7])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[8,8])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[3,5])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[2,6])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[1,7])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[5,3])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[6,2])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[7,1])[0])

    def test_bishop_cannot_move_past_collision(self):

        '''
        Tests that bishops can't move diagonally past a piece that blocks its way.
        '''
        game = Game(debug=set_up_debug(white_pieces=['B-D4'], black_pieces=['P-C3', 'P-C5', 'P-E3', 'P-E5']))
        player_1 = game.p1
        bad_values_1 = [1, 2, 6, 7, 8]
        for val in bad_values_1:
            self.assertFalse(player_1.move_legal(pos=[4,4], dest=[val, val])[0])
        bad_values_2 = [1, 2, 6, 7]
        for val in bad_values_2:
            self.assertFalse(player_1.move_legal(pos=[4,4], dest=[8-val, val])[0])


if __name__ == '__main__':
    unittest.main()
