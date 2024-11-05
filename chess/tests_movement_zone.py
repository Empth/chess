import unittest
import unittest.mock

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from movement_zone import get_movement_zone
from helpers.general_helpers import convert_to_movement_set


class TestRookZone(unittest.TestCase):
    '''
    Tests Rook zone of movement is in straight directions up to (and including) first collision
    '''

    def test_rook_zone_vanilla(self):

        '''
        Tests that on otherwise blank board, rook takes all positions straight from it.
        '''
        game = Game(debug=set_up_debug(white_pieces=['R-D4']))
        board = game.board
        movement_zone = convert_to_movement_set(get_movement_zone(board=board, piece=board.get_piece([4, 4])))
        for i in range(8):
            for j in range(8):
                x, y = i+1, j+1
                if x == y == 4:
                    self.assertFalse((x, y) in movement_zone)
                elif x==4 or y==4:
                    self.assertTrue((x, y) in movement_zone)
                else:
                    self.assertFalse((x, y) in movement_zone)


if __name__ == '__main__':
    unittest.main()
