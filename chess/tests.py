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
        Tests that we can move a piece make it capture.
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


class TestPlayerPawnMoves(unittest.TestCase):
    '''
    Tests moves that the player makes, and their legality.
    '''

    def test_move_starting_pawn(self):
        '''
        Tests that a pawn in its starting position only moves 1 or 2 units straight.
        '''
        game = Game()
        board = game.board
        player_1 = game.p1
        player_2 = game.p2

        self.assertFalse(player_1.move_legal(pos=[1,2], dest=[1,5])[0])
        self.assertTrue(player_1.move_legal(pos=[1,2], dest=[1,3])[0])
        player_1.make_move(pos=[1,2], dest=[1,3])
        w_pawn_1 = board.get_piece([1, 3])
        self.assertEqual(w_pawn_1.name, 'P-A2')
        self.assertEqual(w_pawn_1.color, 'WHITE')
        self.assertEqual(player_1.pieces['P-A2'], w_pawn_1)
        self.assertIsNone(board.get_piece([1, 2]))

        self.assertFalse(player_1.move_legal(pos=[2,2], dest=[2,6])[0])
        self.assertTrue(player_1.move_legal(pos=[2,2], dest=[2,4])[0])
        player_1.make_move(pos=[2,2], dest=[2,4])
        w_pawn_2 = board.get_piece([2, 4])
        self.assertEqual(w_pawn_2.name, 'P-B2')
        self.assertEqual(w_pawn_2.color, 'WHITE')
        self.assertEqual(player_1.pieces['P-B2'], w_pawn_2)
        self.assertIsNone(board.get_piece([2, 2]))

        self.assertFalse(player_2.move_legal(pos=[4,7], dest=[4,4])[0])
        self.assertTrue(player_2.move_legal(pos=[1,7], dest=[1,6])[0])
        player_2.make_move(pos=[1,7], dest=[1,6])
        b_pawn_1 = board.get_piece([1,6])
        self.assertEqual(b_pawn_1.name, 'P-A7')
        self.assertEqual(b_pawn_1.color, 'BLACK')
        self.assertEqual(player_2.pieces['P-A7'], b_pawn_1)
        self.assertIsNone(board.get_piece([1, 7]))

        self.assertFalse(player_2.move_legal(pos=[3,7], dest=[3,4])[0])
        self.assertTrue(player_2.move_legal(pos=[2,7], dest=[2,5])[0])
        player_2.make_move(pos=[2,7], dest=[2,5])
        b_pawn_2 = board.get_piece([2,5])
        self.assertEqual(b_pawn_2.name, 'P-B7')
        self.assertEqual(b_pawn_2.color, 'BLACK')
        self.assertEqual(player_2.pieces['P-B7'], b_pawn_2)
        self.assertIsNone(board.get_piece([2, 7]))


    def test_move_nonstarting_pawn(self):
        '''
        Tests that a pawn outside of its starting position only moves 1 straight and not 2.
        '''
        game = Game()
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        player_1.make_move(pos=[1,2], dest=[1,3])
        player_1.make_move(pos=[2,2], dest=[2,4])
        player_2.make_move(pos=[8,7], dest=[8,6])
        player_2.make_move(pos=[7,7], dest=[7,5])

        self.assertTrue(player_1.move_legal(pos=[1,3], dest=[1,4])[0])
        self.assertFalse(player_1.move_legal(pos=[1,3], dest=[1,5])[0])
        self.assertTrue(player_1.move_legal(pos=[2,4], dest=[2,5])[0])
        self.assertFalse(player_1.move_legal(pos=[2,4], dest=[2,6])[0])
        self.assertTrue(player_2.move_legal(pos=[8,6], dest=[8,5])[0])
        self.assertFalse(player_2.move_legal(pos=[8,6], dest=[8,4])[0])
        self.assertTrue(player_2.move_legal(pos=[8,6], dest=[8,5])[0])
        self.assertFalse(player_2.move_legal(pos=[8,6], dest=[8,4])[0])


    def test_cannot_move_blank_space(self):
        '''
        Test that we cannot move from a blank position on the board.
        '''
        game = Game()
        player_1 = game.p1
        player_2 = game.p2

        self.assertFalse(player_1.move_legal(pos=[1,3], dest=[2,4])[0])
        self.assertFalse(player_1.move_legal(pos=[2,4], dest=[3,6])[0])
        self.assertFalse(player_2.move_legal(pos=[8,6], dest=[7,5])[0])
        self.assertFalse(player_2.move_legal(pos=[7,5], dest=[6,4])[0])
        
    
    def test_cannot_move_wrong_color(self):
        '''
        Test that a player cannot move its opponent's piece on the board.
        '''

        game = Game()
        player_1 = game.p1
        player_2 = game.p2
        self.assertFalse(player_1.move_legal(pos=[8,7], dest=[8,6])[0])
        self.assertFalse(player_1.move_legal(pos=[8,7], dest=[8,5])[0])
        self.assertFalse(player_2.move_legal(pos=[1,2], dest=[1,3])[0])
        self.assertFalse(player_2.move_legal(pos=[1,2], dest=[1,4])[0])

    def test_pawn_cannot_backtrack(self):
        '''
        Test that a pawn cannot move backwards/backtrack.
        '''

        game = Game()
        player_1 = game.p1
        player_2 = game.p2
        player_1.make_move(pos=[1,2], dest=[1,3])
        player_1.make_move(pos=[2,2], dest=[2,4])
        self.assertFalse(player_1.move_legal(pos=[1,3], dest=[1,2])[0])
        self.assertFalse(player_1.move_legal(pos=[1,3], dest=[1,2])[0])
        player_2.make_move(pos=[1,7], dest=[1,6])
        player_2.make_move(pos=[2,7], dest=[2,5])
        self.assertFalse(player_2.move_legal(pos=[1,6], dest=[1,7])[0])
        self.assertFalse(player_1.move_legal(pos=[2,5], dest=[2,7])[0])

    def test_pawn_capture(self):
        '''
        Test that a pawn can only capture diagonally forward.
        '''

        game = Game()
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        killer_pawn = board.get_piece([1, 2])
        board.move_piece(pos=[4, 4], piece=killer_pawn)
        board.move_piece(pos=[5, 5], piece=board.get_piece([1, 8]))
        board.move_piece(pos=[4, 5], piece=board.get_piece([2, 8]))
        board.move_piece(pos=[3, 3], piece=board.get_piece([3, 8]))
        self.assertFalse(player_1.move_legal(pos=[4, 4], dest=[3, 3])[0]) # can't capture diagonally backwards
        self.assertFalse(player_1.move_legal(pos=[4, 4], dest=[4, 5])[0]) # can't capture straight forward
        self.assertTrue(player_1.move_legal(pos=[4, 4], dest=[5, 5])[0])
        player_1.make_move(pos=[4, 4], dest=[5, 5])
        self.assertTrue('R-A8' not in player_2.pieces)
        self.assertIsNone(board.get_piece([4, 4]))
        self.assertEqual(killer_pawn, player_1.pieces['P-A2'])
        self.assertEqual(killer_pawn.pos, [5, 5])

        # reset, check black captures "forward"
        game = Game()
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        killer_pawn = board.get_piece([1, 7])
        board.move_piece(pos=[4, 4], piece=killer_pawn)
        board.move_piece(pos=[5, 5], piece=board.get_piece([1, 1]))
        board.move_piece(pos=[3, 3], piece=board.get_piece([2, 1]))
        self.assertFalse(player_2.move_legal(pos=[4, 4], dest=[5, 5])[0]) # can't capture diagonally backwards
        self.assertTrue(player_2.move_legal(pos=[4, 4], dest=[3, 3])[0])
        player_2.make_move(pos=[4,4], dest=[3,3])
        self.assertTrue('N-B1' not in player_1.pieces)
        self.assertIsNone(board.get_piece([4, 4]))
        self.assertEqual(killer_pawn, player_2.pieces['P-A7'])
        self.assertEqual(killer_pawn.pos, [3,3])

    def test_pawn_promotion(self):
        '''
        Test that a pawn that reaches its relative end of the board is promoted to Queen.
        '''

        game = Game(debug=set_up_debug(white_pieces=['P-A7'], black_pieces=['P-A2']))
        board = game.board
        player_1 = game.p1
        player_2 = game.p2
        self.assertTrue(player_1.move_legal(pos=[1,7], dest=[1,8])[0])
        self.assertTrue(player_2.move_legal(pos=[1,2], dest=[1,1])[0])
        player_1.make_move(pos=[1,7], dest=[1,8])
        player_2.make_move(pos=[1,2], dest=[1,1])
        self.assertEqual(len(player_1.pieces), 1)
        self.assertEqual(len(player_2.pieces), 1)
        queen_1 = None
        queen_2 = None
        for piece in player_1.pieces:
            queen_1 = piece
            self.assertTrue(piece.rank == 'QUEEN')
            self.assertEqual(piece.pos, [1, 8])
        for piece in player_2.pieces:
            queen_2 = piece
            self.assertTrue(piece.rank == 'QUEEN')
            self.assertEqual(piece.pos, [1, 1])
        self.assertIsNone(board.get_piece([1,7]))
        self.assertIsNone(board.get_piece([1,2]))
        self.assertEqual(queen_1, board.get_piece([1,8]))
        self.assertEqual(queen_2, board.get_piece([1,1]))


    def test_cannot_move_oob(self):
        '''
        Tests that we cannot move any piece out of bounds.
        '''
        game = Game(debug=set_up_debug(white_pieces=['P-B2']))
        player_1 = game.p1
        self.assertFalse(player_1.move_legal(pos=[2,2], dest=[0,0])[0])
        self.assertFalse(player_1.move_legal(pos=[2,2], dest=[0,9])[0])
        self.assertFalse(player_1.move_legal(pos=[2,2], dest=[-2,9])[0])

    def test_pawn_cannot_teamkill_diagonally(self):
        '''
        Test that a pawn cannot diagonally team kill its own team member
        '''

        game = Game(debug=set_up_debug(white_pieces=['P-A2', 'Q-B3']))
        player_1 = game.p1
        self.assertFalse(player_1.move_legal(pos=[1, 2], dest=[2, 3])[0]) # can't team kill your own kind
    
    def test_piece_cannot_stall(self):
        '''
        Test that a piece cannot do a stall as a move, it must move to a different position.
        '''

        game = Game()
        player_1 = game.p1
        for i in range(8):
            for j in range(2):
                x, y = i+1, j+1
                self.assertFalse(player_1.move_legal(pos=[x, y], dest=[x, y])[0])


class TestPlayerRookMoves(unittest.TestCase):
    '''
    Tests moves that the player makes for their rooks, and their legality.
    '''

    def test_rook_legal_moves(self):

        '''
        Tests that rooks, in absense of other pieces, can precisely move only in straight directions.
        '''

        game = Game(debug=set_up_debug(white_pieces=['R-D4']))
        player_1 = game.p1
        for i in range(8):
            for j in range(8):
                x, y = i+1, j+1
                if x == y == 4:
                    continue
                if x==4 or y==4:
                    self.assertTrue(player_1.move_legal(pos=[4, 4], dest=[x, y])[0])
                else:
                    self.assertFalse(player_1.move_legal(pos=[4, 4], dest=[x, y])[0])

    def test_rook_captures(self):

        '''
        Tests that rooks can capture correctly in straight directions.
        '''
        black_pieces = ['P-D3', 'R-D6', 'N-G4', 'Q-A4']
        game = Game(debug=set_up_debug(white_pieces=['R-D4'], black_pieces=black_pieces))
        player_1 = game.p1
        player_2 = game.p2
        for code in black_pieces:
            enemy_pos = player_2.pieces[code].pos
            self.assertTrue(player_1.move_legal(pos=[4,4], dest=enemy_pos))
        self.assertTrue(player_2.move_legal(pos=[4,6], dest=[4,4]))
        player_1.make_move(pos=[4,4], dest=[4,6])
        self.assertEqual(player_1.pieces['R-D4'].pos == [4, 6])
        self.assertEqual(len(player_2.pieces), 3)
        self.assertTrue('R-D6' not in player_2.pieces)

    def test_rook_collision(self):

        '''
        Tests that rooks cannot capture a piece if there is another piece blocking its direction.
        '''
        whites = ['R-D5', 'Q-E4']
        black_pieces = ['P-D2', 'R-D6', 'N-G4', 'Q-A4', 'Q-B4']
        game = Game(debug=set_up_debug(white_pieces=['R-D4']+whites, black_pieces=black_pieces))
        player_1 = game.p1
        player_2 = game.p2
        board = game.board
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[1,4])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[4,6])[0])
        self.assertFalse(player_1.move_legal(pos=[4,4], dest=[7,4])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[4,2])[0])
        self.assertTrue(player_1.move_legal(pos=[4,4], dest=[2,4])[0])
        self.assertFalse(player_2.move_legal(pos=[4,6], dest=[4,4])[0])
        

if __name__ == '__main__':
    unittest.main()