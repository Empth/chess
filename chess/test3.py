import unittest
import unittest.mock
from unittest.mock import patch

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from helpers.state_helpers import update_players_check, move_puts_player_in_check, move_locks_opponent
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
        for piece in p1.pieces.values():
            pos = piece.pos

        self.assertFalse(move_locks_opponent(game, [4,2], [4,4])) # white open

class TestEvenMorePlayerHelperFunctions(unittest.TestCase):

    def test_get_all_player_move_options_vanilla(self):
        '''
        Tests that get_all_player_move_options correctly works for
        all combinatorially possible piece moves in default board config.
        '''
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
        
        
        game = Game() # Exhaustive test first, around 2048 options here.
        p1 = game.p1
        p1_all_moves = p1.get_all_player_move_options() # [[[x_1, y_1], [x_2, y_2]],...]
        set_p1_all_moves = get_set(p1_all_moves)
        for j in range(2):
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
        for j in range(2):
            for i in range(8):
                x1, y1 = i+1, j+7
                for k in range(8):
                    for l in range(8):
                        x2, y2 = k+1, l+1
                        proposed_move = [[x1,y1],[x2,y2]] # pos, dest
                        if get_tuple(proposed_move) in set_p2_all_moves:
                            self.assertTrue(p2.bool_move_legal(proposed_move[0], proposed_move[1]))
                        else:
                            self.assertFalse(p2.bool_move_legal(proposed_move[0], proposed_move[1]))



if __name__ == '__main__':
    unittest.main()