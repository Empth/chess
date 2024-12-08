from piece import Piece
from board import Board
from turn import Turn
from misc.constants import *
from move_legal import pawn_move_legal, rook_move_legal, bishop_move_legal, knight_move_legal, queen_move_legal, king_move_legal
from helpers.state_helpers import pawn_promotion, update_moved_piece, update_players_check, update_player_pawns_leap_status
from helpers.general_helpers import (check_in_bounds, algebraic_uniconverter, convert_letter_to_rank, in_between_hori_tiles, swap_colors, 
ordinal_direction)
from helpers.game_helpers import convert_color_to_player, get_opponent
from movement_zone import get_movement_zone, mass_movement_zone

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

    def attempt_action(self, pos:list|None=None, dest:list|None=None, castle_side:str|None=None) -> bool:
        '''
        Wrapper for attempt_move() or attempt_castle().
        pos: [x, y] in [8]^2. A Player piece must exist here. O/W None for castle.
        dest: [x, y] in [8]^2. O/W None for castle.
        castle_side: 'KING', 'QUEEN', or None for make_move
        Either castle_side or pos, dest must be given.
        Returns: success status of attempted move.
        '''
        assert(castle_side == None or castle_side in KQSET)
        assert(castle_side != None or (pos != None and dest != None))
        assert(not (castle_side != None and (pos != None or dest != None)))

        if castle_side != None:
            return self.attempt_castle(castle_side)
        else:
            return self.attempt_move(pos, dest)
        
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
            move_pseudolegal = self.move_pseudolegal(pos, dest)
        
        if move_pseudolegal:
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
        Modifies: Board, Game state if returning True. Otherwise 
        no modifications if returning False.
        Returns: Success status of attempted move.
        '''
        assert(side in KQSET)
        opponent = get_opponent(self.game, self)
        if not castle_legal_assumption:
            castle_legal = self.castle_legal(side, opponent)

        if castle_legal:
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
            
        return True, 'Cannot detect any issues with prelim checks'
    
    
    def get_all_player_move_options(self):
        '''
        TODO options are pseudolegal not all move options
        Given this Player, returns the list of all legal moves
        said player can make with its pieces, where legal moves are represented by
        [[x_0, y_0], [x_1, y_1]] objects, which refer to a legal move 
        x_0, y_0 -> x_1, y_1
        '''
        return []
    

    def update_state(self, moved_piece_arr: list, former_pos=None, dest=None):
        '''
        Player updates game state, typically at end of every turn, to prepare for next turn.
        Updates moved param of piece, both player's check status, pawn leap status, pawn
        promotion rank, and swap game turn color for next turn. 
        moved_piece_arr: list of pieces that this player moved, must be of len [1, 2]
        '''
        assert(1<=len(moved_piece_arr)<=2)

        for moved_piece in moved_piece_arr:
            if moved_piece.rank == PAWN:
                pawn_promotion(self, dest, moved_piece)
                update_player_pawns_leap_status(self, moved_piece, former_pos, dest)
            update_moved_piece(moved_piece)
        
        update_players_check(self.game)
        self.game.turn = swap_colors(self.game.turn)

    
        