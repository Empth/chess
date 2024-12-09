import unittest
import unittest.mock
from unittest.mock import patch

from game import Game
from debug import Debug
from piece import Piece
import random
import os

def set_up_debug(white_pieces = [], black_pieces = [], turn_state=None):
    mapper = {}
    for piece in white_pieces + black_pieces:
        assert len(piece) == 4
    if black_pieces != []:
        mapper['BLACK'] = black_pieces
    if white_pieces != []:
        mapper['WHITE'] = white_pieces
    return Debug(board_state=mapper, turn_state=turn_state)

class TestBoardMoves(unittest.TestCase):
    print('')
    
if __name__ == '__main__':
    unittest.main()