from misc.constants import *
from piece import Piece

class Turn:
    '''
    A class to log the previous turn's action and state.
    '''
    def __init__(self):
        self.move_type: str # 'CASTLE' or 'MOVE'
        self.moved_piece: Piece | None = None # None for castle
        self.moved_piece_pos: list | None = None # None for castle
        self.moved_piece_dest: list | None = None # None for castle
        self.captured_piece: Piece | None = None # None for castle or no captured piece
        self.captured_piece_pos: list | None # None for castle or no captured piece
        self.castle_side: str | None = None # None for move
        self.castle_king_code: str | None = None # None for move, usually 'K-EY' for castle
        self.castle_rook_code: str | None = None # None for move, usually 'R-XY' for castle
        self.pawn_promoted: bool = False # For PAWN promotion status
        self.pieces_first_move: bool # Overloaded for both castle, move
        self.code_of_piece_that_two_leaped: str | None # PAWN only, code for PAWN that 2-leaped on this turn eg 'P-A2'
        self.turn_color: str # BLACK or WHITE turn color on start of this turn
        self.prev_players_check: list # Size 2 array of check status of WHITE, BLACK players resp on start of this turn
        self.is_pseudomove: bool # TODO unecessary?

    
    def log_castle(self, castle_side: str, king_code: str, rook_code: str,
                   turn_color: str, prev_players_check: list):
        '''
        Logs status of a castling move.
        '''
        assert(castle_side in KQSET)
        assert(len(king_code) == len(rook_code) == 4)
        assert(king_code[0] == 'K')
        assert(rook_code[0] == 'R')
        assert(turn_color in BWSET)
        assert(len(prev_players_check)==2)

        self.move_type = CASTLE
        self.castle_side = castle_side
        self.castle_king_code = king_code
        self.castle_rook_code = rook_code
        self.pieces_first_move = True # It must be for castling to work.
        self.piece_two_leaped = False # Not moving PAWN
        self.turn_color = turn_color
        self.prev_players_check = prev_players_check # For WHITE, BLACK player resp
        self.is_pseudomove = False


    def log_move(self, moved_piece: Piece, moved_piece_pos: list, moved_piece_dest: list, pawn_promoted: bool, piece_first_move: bool, 
                 piece_two_leaped: bool, turn_color:str, prev_players_check: list, is_pseudomove: bool, 
                 captured_piece: Piece|None = None, captured_piece_pos: list|None = None):
        '''
        Logs status of a tile move.
        '''
        assert(turn_color in BWSET)
        assert(len(prev_players_check)==2)
        assert((type(captured_piece) == type(captured_piece_pos) == None) 
               or (type(captured_piece) != None and type(captured_piece_pos) != None))
        
        self.move_type = MOVE
        self.moved_piece = moved_piece
        self.moved_piece_pos = moved_piece_pos
        self.moved_piece_dest = moved_piece_dest
        self.captured_piece = captured_piece
        self.captured_piece_pos = captured_piece_pos
        self.pawn_promoted = pawn_promoted
        self.pieces_first_move = piece_first_move
        self.code_of_piece_that_two_leaped = moved_piece.name if piece_two_leaped else None
        self.turn_color = turn_color
        self.prev_players_check = prev_players_check
        self.is_pseudomove = is_pseudomove



