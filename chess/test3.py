import unittest
import unittest.mock
from unittest.mock import patch

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from helpers.state_helpers import (update_players_check, move_puts_player_in_check, move_locks_opponent, 
                                   clone_game_and_get_game_state_based_on_move)
from helpers.game_helpers import clear_terminal
from movement_zone import mass_movement_zone

'''
Tests methods implemented from clone onwards, ie clone, checkmate methods, random, castling methods, etc.
'''

class TestCloneMethods(unittest.TestCase):
    
    def test_clone_move_cannot_affect_original(self):
        '''
        Tests that a move in a cloned game doesn't affect the main game.
        '''
        game = Game()
        board = game.board
        self.assertTrue(game.turn == 'WHITE')
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        clone_p1 = clone_game.p1
        clone_p1.make_move(pos=[4,2], dest=[4,4])
        self.assertTrue(clone_board.piece_exists([4,4]))
        self.assertFalse(clone_board.piece_exists([4,2]))
        self.assertEqual(clone_board.get_piece([4,4]).rank, 'PAWN')

        self.assertTrue(board.piece_exists([4,2]))
        self.assertFalse(board.piece_exists([4,4]))
        self.assertEqual(board.get_piece([4,2]).rank, 'PAWN')

    def test_original_move_cannot_affect_clone(self):
        '''
        Tests that a move in the original game doesn't affect the clone game.
        '''
        game = Game()
        board = game.board
        self.assertTrue(game.turn == 'WHITE')
        game.clone_game()
        clone_game = game.game_clone
        assert(clone_game != None)
        clone_board = clone_game.board
        p1 = game.p1
        p1.make_move(pos=[4,2], dest=[4,4])
        self.assertTrue(board.piece_exists([4,4]))
        self.assertFalse(board.piece_exists([4,2]))
        self.assertEqual(board.get_piece([4,4]).rank, 'PAWN')

        self.assertTrue(clone_board.piece_exists([4,2]))
        self.assertFalse(clone_board.piece_exists([4,4]))
        self.assertEqual(clone_board.get_piece([4,2]).rank, 'PAWN')

    def test_clone_capture_cannot_affect_original(self):
        '''
        Tests that a capture in a cloned game doesn't affect the main game's pieces.
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
        clone_p1.make_move(pos=[1,1], dest=[1,8])
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


    def test_original_capture_cannot_affect_clone(self):
        '''
        Tests that a capture in an original game doesn't affect the cloned game's pieces.
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
        p1.make_move(pos=[1,1], dest=[1,8])
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

    def test_move_puts_player_in_check(self):
        '''
        Tests move_puts_player_in_check.
        '''
        game = Game()
        self.assertFalse(move_puts_player_in_check(game, [4,2], [4,4])) # white open
        self.assertFalse(move_puts_player_in_check(game, [4,7], [4,5])) # black open

        white_pieces = ['K-E1', 'Q-E2']
        black_pieces = ['K-E8', 'Q-E7']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        update_players_check(game)
        self.assertTrue(move_puts_player_in_check(game, [5,2], [6,2]))
        self.assertFalse(move_puts_player_in_check(game, [5,2], [5,3]))
        self.assertFalse(move_puts_player_in_check(game, [5,2], [5,7]))
        self.assertTrue(move_puts_player_in_check(game, [5,7], [4,7]))
        self.assertFalse(move_puts_player_in_check(game, [5,7], [5,6]))
        self.assertFalse(move_puts_player_in_check(game, [5,7], [5,2]))

    def test_move_locks_opponent(self):
        '''
        Tests move_locks_opponent under various scenarios.
        '''
        game = Game() # vanilla false positive tests
        p1 = game.p1
        all_p1_moves = p1.get_all_player_move_options()
        for move in all_p1_moves:
            self.assertFalse(move_locks_opponent(game, move[0], move[1])) # white open

        white_pieces = ['K-E1', 'R-D2', 'Q-E2', 'R-G2']
        black_pieces = ['K-E8']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)
        p1 = game.p1
        p2 = game.p2
        update_players_check(game)
        self.assertTrue(p2.in_check)
        self.assertFalse(p1.in_check)
        self.assertTrue(move_locks_opponent(game, [7,2], [6,2]))
        self.assertFalse(move_locks_opponent(game, [7,2], [7,8]))

    def test_clone_game_and_get_game_state_based_on_move(self):
        '''
        Tests that clone_game_and_get_game_state_based_on_move works correctly.
        '''
        game = Game()
        p1 = game.p1
        p2 = game.p2
        board = game.board
        (cloned_game, 
         cloned_player, 
         cloned_opponent, 
         cloned_board) = clone_game_and_get_game_state_based_on_move(game, [4,2], [4,4]) # do white D4, by cloned_player
        self.assertIsNotNone(game.game_clone)
        self.assertEqual(type(game.game_clone), Game)
        # check that we indeed return the cloned game
        self.assertEqual(game.game_clone, cloned_game)
        # check cloned_board reflects this move's changes
        self.assertIsNone(cloned_board.get_piece([4,2]))
        self.assertTrue(cloned_board.get_piece([4,4]).rank, 'PAWN')
        self.assertTrue(cloned_board.get_piece([4,4]).color, 'WHITE')
        # check cloned_player reflects this move's changes:
        self.assertEqual(cloned_player.pieces['P-D2'].pos, [4,4])
        # check original board didn't make this move
        self.assertTrue(board.piece_exists([4,2]))
        self.assertFalse(board.piece_exists([4,4]))
        # check that original p1 did not use this clone move:
        self.assertEqual(p1.pieces['P-D2'].pos, [4,2])
        # testing clones again
        cloned_opponent.make_move([4,7], [4,5])
        # test that opponent clone's move is reflected on board
        self.assertIsNone(cloned_board.get_piece([4,7]))
        self.assertTrue(cloned_board.get_piece([4,5]).rank, 'PAWN')
        self.assertTrue(cloned_board.get_piece([4,4]).color, 'BLACK')
        # check cloned_opponent reflects this move's changes:
        self.assertEqual(cloned_opponent.pieces['P-D7'].pos, [4,5])
        # check original board didn't make this move
        self.assertTrue(board.piece_exists([4,7]))
        self.assertFalse(board.piece_exists([4,5]))
        # check that original p2 did not use this clone move:
        self.assertEqual(p2.pieces['P-D7'].pos, [4,7])

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

    def test_get_all_player_move_options(self, debug_config=None):
        '''
        Tests that get_all_player_move_options correctly works for
        all combinatorially possible piece moves given debug_config.
        Remember, this only tests movement_zone legality, not check legality.
        '''
        game = None # Exhaustive test, around 8192 options here.
        if debug_config == None:
            game = Game()
        else:
            game = Game(debug_config)
        p1 = game.p1
        p1_all_moves = p1.get_all_player_move_options() # [[[x_1, y_1], [x_2, y_2]],...]
        set_p1_all_moves = get_set(p1_all_moves)
        for j in range(8):
            for i in range(8):
                x1, y1 = i+1, j+1
                for k in range(8):
                    for l in range(8):
                        x2, y2 = k+1, l+1
                        proposed_move = [[x1,y1],[x2,y2]] # pos, dest
                        if get_tuple(proposed_move) in set_p1_all_moves:
                            self.assertTrue(p1.bool_move_legal(proposed_move[0], proposed_move[1]))
                        else:
                            self.assertFalse(p1.bool_move_legal(proposed_move[0], proposed_move[1]))

        p2 = game.p2
        p2_all_moves = p2.get_all_player_move_options() # [[[x_1, y_1], [x_2, y_2]],...]
        set_p2_all_moves = get_set(p2_all_moves)
        for j in range(8):
            for i in range(8):
                x1, y1 = i+1, j+1
                for k in range(8):
                    for l in range(8):
                        x2, y2 = k+1, l+1
                        proposed_move = [[x1,y1],[x2,y2]] # pos, dest
                        if get_tuple(proposed_move) in set_p2_all_moves:
                            self.assertTrue(p2.bool_move_legal(proposed_move[0], proposed_move[1]))
                        else:
                            self.assertFalse(p2.bool_move_legal(proposed_move[0], proposed_move[1]))


    def test_get_all_player_move_options_custom(self):
        '''
        Tests that get_all_player_move_options correctly works for
        many custom board configs.
        '''
        self.test_get_all_player_move_options()
        self.test_get_all_player_move_options(set_up_debug(white_pieces=['K-E1', 'Q-D1'], 
                                                                   black_pieces=['K-E8']))
        self.test_get_all_player_move_options(set_up_debug(white_pieces = ['K-E1', 'Q-E7'],
                                                                   black_pieces = ['K-E8', 'Q-E2']))
        self.test_get_all_player_move_options(set_up_debug(
        white_pieces = ['R-A1', 'N-B1', 'B-C1', 'Q-D1', 'K-E1', 'B-F1', 'N-G1', 'R-H1'],
        black_pieces = ['R-A8', 'N-B8', 'B-C8', 'Q-D8', 'K-E8', 'B-F8', 'N-G8', 'R-H8']))
        self.test_get_all_player_move_options(set_up_debug(white_pieces=['K-D4'],
        black_pieces = ['P-C3', 'P-C4', 'P-C5', 'P-D5', 'P-E5', 'P-E4', 'P-E3', 'P-D3']))
        # Fails but I don't even think it is a well posed test, given that pawns out of regular position are being used.
        #It at least suggests there's a mismatch between pawn_move_legal's logic and pawn_movement_zone logic, which
        #could cause logical errors for something like non-standard position chess.
        self.test_get_all_player_move_options(set_up_debug(white_pieces=['K-D4'],
        black_pieces = ['R-C3', 'R-C4', 'R-C5', 'R-D5', 'R-E5', 'R-E4', 'R-E3', 'R-D3']))

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
        game.make_random_move()
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
        input_commands = (['f2', 'f3']+['e7', 'e5']+['g2', 'g4']+['d8', 'h4'])
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
        game_clone = game.clone_game() # backup to get back to later,
        game.turn = 'WHITE'
        # w/o having to reconfigure game repeatedly
        self.assertTrue(p1.castle_legal('KING', p2))
        self.assertTrue(p1.castle_legal('QUEEN', p2))
        self.assertTrue(p1.castle_legal('KING', p1))
        self.assertTrue(p1.castle_legal('QUEEN', p1))
        # Now perform castling on clone:
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

        # now work on clone
        game = game_clone
        board = game.board
        p1 = game.p1
        p2 = game.p2
        game_clone = game.clone_game() # backup to get back to later,
        game.turn = 'WHITE'

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


        game = game_clone
        board = game.board
        p1 = game.p1
        p2 = game.p2
        game_clone = game.clone_game() # backup to get back to later,
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

        game = game_clone
        board = game.board
        p1 = game.p1
        p2 = game.p2
        game_clone = game.clone_game() 
        game.turn = 'BLACK'

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

    def test_en_passant_custom_config(self):
        '''
        Tests en passant on custom board config on
        cases where it should work vs cases where it should fail.
        '''
        white_pieces = ['K-A1', 'P-D2']
        black_pieces = ['K-A8', 'P-E4', 'P-C4']
        debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
        game = Game(debug)

if __name__ == '__main__':
    unittest.main()