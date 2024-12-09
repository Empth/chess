import unittest
import unittest.mock
from unittest.mock import patch

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from helpers.state_helpers import (update_players_check)
from helpers.game_helpers import clear_terminal
from movement_zone import mass_movement_zone, get_movement_zone
from misc.constants import *

'''
Tests methods implemented from clone onwards, ie clone, checkmate methods, random, castling methods, etc.
'''

class TestCloneMethods(unittest.TestCase):
    
    def test_clone_move_cannot_affect_original(self):
        '''
        Tests that a move in a cloned game doesn't affect the main game.
        '''
        '''
        game = Game()
        board = game.board
        self.assertTrue(game.turn == 'WHITE')
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        clone_p1 = clone_game.p1
        clone_p1.attempt_move(pos=[4,2], dest=[4,4])
        self.assertTrue(clone_board.piece_exists([4,4]))
        self.assertFalse(clone_board.piece_exists([4,2]))
        self.assertEqual(clone_board.get_piece([4,4]).rank, 'PAWN')

        self.assertTrue(board.piece_exists([4,2]))
        self.assertFalse(board.piece_exists([4,4]))
        self.assertEqual(board.get_piece([4,2]).rank, 'PAWN')
        '''

    def test_original_move_cannot_affect_clone(self):
        '''
        Tests that a move in the original game doesn't affect the clone game.
        '''
        '''
        game = Game()
        board = game.board
        self.assertTrue(game.turn == 'WHITE')
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        p1 = game.p1
        p1.attempt_move(pos=[4,2], dest=[4,4])
        self.assertTrue(board.piece_exists([4,4]))
        self.assertFalse(board.piece_exists([4,2]))
        self.assertEqual(board.get_piece([4,4]).rank, 'PAWN')

        self.assertTrue(clone_board.piece_exists([4,2]))
        self.assertFalse(clone_board.piece_exists([4,4]))
        self.assertEqual(clone_board.get_piece([4,2]).rank, 'PAWN')
        '''

    def test_clone_capture_cannot_affect_original(self):
        '''
        Tests that a capture in a cloned game doesn't affect the main game's pieces.
        '''
        '''
        white_pieces = ['R-A1', 'N-B1', 'B-C1', 'Q-D1', 'K-E1', 'B-F1', 'N-G1', 'R-H1']
        black_pieces = ['R-A8', 'N-B8', 'B-C8', 'Q-D8', 'K-E8', 'B-F8', 'N-G8', 'R-H8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        clone_p1 = clone_game.p1
        clone_p1.attempt_move(pos=[1,1], dest=[1,8])
        self.assertTrue(clone_board.piece_exists([1,8]))
        self.assertFalse(clone_board.piece_exists([1,1]))
        self.assertEqual(clone_board.get_piece([1,8]).rank, 'ROOK')
        self.assertEqual(len(clone_game.p1.pieces), 8)
        self.assertEqual(len(clone_game.p2.pieces), 7)

        self.assertTrue(board.piece_exists([1,8]))
        self.assertTrue(board.piece_exists([1,1]))
        self.assertEqual(board.get_piece([1,1]).rank, 'ROOK')
        self.assertEqual(board.get_piece([1,8]).rank, 'ROOK')
        self.assertTrue(len(game.p1.pieces)==len(game.p2.pieces)==8)
        '''


    def test_original_capture_cannot_affect_clone(self):
        '''
        Tests that a capture in an original game doesn't affect the cloned game's pieces.
        '''
        '''
        white_pieces = ['R-A1', 'N-B1', 'B-C1', 'Q-D1', 'K-E1', 'B-F1', 'N-G1', 'R-H1']
        black_pieces = ['R-A8', 'N-B8', 'B-C8', 'Q-D8', 'K-E8', 'B-F8', 'N-G8', 'R-H8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        p1 = game.p1
        p1.attempt_move(pos=[1,1], dest=[1,8])
        self.assertTrue(board.piece_exists([1,8]))
        self.assertFalse(board.piece_exists([1,1]))
        self.assertEqual(board.get_piece([1,8]).rank, 'ROOK')
        self.assertEqual(len(game.p1.pieces), 8)
        self.assertEqual(len(game.p2.pieces), 7)

        self.assertTrue(clone_board.piece_exists([1,8]))
        self.assertTrue(clone_board.piece_exists([1,1]))
        self.assertEqual(clone_board.get_piece([1,1]).rank, 'ROOK')
        self.assertEqual(clone_board.get_piece([1,8]).rank, 'ROOK')
        self.assertTrue(len(clone_game.p1.pieces)==len(clone_game.p2.pieces)==8)
        '''

class TestStateHelperFunctions(unittest.TestCase):

    def test_update_players_check(self):
        '''
        Tests update_players_check on board configs.
        '''
        game = Game()
        update_players_check(game)
        self.assertFalse(game.p1.in_check)
        self.assertFalse(game.p2.in_check)

        white_pieces = ['K-E1', 'Q-E7']
        black_pieces = ['K-E8', 'Q-E2']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        update_players_check(game)
        self.assertTrue(game.p1.in_check)
        self.assertTrue(game.p2.in_check)

        white_pieces = ['K-D1']
        black_pieces = ['K-E8', 'Q-D8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        update_players_check(game)
        self.assertTrue(game.p1.in_check)
        self.assertFalse(game.p2.in_check)

#---------------------------------

def get_set(arr):
    '''
    converts [[[x_1, y_1], [x_2, y_2]],...] to a set thing and returns it.
    '''
    return_set = set()
    for move in arr:
        move_tuple = get_tuple(move)
        return_set.add(move_tuple)
    return return_set

def get_tuple(move_arr):
    '''
    converts [[x_1, y_1], [x_2, y_2]] to tuples and returns it.
    '''
    return tuple([tuple(move_arr[0]), tuple(move_arr[1])])

#---------------------------------

class TestEvenMorePlayerHelperFunctions(unittest.TestCase):

    def test_get_all_legal_moves(self, debug_config=None):
        '''
        Tests that get_all_legal_moves correctly works for
        all combinatorially possible piece moves given debug_config.
        Also a stress test for unmake_turn as well.
        '''
        game = None # Exhaustive test, around 8192 options here.
        if debug_config == None:
            game = Game()
        else:
            game = Game(debug_config)
        p1 = game.p1
        p1_all_moves = p1.get_all_legal_moves() # [[[x_1, y_1], [x_2, y_2]],..., KING, QUEEN]
        for j in range(8):
            for i in range(8):
                x1, y1 = i+1, j+1
                for k in range(8):
                    for l in range(8):
                        x2, y2 = k+1, l+1
                        proposed_move = [[x1,y1],[x2,y2]] # pos, dest
                        move_success = p1.attempt_action(proposed_move)
                        if proposed_move in p1_all_moves:
                            self.assertTrue(move_success)
                            game.unmake_turn()
                        else:
                            self.assertFalse(move_success)
        
        p2 = game.p2
        # test castle on p1
        castle_legal = p1.castle_legal(KING, p2)
        castle_success = p1.attempt_action(KING)
        if castle_legal:
            self.assertTrue(castle_success)
            game.unmake_turn()
        else:
            self.assertFalse(castle_success)
        castle_legal = p1.castle_legal(QUEEN, p2)
        castle_success = p1.attempt_action(QUEEN)
        if castle_legal:
            self.assertTrue(castle_success)
            game.unmake_turn()
        else:
            self.assertFalse(castle_success)


        p2_all_moves = p2.get_all_legal_moves() # [[[x_1, y_1], [x_2, y_2]],...]
        for j in range(8):
            for i in range(8):
                x1, y1 = i+1, j+1
                for k in range(8):
                    for l in range(8):
                        x2, y2 = k+1, l+1
                        proposed_move = [[x1,y1],[x2,y2]] # pos, dest
                        move_success = p2.attempt_action(proposed_move)
                        if proposed_move in p2_all_moves:
                            self.assertTrue(move_success)
                            game.unmake_turn()
                        else:
                            self.assertFalse(move_success)

        # test castle on p2
        castle_legal = p2.castle_legal(KING, p1)
        castle_success = p2.attempt_action(KING)
        if castle_legal:
            self.assertTrue(castle_success)
            game.unmake_turn()
        else:
            self.assertFalse(castle_success)
        castle_legal = p2.castle_legal(QUEEN, p1)
        castle_success = p2.attempt_action(QUEEN)
        if castle_legal:
            self.assertTrue(castle_success)
            game.unmake_turn()
        else:
            self.assertFalse(castle_success)


    def test_get_all_legal_moves_custom(self):
        '''
        Tests that get_all_legal_moves correctly works for
        many custom board configs.
        '''
        self.test_get_all_legal_moves()
        self.test_get_all_legal_moves(set_up_debug(white_pieces=['K-E1', 'Q-D1'], 
                                                                   black_pieces=['K-E8']))
        self.test_get_all_legal_moves(set_up_debug(white_pieces = ['K-E1', 'Q-E7'],
                                                                   black_pieces = ['K-E8', 'Q-E2']))
        self.test_get_all_legal_moves(set_up_debug(
        white_pieces = ['R-A1', 'N-B1', 'B-C1', 'Q-D1', 'K-E1', 'B-F1', 'N-G1', 'R-H1'],
        black_pieces = ['R-A8', 'N-B8', 'B-C8', 'Q-D8', 'K-E8', 'B-F8', 'N-G8', 'R-H8']))
        '''
        Disabling this test, as these legality tests dont work for ccustom kingless configs.
        self.test_get_all_legal_moves(set_up_debug(white_pieces=['K-D4'],
        black_pieces = ['P-C3', 'P-C4', 'P-C5', 'P-D5', 'P-E5', 'P-E4', 'P-E3', 'P-D3']))
        self.test_get_all_legal_moves(set_up_debug(white_pieces=['K-D4'],
        black_pieces = ['R-C3', 'R-C4', 'R-C5', 'R-D5', 'R-E5', 'R-E4', 'R-E3', 'R-D3']))
        '''

class TestRandomMove(unittest.TestCase):

    def test_random_move_only_legal_move_is_used(self):
        '''
        Given a position where WHITE has only 1 legal move if it doesn't wish to get checkmated, tests that WHITE
        will use it.
        '''
        white_pieces = ['K-E1', 'R-E4']
        black_pieces = ['Q-E3', 'N-H2', 'N-B2', 'K-H8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        # update check first, to get correct game state.
        update_players_check(game)
        p1.make_random_move()
        # WHITE ROOK has to move E4 -> E3. Check this.
        self.assertFalse(board.piece_exists([5, 4]))
        self.assertEqual(board.get_piece([5, 3]).color, 'WHITE')
        self.assertEqual(board.get_piece([5, 3]).rank, 'ROOK')
        self.assertTrue('Q-E3' not in p2.pieces) # BLACK QUEEN was captured.

    def test_only_random_move_leads_to_checkmate(self):
        '''
        Given a position where WHITE has only 1 legal move if it doesn't wish to get checkmated, tests that WHITE
        will use it, and that move correctly leads to checkmate.
        '''
        white_pieces = ['K-A8', 'P-A6', 'B-A5', 'N-E5']
        black_pieces = ['Q-B7', 'K-C8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        # update check first, to get correct game state.
        update_players_check(game)
        self.assertEqual(game.turn, 'WHITE')
        os.system('cls')
        print(game.board)
        input_commands = ['r', 'PAUSE']
        with patch('builtins.input', side_effect=input_commands):
            game.start()
        board = game.board
        p1 = game.p1
        p2 = game.p2
        # WHITE PAWN has to move A6 -> B7 as it has to escape checkmate. Check this.
        self.assertFalse(board.piece_exists([1, 6]))
        self.assertEqual(board.get_piece([2, 7]).color, 'WHITE')
        self.assertEqual(board.get_piece([2, 7]).rank, 'PAWN')
        self.assertTrue('Q-B7' not in p2.pieces) # BLACK QUEEN was captured.
        self.assertEqual(game.winner, 'WHITE') # WHITE should win by checkmate.
        # clear_terminal() # dont


class TestCheckmateInGames(unittest.TestCase):

    '''
    Test a variety of moves in which checkmate is delivered.
    '''
    def test_fools_mate(self):
        '''
        Test fool's mate checkmate in 2 moves.
        '''
        game = Game()
        self.assertEqual(game.turn, 'WHITE')
        input_commands = (['f2f3']+['e7e5']+['g2g4']+['d8h4'])
        with patch('builtins.input', side_effect=input_commands):
            game.start()
        self.assertEqual(game.winner, 'BLACK')


class TestCastling(unittest.TestCase):

    '''
    Tests functionality of castling.
    '''

    def test_castle_custom_gap_config(self):
        '''
        Tests castling where kings <-> rooks have gaps between them
        in a custom board config. Checks that the castle is legal, 
        then tests the two sides of castling for each player, and verifies that 
        kings and rooks land in the correct positions.
        '''
        white_pieces = (['P-A2', 'P-B2', 'P-C2', 'P-D2', 'P-E2', 'P-F2', 'P-G2', 'P-H2']+
            ['R-A1', 'K-E1', 'R-H1'])
        black_pieces = (['P-A7', 'P-B7', 'P-C7', 'P-D7', 'P-E7', 'P-F7', 'P-G7', 'P-H7']+
            ['R-A8', 'K-E8', 'R-H8'])
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        game.turn = 'WHITE'
        # w/o having to reconfigure game repeatedly
        self.assertTrue(p1.castle_legal('KING', p2))
        self.assertTrue(p1.castle_legal('QUEEN', p2))
        self.assertTrue(p2.castle_legal('KING', p1))
        self.assertTrue(p2.castle_legal('QUEEN', p1))
        # p1 kingside
        with patch('builtins.input', side_effect=['kc', 'pause']):
            game.start()

        self.assertIsNone(board.get_piece([2, 1]))
        self.assertIsNone(board.get_piece([3, 1]))
        self.assertIsNone(board.get_piece([4, 1]))

        self.assertIsNone(board.get_piece([5, 1]))
        self.assertIsNone(board.get_piece([8, 1]))

        self.assertEqual(board.get_piece([6,1]).rank, 'ROOK')
        self.assertEqual(board.get_piece([6,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([6,1]).name, 'R-H1')
        self.assertEqual(board.get_piece([7,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([7,1]).rank, 'KING')
        self.assertEqual(board.get_piece([7,1]).name, 'K-E1')

        self.assertEqual(board.get_piece([1,1]).rank, 'ROOK')
        self.assertEqual(board.get_piece([1,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([1,1]).name, 'R-A1')

        # now go back
        game.unmake_turn()

        # p1 queenside
        with patch('builtins.input', side_effect=['qc', 'pause']):
            game.start()
            
        self.assertIsNone(board.get_piece([1, 1]))
        self.assertIsNone(board.get_piece([2, 1]))

        self.assertIsNone(board.get_piece([5, 1]))
        self.assertIsNone(board.get_piece([6, 1]))
        self.assertIsNone(board.get_piece([7, 1]))

        self.assertEqual(board.get_piece([4,1]).rank, 'ROOK')
        self.assertEqual(board.get_piece([4,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([4,1]).name, 'R-A1')
        self.assertEqual(board.get_piece([3,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([3,1]).rank, 'KING')
        self.assertEqual(board.get_piece([3,1]).name, 'K-E1')

        self.assertEqual(board.get_piece([8,1]).rank, 'ROOK')
        self.assertEqual(board.get_piece([8,1]).color, 'WHITE')
        self.assertEqual(board.get_piece([8,1]).name, 'R-H1')


        game.unmake_turn() # go back
        game.turn = 'BLACK'

        # p2 kingside
        with patch('builtins.input', side_effect=['kc', 'pause']):
            game.start()

        self.assertIsNone(board.get_piece([2, 8]))
        self.assertIsNone(board.get_piece([3, 8]))
        self.assertIsNone(board.get_piece([4, 8]))

        self.assertIsNone(board.get_piece([5, 8]))
        self.assertIsNone(board.get_piece([8, 8]))

        self.assertEqual(board.get_piece([6,8]).rank, 'ROOK')
        self.assertEqual(board.get_piece([6,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([6,8]).name, 'R-H8')
        self.assertEqual(board.get_piece([7,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([7,8]).rank, 'KING')
        self.assertEqual(board.get_piece([7,8]).name, 'K-E8')

        self.assertEqual(board.get_piece([1,8]).rank, 'ROOK')
        self.assertEqual(board.get_piece([1,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([1,8]).name, 'R-A8')

        game.unmake_turn()

        # p2 queenside
        with patch('builtins.input', side_effect=['qc', 'pause']):
            game.start()
            
        self.assertIsNone(board.get_piece([1, 8]))
        self.assertIsNone(board.get_piece([2, 8]))

        self.assertIsNone(board.get_piece([5, 8]))
        self.assertIsNone(board.get_piece([6, 8]))
        self.assertIsNone(board.get_piece([7, 8]))

        self.assertEqual(board.get_piece([4,8]).rank, 'ROOK')
        self.assertEqual(board.get_piece([4,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([4,8]).name, 'R-A8')
        self.assertEqual(board.get_piece([3,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([3,8]).rank, 'KING')
        self.assertEqual(board.get_piece([3,8]).name, 'K-E8')

        self.assertEqual(board.get_piece([8,8]).rank, 'ROOK')
        self.assertEqual(board.get_piece([8,8]).color, 'BLACK')
        self.assertEqual(board.get_piece([8,8]).name, 'R-H8')


    def test_castle_can_checkmate(self):
        '''
        Tests that player can checkmate from castling.
        '''
        white_pieces = ['K-E1', 'R-E2', 'R-H1', 'Q-G3']
        black_pieces = ['K-F5']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        self.assertTrue(p1.castle_legal('KING', p2))
        game.turn = 'WHITE'
        with patch('builtins.input', side_effect=['kc', 'pause']):
            game.start()

        self.assertEqual(game.winner, 'WHITE')


    def test_castle_can_stalemate(self):
        '''
        Tests that player can stalemate from castling.
        '''
        white_pieces = ['K-E1', 'R-H1', 'Q-H3']
        black_pieces = ['K-G5', 'P-H4', 'P-H5', 'P-H6', 'P-G6']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        self.assertTrue(p1.castle_legal('KING', p2))
        game.turn = 'WHITE'
        with patch('builtins.input', side_effect=['kc', 'pause']):
            game.start()

        self.assertEqual(game.winner, 'DRAW')

class TestEnPassant(unittest.TestCase):

    '''
    Tests en passant moves.
    '''

    def test_en_passant_custom_config_true_positive(self):
        '''
        Tests en passant on custom board config on
        cases where it should work.
        '''
        white_pieces = ['K-A1', 'P-D2']
        black_pieces = ['K-A8', 'P-E4', 'P-C4']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        p1 = game.p1
        p2 = game.p2
        p1.attempt_move([4,2], [4,4])
        self.assertTrue(p2.move_pseudolegal([5, 4], [4, 3]))
        self.assertTrue(p2.move_pseudolegal([3, 4], [4, 3]))
        p2.attempt_move([5, 4], [4, 3])
        self.assertEqual(p2.pieces['P-E4'].pos, [4, 3])
        self.assertTrue('P-D2' not in p1.pieces)
        self.assertEqual(len(p1.pieces), 1)

        game.unmake_turn()
        p2.attempt_move([3, 4], [4, 3])
        self.assertEqual(p2.pieces['P-C4'].pos, [4, 3])
        self.assertTrue('P-D2' not in p1.pieces)
        self.assertEqual(len(p1.pieces), 1)
        
        # Now test en passant against opposing black color.

        white_pieces = ['K-A1', 'P-E5', 'P-C5']
        black_pieces = ['K-A8', 'P-D7']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        p1 = game.p1
        p2 = game.p2
        p2.attempt_move([4,7], [4,5])
        self.assertTrue(p1.move_pseudolegal([5, 5], [4, 6]))
        self.assertTrue(p1.move_pseudolegal([3, 5], [4, 6]))
        p1.attempt_move([5, 5], [4, 6])
        self.assertEqual(p1.pieces['P-E5'].pos, [4, 6])
        self.assertTrue('P-D7' not in p2.pieces)
        self.assertEqual(len(p2.pieces), 1)

        game.unmake_turn()
        p1.attempt_move([3, 5], [4, 6])
        self.assertEqual(p1.pieces['P-C5'].pos, [4, 6])
        self.assertTrue('P-D7' not in p2.pieces)
        self.assertEqual(len(p2.pieces), 1)

    def test_en_passant_custom_config_true_negative_1(self):
        '''
        Test if black pawn starts with 2 tile forward, then white makes some different move, then
        white shouldn't be able to en passant capture on the second turn.
        '''
        game = Game()
        p1 = game.p1
        p2 = game.p2
        p1.attempt_move([4,2],[4,4])
        p2.attempt_move([1,7],[1,6])
        p1.attempt_move([4,4],[4,5])
        p2.attempt_move([5,7],[5,5])
        self.assertTrue(p1.move_pseudolegal([4,5],[5,6]))
        p1.attempt_move([1,2],[1,3])
        p2.attempt_move([1,6],[1,5])
        self.assertFalse(p1.move_pseudolegal([4,5],[5,6]))

    def test_en_passant_custom_config_true_negative_2(self):
        '''
        White can't en passant capture if Black starts with single tile forward.
        '''
        game = Game()
        p1 = game.p1
        p2 = game.p2
        p1.attempt_move([4,2],[4,4])
        p2.attempt_move([1,7],[1,6])
        p1.attempt_move([4,4],[4,5])
        p2.attempt_move([1,6],[1,5])
        p1.attempt_move([4,5],[4,6])
        p2.attempt_move([5,7],[5,6])
        self.assertFalse(p1.move_pseudolegal([4,6],[5,7]))

    def test_en_passant_movement_zone(self):
        '''
        Tests movement zone for en passant displays correctly if it should or should not exist.
        '''

        white_pieces = ['K-A1', 'P-D2']
        black_pieces = ['K-A8', 'P-E4', 'P-C4']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        p1.attempt_move([4,2], [4,4])
        self.assertTrue((4, 3) in get_movement_zone(board, board.get_piece([5,4])))
        self.assertTrue((4, 3) in get_movement_zone(board, board.get_piece([3,4])))
        p2.attempt_move([1,8], [1,7])
        p1.attempt_move([1,1], [1,2])
        # no more en passant
        self.assertFalse((4, 3) in get_movement_zone(board, board.get_piece([5,4])))
        self.assertFalse((4, 3) in get_movement_zone(board, board.get_piece([3,4])))
        
        # Now test en passant against opposing black color.

        white_pieces = ['K-A1', 'P-E5', 'P-C5']
        black_pieces = ['K-A8', 'P-D7']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        board = game.board
        p1 = game.p1
        p2 = game.p2
        p2.attempt_move([4,7], [4,5])
        self.assertTrue((4, 6) in get_movement_zone(board, board.get_piece([5,5])))
        self.assertTrue((4, 6) in get_movement_zone(board, board.get_piece([3,5])))
        p1.attempt_move([1,1], [1,2])
        p2.attempt_move([1,8], [1,7])
        self.assertFalse((4, 6) in get_movement_zone(board, board.get_piece([5,5])))
        self.assertFalse((4, 6) in get_movement_zone(board, board.get_piece([3,5])))


if __name__ == '__main__':
    unittest.main()