import random
from player import Player
from board import Board
from debug import Debug
from helpers.general_helpers import algebraic_uniconverter, swap_colors
from helpers.game_helpers import (clear_terminal, get_error_message, get_special_command, set_error_message, set_special_command, 
                          get_color_in_check, pos_checker, dest_checker, convert_color_to_player, get_opponent)
from helpers.state_helpers import (update_players_check, move_puts_player_in_check, move_locks_opponent, 
get_all_truly_legal_player_moves, pawn_promotion, undo_pawn_promotion)
from movement_zone import get_movement_zone
from misc.constants import *
from minimax import evaluate_minimax_of_move
from turn import Turn

'''File contains The Game logic.'''

#special_command_set = set(['PAUSE', 'EXIT', 'RESELECT', 'FORFEIT', 'RANDOM', 'R', 'KC', 'QC', 'B'])
#mate_special_command_set = set(['checkmate', 'stalemate'])

class Game:
    def __init__(self, debug=None):

        '''
        debug: is Debug object for testing. None by default.
        '''

        self.board = Board()
        self.p1 = Player(color=WHITE, board=self.board, game=self, debug=debug)
        self.p2 = Player(color=BLACK, board=self.board, game=self, debug=debug)
        self.turn = self.p1.color  # 'WHITE' or 'BLACK'
        self.winner = None # Should be either 'WHITE', 'BLACK', or 'DRAW'
        self.turn_log: list[Turn] = []


    def reset(self):
        '''
        Resets game state to a blank slate.
        '''
        self.__init__()


    def render(self, render_below_board=True):
        '''
        Renders the game visuals, minus input text which must be handled outside.
        All previous rendered visuals in the terminal are erased.
        In order: Special Command shortcut list, error message slot, board, 
        (and optionally) in_check message slot, based off if render below_board is True
        render_below_board: If we render in_check below board.
        '''
        clear_terminal()
        print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT, RANDOM (or R), QC or KC (to castle), B (best move)')
        print(str(self.board))


    def start(self):
        '''
        Starts a new game, or continues an existing game if it was paused. TODO I didn't implement pause
        '''
        while self.winner == None:
            self.render()
            cur_player = convert_color_to_player(self, self.turn)
            query = input('Input move (e.g. e2e4 or kc/qc): ')
            n = len(query)
            if n not in [2, 4]:
                continue
            if n == 4:
                pos = algebraic_uniconverter(query[:2].upper())
                dest = algebraic_uniconverter(query[2:].upper())
                move_success = cur_player.attempt_action(pos, dest) # type: ignore
                if not move_success:
                    continue
            if n == 2:
                if query.upper() not in ['KC', 'QC']:
                    continue
                castle_side = KING if query.upper() == 'KC' else QUEEN
                move_success = cur_player.attempt_action(castle_side=castle_side)
                if not move_success:
                    continue


    def make_random_move(self):
        '''
        Given a game state where it is PLAYER's turn, makes a 
        randomized move for PLAYER, where moves are drawn
        from set of all possible legal moves. 
        The move distribution is uniform. 
        This method will take up PLAYER's turn.
        '''
            
    def make_best_move(self, depth=2):
        '''
        Given a game state where it is PLAYER's turn, makes the
        best move for PLAYER, based on minimax search 'depth' levels deep.
        If PLAYER is WHITE, PLAYER is a maximizing player, otherwise PLAYER
        is a minimizing player.
        This method will take up PLAYER's turn.
        depth: Deepness of minimax search, integer greater than 0.
        '''

    def unmake_turn(self, pseudomove=False):
        '''
        Undos latest turn made, recorded on end of turn_log (pseudolegal or not). 
        Handles updating turn_log w/ pop undone move from turn_log history.
        Wrapper for unmake_move, unmake_castle.
        psuedomove: Whether move is pseudolegal move, for assertions. TODO seems unnessessary?
        '''
        latest_turn = self.turn_log[-1]
        assert(latest_turn.is_pseudomove == pseudomove)
        n = len(self.turn_log)
        if n >= 2:
            for i in range(n-1):
                assert(self.turn_log[i].is_pseudomove == False)

        move_type = latest_turn.move_type
        if move_type == MOVE:
            self.unmake_move()
        elif move_type == CASTLE:
            self.unmake_castle()
        else:
            assert(False)

        self.turn_log.pop()


    def unmake_move(self):
        '''
        Undos a pos->dest move and reverts game state to start of turn before that move.
        '''
        latest_turn = self.turn_log[-1]
        assert(not self.board.piece_exists(latest_turn.moved_piece_pos))
        moved_piece_record = latest_turn.moved_piece # recorded piece
        moved_piece_board = self.board.get_piece(latest_turn.moved_piece_dest) # that piece on board
        assert(moved_piece_board == moved_piece_record)

        board = self.board
        old_pos = latest_turn.moved_piece_pos
        dest = latest_turn.moved_piece_dest
        # move moved_piece back into original position and revert its position state
        board.move_piece(old_pos, moved_piece_board)

        if latest_turn.pawn_promoted: # undo pawn promotion
            assert(moved_piece_board.rank != PAWN)
            undo_pawn_promotion(moved_piece_board)

        moved_piece_board.moved = not latest_turn.pieces_first_move # piece didn't move

        # move captured piece or none back into original position
        captured_piece = latest_turn.captured_piece
        board.add_or_replace_piece(dest, captured_piece)

        # revert 2 leap statuses
        moved_piece_board.pawn_two_leap_on_prev_turn = False # piece did not 2-leaped at start of this turn
        player = convert_color_to_player(self, latest_turn.turn_color) # get player on this turn
        opponent = get_opponent(self, player)
        if len(self.turn_log) >= 2:
            second_latest_turn = self.turn_log[-2]
            opp_two_leap_code = second_latest_turn.code_of_piece_that_two_leaped # opponent two leaper on turn before latest turn
            if opp_two_leap_code != None:
                opponent.pieces[opp_two_leap_code].pawn_two_leap_on_prev_turn = True

        # update check status
        white_check, black_check = latest_turn.prev_players_check[0], latest_turn.prev_players_check[1]
        self.p1.in_check = white_check if self.p1.color == WHITE else black_check
        self.p2.in_check = white_check if self.p2.color == WHITE else black_check

        # revert turn color
        self.turn = latest_turn.turn_color

        # revert winner status
        self.winner = None



    def unmake_castle(self):
        '''
        Undos a castle and reverts game state to start of turn before that move.
        '''

        latest_turn = self.turn_log[-1]
        board = self.board
        castle_side = latest_turn.castle_side
        player = convert_color_to_player(self, latest_turn.turn_color) # get player on this turn
        turn_color = latest_turn.turn_color
        king_code, rook_code = latest_turn.castle_king_code, latest_turn.castle_rook_code
        assert(king_code in player.pieces and rook_code in player.pieces) # as castling last turn requires these still exist
        king = player.pieces[king_code]
        rook = player.pieces[rook_code]
        y = 8 if turn_color == BLACK else 1
        rx = 8 if castle_side == KING else 1 # rook_x_pos
        # move king, rook back into their original positions
        board.move_piece([5, y], king)
        board.move_piece([rx, y], rook)
        
        # revert moved status
        king.moved = False
        rook.moved = False

        # revert 2 leap statuses
        opponent = get_opponent(self, player)
        if len(self.turn_log) >= 2:
            second_latest_turn = self.turn_log[-2]
            opp_two_leap_code = second_latest_turn.code_of_piece_that_two_leaped # opponent two leaper on turn before latest turn
            if opp_two_leap_code != None:
                opponent.pieces[opp_two_leap_code].pawn_two_leap_on_prev_turn = True

        # update check status
        white_check, black_check = latest_turn.prev_players_check[0], latest_turn.prev_players_check[1]
        self.p1.in_check = white_check if self.p1.color == WHITE else black_check
        self.p2.in_check = white_check if self.p2.color == WHITE else black_check

        # revert turn color
        self.turn = latest_turn.turn_color

        # revert winner status
        self.winner = None



            

