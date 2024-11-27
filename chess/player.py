from piece import Piece
from board import Board
from misc.constants import *
from move_legal import pawn_move_legal, rook_move_legal, bishop_move_legal, knight_move_legal, queen_move_legal, king_move_legal
from helpers.state_helpers import pawn_promotion, update_moved_piece, update_players_check, update_player_pawns_leap_status
from helpers.general_helpers import check_in_bounds, algebraic_uniconverter, convert_letter_to_rank, in_between_hori_tiles, swap_colors, ordinal_direction
from helpers.game_helpers import convert_color_to_player
from movement_zone import get_movement_zone, mass_movement_zone

'''
Player who gets to make chess moves.
'''

class Player:
    def __init__(self, color: str, board: Board, game, debug=None, is_clone=False):
        '''
        debug: debugging config, for setting initial config of pieces
        is_clone: Whether created player is a clone, if so, forgos collecting of pieces
        and setting them on board, to delegate them to client.
        '''
        self.color = color
        self.pieces = {} # key is Piece name, value is Piece, its a collection of this player's pieces
        self.board = board
        if not is_clone:
            self.collect_pieces(debug=debug) 
            self.set_pieces_on_board()
        self.in_check = False # whether Player's king is in check or not. 
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


    def make_move(self, pos, dest):
        '''
        This moves a piece at pos to dest if said move is legal.
        Note, pos, dest are [8]^2 coordinates.
        Function will handle pawn promotion, and update the 'moved' parameter of
        the moved piece, if it has moved.
        '''
        legality, special_message = self.non_bool_move_legal(pos=pos, dest=dest)
        # special message is an error (ignored), blank '' (ignored), or 'EN PASSANT' command string (important)
        if legality:
            moving_piece = self.board.get_piece(pos)
            assert(moving_piece.color in BWSET)
            if special_message == 'EN PASSANT':
                assert(moving_piece.rank == 'PAWN')
                ord_dir = ordinal_direction(pos, dest)
                look = ord_dir[1] 
                assert(look in set(['E', 'W']))
                offset = 1 if look == 'E' else -1
                self.board.move_piece(pos=dest, piece=moving_piece)
                removed_pawn = self.board.remove_piece([pos[0]+offset, pos[1]])
                assert(removed_pawn != None)
                assert(removed_pawn.color in BWSET)
                assert(removed_pawn.color != moving_piece.color)
                assert(removed_pawn.rank == 'PAWN')
            else:
                self.board.move_piece(pos=dest, piece=moving_piece)
            pawn_promotion(player=self, dest=dest, piece=moving_piece)
            assert(moving_piece.pos == dest)
            update_moved_piece(piece=moving_piece)
            update_players_check(self.game)
            update_player_pawns_leap_status(self, moving_piece, pos, dest)
            self.game.turn = swap_colors(self.game.turn)
        else:
            return

    def non_bool_move_legal(self, pos, dest) -> tuple[bool, str]:
        '''
        This checks to see if moving a piece from pos to dest is legal.
        Some examples of illegal moves include out-of-bounds, out of movement zone, and other misc stuff.
        Note, moving into check is illegal but is not handled by this method.
        Note, pos, dest are [8]^2 coordinates.
        Returns True, '' or False, error message string.
        Note: NOT to be used as a boolean value, the non_bool prefix specifies this, so as to not mistake
        move_legal as a boolean value.
        '''

        misc_check = self.misc_checks(pos=pos, dest=dest) # helper
        if not misc_check[0]:
            return misc_check
        
        cur_piece = self.board.get_piece(pos=pos)
        assert(cur_piece.pos == pos)
        rank = cur_piece.rank

        if rank == None:
            raise Exception("Piece needs to have rank")
        
        # Note no teamkill is delegated by X_move_legal functions, to have error messages make sense
        
        if rank == 'PAWN':
            return pawn_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'ROOK':
            return rook_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'BISHOP':
            return bishop_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KNIGHT':
            return knight_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'QUEEN':
            return queen_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KING':
            return king_move_legal(player=self, pos=pos, dest=dest)
        else:
            return False, 'Rank of piece at position ' +str(algebraic_uniconverter(pos))+ ' does not match any of the 6 classes.'
    

    def misc_checks(self, pos, dest) -> tuple[bool, str]:
        '''
        Helper for move_legal.
        '''

        if not check_in_bounds(pos) or not check_in_bounds(dest):
            return False, 'Given coordinates '+str(pos)+' is out of bounds' # unreachable?
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
    

    def bool_move_legal(self, pos, dest) -> bool:
        '''
        Returns boolean value of move_legal's tuple output.
        Mainly for use when testing truth values of move legality.
        '''
        return self.non_bool_move_legal(pos=pos, dest=dest)[0]
    
    def clone_player(self, board: Board, clone_game):
        '''
        Returns a deep copy clone of this player, including its pieces and board state.
        Required that both players have their kings.
        '''
        clone = Player(color=self.color, board=board, game=clone_game, is_clone=True)
        clone.pieces = self.clone_player_pieces(clone_player=clone)
        clone.set_pieces_on_board() # updates board param for clone, which is also board param for higher up Game.
        clone.in_check = self.in_check
        clone.king = clone.get_king()
        assert(clone.king != None)
        assert(clone.king.rank == 'KING')
        return clone
    
    def clone_player_pieces(self, clone_player):
        '''
        Returns a deep copy clone of the collection of pieces for this (non-clone) player.
        Each cloned piece is a deep copy of the original piece.
        The map uses the same keys as the original player.
        '''
        cloned_collection = {}
        for piece in self.pieces.values():
            clone_piece = piece.clone_piece(clone_player)
            cloned_collection[clone_piece.name] = clone_piece
        return cloned_collection
    
    def get_all_player_move_options(self):
        '''
        Given this Player, returns the list of all legal moves
        said player can make with its pieces, where legal moves are represented by
        [[x_0, y_0], [x_1, y_1]] objects, which refer to a legal move 
        x_0, y_0 -> x_1, y_1
        '''
        all_player_moves = []

        for piece in self.pieces.values(): # opponent piece
            piece_pos_arr = piece.pos # recall this is [x, y] in [1-8, 1-8]
            piece_movement_zone = get_movement_zone(board=self.board, piece=piece) # recall this is set of ordered pair tuples.
            for piece_dest in piece_movement_zone:
                piece_dest_arr = list(piece_dest) # this converts dest into [x, y]
                if (not self.bool_move_legal(piece_pos_arr, piece_dest_arr)):
                    '''
                    # Reenable for debugging purposes
                    print(self.board)
                    print('Pos: '+str(piece_pos_arr)+' and dest: '+str(piece_dest_arr))
                    '''
                    assert(self.bool_move_legal(piece_pos_arr, piece_dest_arr)) # type: ignore TODO how do they know its always true?
                all_player_moves.append([piece_pos_arr, piece_dest_arr])

        return all_player_moves
    

    def castle_legal(self, side, opponent) -> tuple[bool, str]:
        '''
        Returns boolean value, error message on if castle on king/queen's side for this player
        is legal.
        side: 'KING' or 'QUEEN'
        opponent: Player that opposes current player.

        Right now doesn't work outside of standard position chess.
        Thus, its required for this method that all pieces are in their standard positions, 
        and espeicially the case that Rooks go by their key code names (eg R-A1, R-H1 for WHITE).
        Also required that KING exists for this player.
        '''
        assert(side in ['KING', 'QUEEN'])
        assert(self.king != None)
        if self.king.moved:
            return False, 'Cannot castle as KING has already moved!'
        rook_code = 'R-A' if side == 'QUEEN' else 'R-H'
        rook_code = rook_code + str(self.king.pos[1])
        if rook_code not in self.pieces:
            return False, 'Cannot castle on '+str(side)+'-side as this side\'s ROOK does not exist!'
        rook = self.pieces[rook_code]
        assert(rook != None)
        if rook.moved:
            return False, 'Cannot castle here as the '+str(side)+'-side ROOK has already moved!'
        assert(self.king.pos[1] == rook.pos[1]) # must hold for standard position chess where king, rook haven't moved
        in_between_tiles = in_between_hori_tiles(pos_1=self.king.pos, pos_2=rook.pos) # exclude king, rook endpoints
        # ^ is [[x, y],...]
        for tile in in_between_tiles:
            if self.board.piece_exists(tile):
                return False, 'Cannot castle on '+str(side)+'-side as piece(s) exist between your KING and ROOK!'
        if self.in_check:
            return False, 'Cannot castle when your KING is in check!'
        
        enemy_movement_zone = mass_movement_zone(self.board, opponent) # enemy mass movement zone, recall, it's set of (x, y)
        unit_offset = 1 if side == 'KING' else -1
        tile_to_land_on = [self.king.pos[0]+2*unit_offset, self.king.pos[1]] # KING would land on it from castling
        if tuple(tile_to_land_on) in enemy_movement_zone:
            return False, ('Cannot castle on '+str(side)+'-side as you would be landing on tile \n'
                           +str(tile_to_land_on)+', which is in attack by an enemy piece, and thus put yourself in check!')
        tile_to_cross_over = [self.king.pos[0]+unit_offset, self.king.pos[1]]
        if tuple(tile_to_cross_over) in enemy_movement_zone:
            return False, ('Cannot castle on '+str(side)+'-side as you would be crossing over tile \n'
                           +str(tile_to_cross_over)+', which is in attack by an enemy piece!')
        
        # Now castling is probably legal
        
        return True, ''
    

    def castle(self, side, opponent):
        '''
        This makes the player perform a castle on KING/QUEEN side,
        if castling on that side is legal.
        This function will update the 'moved' parameter of
        the moved KING and ROOK, if castling is performed.
        side: 'KING' or 'QUEEN'
        opponent: Player that opposes current player.
        '''
        assert(side in ['KING', 'QUEEN'])
        legality, _ = self.castle_legal(side, opponent)
        if legality:

            # move KING first
            king = self.king
            assert(king != None)
            base_row = king.pos[1] # generally 1 if player is WHITE, 8 if BLACK
            unit_offset = 1 if side == 'KING' else -1
            tile_to_land_on = [king.pos[0]+2*unit_offset, base_row] # KING moves two units in 'side' dir
            crossed_tile = [king.pos[0]+unit_offset, base_row] # Tile that KING will cross, 
                                                            # must set this before king moves
            self.board.move_piece(pos=tile_to_land_on, piece=king)
            update_moved_piece(piece=king)
            # FIXME ^ Also maybe too coupled but always executed only outside smell

            # Next move ROOK to the tile that KING crossed over.
            rook_code = 'R-A' if side == 'QUEEN' else 'R-H'
            rook_code = rook_code + str(base_row)
            # this rook on 'side' must exist as legality is True
            rook = self.pieces[rook_code]
            self.board.move_piece(pos=crossed_tile, piece=rook)
            update_moved_piece(piece=rook)
            update_players_check(self.game)
            update_player_pawns_leap_status(self, castled=True)
            self.game.turn = swap_colors(self.game.turn)
        else:
            return
