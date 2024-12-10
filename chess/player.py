from piece import Piece
from board import Board
from turn import Turn
from misc.constants import *
from helpers.state_helpers import pawn_promotion, update_moved_piece, update_player_check, update_player_pawns_leap_status
from helpers.general_helpers import (check_in_bounds, algebraic_uniconverter, convert_letter_to_rank, in_between_hori_tiles, swap_colors, 
ordinal_direction)
from helpers.game_helpers import convert_color_to_player, get_opponent
from movement_zone import get_movement_zone, mass_movement_zone
from minimax import minimax
import random

'''
Player who gets to make chess moves.
'''

class Player:
    def __init__(self, color: str, board: Board, game, debug=None):
        '''
        debug: debugging config, for setting initial config of pieces
        is_clone: Whether created player is a clone, if so, forgos collecting of pieces
        and setting them on board, to delegate them to client.
        '''
        self.color = color
        self.pieces = {} # key is Piece name, value is Piece, its a collection of this player's pieces
        self.board = board
        self.collect_pieces(debug=debug) 
        self.set_pieces_on_board()
        self.in_check = False # whether Player's king is in check or not. # FIXME Player might be in check based on debug config
        self.king = self.get_king() # points towards a player's singular king object, or None if it doesn't exist on player init.
        self.game = game

        
    def collect_pieces(self, debug=None):
        '''
        Builds piece collection and their positions for this player.
        '''
        
        if debug == None:
            assert(self.color in BWSET)
            main_row = ['ROOK', 'KNIGHT', 'BISHOP', 'QUEEN', 'KING', 'BISHOP', 'KNIGHT', 'ROOK']
            main_row_pos = 1 if self.color == WHITE else 8
            pawn_row_pos = 2 if self.color == WHITE else 7
            for i in range(8):
                pawn_piece = Piece(color=self.color, rank='PAWN', pos=[i+1, pawn_row_pos], player=self)
                self.pieces[pawn_piece.name] = pawn_piece
                main_piece = Piece(color=self.color, rank=main_row[i], pos=[i+1, main_row_pos], player=self)
                self.pieces[main_piece.name] = main_piece
        elif self.color in debug.board_state:
            player_board_state = debug.board_state[self.color]
            for code in player_board_state:
                piece = Piece(color=self.color, rank=convert_letter_to_rank(code[0]), 
                              pos=algebraic_uniconverter(code[2:]), player=self)
                assert(piece.name == code) # sanity check, helped catch a knight is N bug once
                self.pieces[piece.name] = piece 


    def set_pieces_on_board(self):
        '''
        Sets this player's pieces on the board, for the start of the game.
        '''
        for piece in self.pieces.values():
            self.board.add_or_replace_piece(pos=piece.pos, piece=piece)


    def get_king(self):
        '''
        Retrieves KING piece of this player to return.
        '''
        for piece in self.pieces.values():
            if piece.rank == 'KING':
                return piece
        return None

    def attempt_action(self, turn: list|str,
                       move_pseudolegal_assumption=False) -> bool:
        '''
        Wrapper for attempt_move() or attempt_castle().
        turn: [[x_0, y_0], [x_1, y_1]] pos->dest move list, 
        or 'KING'/'QUEEN' string for castle.
        move_pseudolegal_assumption: Assumption on if we have to check pseudolegality of move or not.
        Returns: success status of attempted move.
        '''
        if type(turn) == list:
            assert(len(turn) == 2)
            assert(len(turn[0]) == len(turn[1]) == 2)
        else:
            assert(turn in KQSET)

        if type(turn) == list:
            return self.attempt_move(turn[0], turn[1], 
                                     move_pseudolegal_assumption=move_pseudolegal_assumption)
        else:
            # note pseudolegal castle == legal castle
            return self.attempt_castle(turn, 
                                       castle_legal_assumption=move_pseudolegal_assumption)
        
    def attempt_move(self, pos, dest, move_pseudolegal_assumption=False) -> bool:
        '''
        Attempts a move from pos->dest for this player.
        pos: [x, y] in [8]^2. This Player piece must exist here.
        dest: [x, y] in [8]^2.
        move_pseudolegal_assumption: Boolean on if we have outside info that
        pos->dest is pseudolegal w/o need to check pseudolegality in this function.
        Modifies: Board, Game state if returning True. Otherwise 
        no modifications if returning False.
        Returns: Success status of attempted move.
        '''
        if not self.misc_checks(pos, dest)[0]:
            return False
        
        if not move_pseudolegal_assumption:
            move_pseudolegal_assumption = self.move_pseudolegal(pos, dest)
        
        if move_pseudolegal_assumption:
            turn_color_at_turn_start = self.color
            opponent = get_opponent(self.game, self)
            player_check = self.in_check
            opponent_check = opponent.in_check
            prev_check_status = [player_check, opponent_check] if self.color == WHITE else [opponent_check, player_check]

            moved_piece = self.board.get_piece(pos)
            former_rank = moved_piece.rank
            piece_first_move = not moved_piece.moved
            captured_piece = self.make_pseudomove(pos, dest)

            assert(moved_piece.pos == dest)
            self.update_state([moved_piece], pos, dest)

            new_rank = moved_piece.rank
            pseudolegal_turn = Turn()
            pawn_promoted = (former_rank != new_rank)
            captured_piece_pos = None if captured_piece == None else captured_piece.pos
            pawn_two_leap = moved_piece.pawn_two_leap_on_prev_turn
            pseudolegal_turn.log_move(moved_piece, pos, dest, pawn_promoted, piece_first_move, 
                                    pawn_two_leap, turn_color_at_turn_start, prev_check_status, True, 
                                      captured_piece=captured_piece, 
                                      captured_piece_pos=captured_piece_pos)
            self.game.turn_log.append(pseudolegal_turn)

            if self.in_check: # illegal move
                self.game.unmake_turn(pseudomove=True)
                return False
            else:
                # move is indeed legal
                self.game.turn_log[-1].is_pseudomove = False
                return True
            
        return False # not even pseudolegal


    def move_pseudolegal(self, pos, dest):
        '''
        Returns whether pos->dest move is pseudolegal, ie pos->dest
        is a valid movement tile option for piece on pos, without regards
        for whether it takes this player into check.
        '''
        cur_piece = self.board.get_piece(pos)
        cur_piece_movement_zone = get_movement_zone(self.board, cur_piece)
        return tuple(dest) in cur_piece_movement_zone
    

    def make_pseudomove(self, pos, dest):
        '''
        Makes pseudolegal pos->dest move for player.
        Requires: pos->dest is pseudolegal.
        Modifies: Board, piece positions. Does not update other Piece, Player states.
        Note, all changes here can be possibly reverted by the caller function.
        Returns: Captured enemy piece from player. Otherwise None.
        '''
        moving_piece = self.board.get_piece(pos)
        if moving_piece.rank == PAWN:
            if abs(pos[0]-dest[0]) == abs(pos[1]-dest[1]) == 1:
                if not self.board.piece_exists(dest):
                    # This is an en passant and it is pseudolegal.
                    ord_dir = ordinal_direction(pos, dest)
                    look = ord_dir[1]
                    offset = 1 if look == 'E' else -1
                    self.board.move_piece(pos=dest, piece=moving_piece)
                    removed_pawn = self.board.remove_piece([pos[0]+offset, pos[1]])
                    return removed_pawn
                
        # Else, its a normal move
        captured_piece = self.board.move_piece(pos=dest, piece=moving_piece)
        return captured_piece
    
    
    def attempt_castle(self, side, castle_legal_assumption=False) -> bool:
        '''
        Attempts a castle on 'side' for this player.
        side: 'KING' or 'QUEEN'
        castle_legal_assumption: Boolean on if we have outside info that
        castling on this side is legal w/o need to check legality in this function.
        omit_pl_op_check: 1st, 2nd args tell whether this player, opponent (resp) 
        check updates can be ommited or not.
        Modifies: Board, Game state if returning True. Otherwise 
        no modifications if returning False.
        Returns: Success status of attempted move.
        '''
        assert(side in KQSET)
        opponent = get_opponent(self.game, self)
        if not castle_legal_assumption:
            castle_legal_assumption = self.castle_legal(side, opponent)

        if castle_legal_assumption:
            # castling guarenteed to work
            turn_color_at_turn_start = self.color
            player_check = self.in_check
            opponent_check = opponent.in_check
            prev_check_status = [player_check, opponent_check] if self.color == WHITE else [opponent_check, player_check]
            
            moved_king, moved_rook = self.castle(side)
            self.update_state([moved_king, moved_rook])
            turn = Turn()
            turn.log_castle(side, moved_king.name, moved_rook.name, turn_color_at_turn_start, prev_check_status)
            self.game.turn_log.append(turn)
            return True
        
        return False


    def castle_legal(self, side, opponent) -> bool:
        '''
        Returns whether player castling on 'side' is legal.
        '''
        assert(side in KQSET)
        assert(self.king != None)
        if self.king.moved:
            return False # 'Cannot castle as KING has already moved!'
        rook_code = 'R-A' if side == QUEEN else 'R-H'
        rook_code = rook_code + str(self.king.pos[1])
        if rook_code not in self.pieces:
            return False # 'Cannot castle on '+str(side)+'-side as this side\'s ROOK does not exist!'
        rook = self.pieces[rook_code]
        assert(rook != None)
        if rook.moved:
            return False # 'Cannot castle here as the '+str(side)+'-side ROOK has already moved!'
        assert(self.king.pos[1] == rook.pos[1]) # must hold for standard position chess where king, rook haven't moved
        in_between_tiles = in_between_hori_tiles(pos_1=self.king.pos, pos_2=rook.pos) # exclude king, rook endpoints
        # ^ is [[x, y],...]
        for tile in in_between_tiles:
            if self.board.piece_exists(tile):
                return False # 'Cannot castle on '+str(side)+'-side as piece(s) exist between your KING and ROOK!'
        if self.in_check:
            return False # 'Cannot castle when your KING is in check!'
        
        enemy_movement_zone = mass_movement_zone(self.board, opponent) # enemy mass movement zone, recall, it's set of (x, y)
        unit_offset = 1 if side == KING else -1
        tile_to_land_on = [self.king.pos[0]+2*unit_offset, self.king.pos[1]] # KING would land on it from castling
        if tuple(tile_to_land_on) in enemy_movement_zone:
            return False # ('Cannot castle on '+str(side)+'-side as you would be landing on tile \n'
                            # +str(tile_to_land_on)+', which is in attack by an enemy piece, and thus put yourself in check!')
        tile_to_cross_over = [self.king.pos[0]+unit_offset, self.king.pos[1]]
        if tuple(tile_to_cross_over) in enemy_movement_zone:
            return False # ('Cannot castle on '+str(side)+'-side as you would be crossing over tile \n'
                            # +str(tile_to_cross_over)+', which is in attack by an enemy piece!')
        
        # Now castling is legal
        
        return True
        
    
    def castle(self, side):
        '''
        Perform player castle on 'side'.
        side: 'KING' or 'QUEEN'
        Modifies: Board, piece positions.
        Requires: Player castling on this side is legal.
        Returns: Moved KING, ROOK respectively.
        '''
        assert(side in KQSET)

        # move KING first
        king = self.king
        assert(king != None)
        base_row = king.pos[1] # generally 1 if player is WHITE, 8 if BLACK
        unit_offset = 1 if side == KING else -1
        tile_to_land_on = [king.pos[0]+2*unit_offset, base_row] # KING moves two units in 'side' dir
        crossed_tile = [king.pos[0]+unit_offset, base_row] # Tile that KING will cross, 
                                                        # must set this before king moves
        self.board.move_piece(pos=tile_to_land_on, piece=king)

        # Next move ROOK to the tile that KING crossed over.
        rook_code = 'R-A' if side == QUEEN else 'R-H'
        rook_code = rook_code + str(base_row)
        # this rook on 'side' must exist as legality is True
        rook = self.pieces[rook_code]
        self.board.move_piece(pos=crossed_tile, piece=rook)

        return king, rook


    def misc_checks(self, pos, dest) -> tuple[bool, str]:
        '''
        Helper for move_legal.
        '''

        if not check_in_bounds(pos) or not check_in_bounds(dest):
            return False, 'Given coordinates '+str(pos)+' is out of bounds'
        cur_piece = self.board.get_piece(pos=pos)
        if cur_piece == None:
            return False, 'No piece at position '+str(algebraic_uniconverter(pos))+' exists'
        if type(cur_piece) != Piece:
            return False, 'Object at '+str(algebraic_uniconverter(pos))+' needs to be a piece!' # probably unreachable
        if cur_piece.color != self.color:
            return False, 'Color of selected piece doesnt match players color of '+str(self.color)+'!'
        if dest == pos:
            return False, 'Piece cannot stall as a move!'
        dest_piece = self.board.get_piece(dest)
        if dest_piece != None:
            if dest_piece.color == self.color:
                return False, 'Cannot teamkill as a move!'
            else:
                if dest_piece.rank == KING:
                    return False, 'You cannot kill the KING!'
            
        return True, 'Cannot detect any issues with prelim checks'
    

    def update_state(self, moved_piece_arr: list, former_pos=None, dest=None):
        '''
        Player updates game state, typically at end of every turn, to prepare for next turn.
        Updates moved param of piece, both player's check status, pawn leap status, pawn
        promotion rank, and swap game turn color for next turn. 
        moved_piece_arr: list of pieces that this player moved, must be of len 1-2
        If None, we compute the player check status as usual.
        '''
        n = len(moved_piece_arr)
        assert(1<=n<=2)
        castled = (n == 2)
        for moved_piece in moved_piece_arr:
            update_player_pawns_leap_status(self, moved_piece, former_pos, 
                                            dest, castled=castled)
            if moved_piece.rank == PAWN:
                pawn_promotion(self, dest, moved_piece)
            update_moved_piece(moved_piece)
        opponent = get_opponent(self.game, self)
        update_player_check(self.game, self)
        update_player_check(self.game, opponent)
        self.game.turn = swap_colors(self.game.turn)


    def get_all_legal_moves(self, shuffle=False):
        '''
        Function retrieves an array of all truly legal moves for this player 
        (ie pseudolegal and does not put/leave player in check and does not try
        to capture a king).
        A move is represented as either a 'KING'/'QUEEN' string (castle move)
        or is [[x_0, y_0], [x_1, y_1]] array from [x_0, y_0] pos to
        [x_1, y_1] dest.
        shuffle: Whether to randomize returning array or not.
        Returns: Array of moves (moves are list or str)
        '''
        all_pseudolegal_moves = self.get_all_psuedolegal_moves()
        all_truly_legal_moves = []
        for pseud_move in all_pseudolegal_moves:
            move_success = self.attempt_action(pseud_move, move_pseudolegal_assumption=True)
            if move_success:
                all_truly_legal_moves.append(pseud_move)
                assert(self.game.turn_log[-1].is_pseudomove == False)
                self.game.unmake_turn()

        opponent = get_opponent(self.game, self)
        if self.castle_legal(KING, opponent):
            all_truly_legal_moves.append(KING)
        if self.castle_legal(QUEEN, opponent):
            all_truly_legal_moves.append(QUEEN)

        if shuffle:
            random.seed(42)
            random.shuffle(all_truly_legal_moves)

        return all_truly_legal_moves
    
    def get_all_psuedolegal_moves(self):
        '''
        Function retrieves an array of all pseudolegal pos->dest moves for this 
        player. A pseudolegal move is a [[x_0, y_0], [x_1, y_1]] array, representing
        valid movement from [x_0, y_0] pos to [x_1, y_1] dest.
        Returns: Array of psedolegal moves.
        '''
        all_pseudolegal_moves = []
        for piece in self.pieces.values(): # piece
            piece_pos_arr = piece.pos # recall this is [x, y] in [8]^2
            piece_movement_zone = get_movement_zone(board=self.board, piece=piece) # recall this is set of ordered pair tuples.
            for piece_dest in piece_movement_zone:
                piece_dest_arr = list(piece_dest) # this converts dest into [x, y]
                all_pseudolegal_moves.append([piece_pos_arr, piece_dest_arr])

        return all_pseudolegal_moves
    

    def make_random_move(self) -> bool:
        '''
        Given a game state where it is PLAYER's turn, makes a 
        randomized move for PLAYER, where moves are drawn
        from set of all possible legal moves. 
        The move distribution is uniform. 
        This method will take up PLAYER's turn.
        Return: Success status of random move.
        '''
        all_legal_moves = self.get_all_legal_moves(shuffle=True)
        assert(len(all_legal_moves) > 0)
        move = all_legal_moves[0]
        move_success = self.attempt_action(move, True)
        return move_success
    

    def make_best_move(self, depth:int, shuffle=False) -> bool:
        '''
        Given a game state where it is PLAYER's turn, makes the
        best move for PLAYER, based on minimax search 'depth' levels deep.
        If PLAYER is WHITE, PLAYER is a maximizing player, otherwise PLAYER
        is a minimizing player.
        This method will take up PLAYER's turn.
        depth: Deepness of minimax search, integer greater than 0.
        shuffle: Whether to randomize order of generated legal moves.
        Return: Success status of best move.
        '''
        game = self.game
        is_maximizing_player = True if self.color == WHITE else False
        minmax_val, best_move = minimax(game, self, depth, is_maximizing_player)
        assert(best_move != None)
        move_taken = self.attempt_action(best_move)
        return move_taken




    
        