import unittest

from game import Game
from debug import Debug

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
    
    def test_get_existant_piece(self):
        '''
        Tests that get_piece works for pieces on board
        '''
        white_pieces = ['P-A1', 'R-B2', 'P-C3']
        debug = set_up_debug(white_pieces=white_pieces)
        game = Game(debug=debug)
        board = game.board
        self.assertEqual(str(board.get_piece([1, 1])), 'P-A1')
        self.assertEqual(str(board.get_piece([2, 2])), 'R-B2')
        self.assertEqual(str(board.get_piece([3, 3])), 'P-C3')


if __name__ == '__main__':
    unittest.main()