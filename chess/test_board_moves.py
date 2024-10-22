import unittest

from game import Game
from debug import Debug
from piece import Piece

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
        self.assertEqual(board.get_piece([1, 1]).name, 'P-A1')
        self.assertEqual(board.get_piece([2, 2]).name, 'R-B2')
        self.assertEqual(board.get_piece([3, 3]).name, 'P-C3')

    def test_get_nonexistant_piece(self):
        '''
        Tests that get_piece returns None for empty tile.
        '''
        white_pieces = ['P-A1', 'R-B2', 'P-C3']
        debug = set_up_debug(white_pieces=white_pieces)
        game = Game(debug=debug)
        board = game.board
        self.assertEqual(board.get_piece([2, 1]), None)

    def test_empty_board_debug(self):
        '''
        Tests that an empty board created via Debug object corresponds to
        an empty game state, ie the board has no pieces, and players have 
        no pieces in their collection.
        '''
        game = Game(debug=set_up_debug())
        board = game.board
        for i in range(8):
            for j in range(8):
                self.assertEqual(board.game_board[i][j], None)
        player_1 = game.p1
        player_2 = game.p2
        self.assertEqual(player_1.pieces, {})
        self.assertEqual(player_2.pieces, {})


    def test_add_piece(self):
        '''
        Tests that add_or_replace_piece on empty board adds a piece, 
        and that the piece has correct position, and is in WHITE player's
        collection. Name of piece may be messed up.
        '''
        game = Game(debug=set_up_debug())
        board = game.board
        pawn = Piece(color='WHITE', rank='PAWN', player=game.p1, pos=[6,6]) # pos (6, 6) because we don't use this otherwise
        board.add_or_replace_piece(piece=pawn, pos=[1,2])
        self.assertIsNotNone(board.get_piece([1, 2]))
        self.assertEqual(board.get_piece([1, 2]).pos, [1, 2])
        self.assertEqual(board.get_piece([1, 2]).name, 'P-F6')
        self.assertEqual(board.get_piece([1, 2]), game.p1.pieces['P-F6'])

    def test_replace_piece(self):
        '''
        Tests that replaced piece is returned and that it is not in player's wallet.
        '''
        game = Game(debug=set_up_debug(white_pieces=['P-A2'], black_pieces=['Q-B8']))
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        p1_pawn = player_1.pieces['P-A2']
        p2_queen = player_2.pieces['Q-B8']
        self.assertEqual(p1_pawn.pos, [1, 2])
        self.assertEqual(p1_pawn.rank, 'PAWN')
        self.assertEqual(p1_pawn.color, 'WHITE')
        self.assertEqual(p2_queen.pos, [2, 8])
        self.assertEqual(p2_queen.rank, 'QUEEN')
        self.assertEqual(p2_queen.color, 'BLACK')
        replaced = board.add_or_replace_piece(pos=[2, 8], piece=p1_pawn) # god pawn, also this isn't a move
        #print(str(board))
        self.assertEqual(p2_queen, replaced)
        self.assertEqual(player_2.pieces, {})
        self.assertIsNone(board.get_piece(pos=[1,2])) # existant piece replace is a move
        self.assertEqual(len(player_1.pieces), 1) # existant piece replace is a move


    def test_replace_own_piece(self):
        '''
        Tests promotion mechanic, in replacing white's pawn to queen.
        '''
        game = Game(debug=set_up_debug(white_pieces=['P-A8']))
        board = game.board
        # print(str(board))
        player_1 = game.p1
        pawn = player_1.pieces['P-A8']
        promoted_queen = Piece(color='WHITE', rank='QUEEN', player=player_1, pos=[2, 7])
        replaced = board.add_or_replace_piece(pos=[1, 8], piece=promoted_queen)
        # print(str(board))
        self.assertIsNone(replaced.pos)
        self.assertEqual(replaced, pawn)
        self.assertEqual(len(player_1.pieces), 1)
        self.assertEqual(promoted_queen, board.get_piece(pos=[1, 8]))
        self.assertEqual(promoted_queen, player_1.pieces['Q-B7'])

    def test_move_piece(self):
        '''
        Tests that we can move a piece.
        '''
        game = Game(debug=set_up_debug(white_pieces=['P-B2']))
        board = game.board
        #print(str(board))
        player_1 = game.p1
        replaced = board.move_piece(pos=[2, 4], piece=board.get_piece(pos=[2, 2]))
        #print(str(board))
        self.assertIsNone(replaced)
        self.assertIsNone(board.get_piece(pos=[2, 2]))
        self.assertEqual(len(player_1.pieces), 1)
        new_pawn = board.get_piece(pos=[2, 4])
        self.assertEqual(new_pawn, player_1.pieces['P-B2'])
        self.assertEqual(new_pawn.pos, [2, 4])
        replaced = board.move_piece(pos=[2, 5], piece=board.get_piece(pos=[2, 4]))
        self.assertIsNone(replaced)
        self.assertIsNone(board.get_piece(pos=[2, 4]))
        self.assertEqual(len(player_1.pieces), 1)
        new_pawn = board.get_piece(pos=[2, 5])
        self.assertEqual(new_pawn, player_1.pieces['P-B2'])
        self.assertEqual(new_pawn.pos, [2, 5])

    def test_move_piece_capture(self):
        '''
        Tests that we can move a piece and set it up to capture.
        '''
        game = Game(debug=set_up_debug(white_pieces=['P-B2'], black_pieces=['P-C3']))
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        moving_pawn = board.get_piece([2, 2])
        to_die = board.get_piece(pos=[3, 3])
        replaced = board.move_piece(pos=[3, 3], piece=board.get_piece(pos=[2, 2]))
        self.assertEqual(to_die, replaced)
        self.assertEqual(player_2.pieces, {})
        self.assertIsNone(board.get_piece(pos=[2, 2]))
        self.assertEqual(len(player_1.pieces), 1)
        self.assertIsNotNone(board.get_piece([3, 3]))
        self.assertEqual(board.get_piece([3, 3]).pos, [3, 3])
        self.assertEqual(moving_pawn, player_1.pieces['P-B2'])



if __name__ == '__main__':
    unittest.main()