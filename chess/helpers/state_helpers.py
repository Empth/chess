from .general_helpers import get_piece_visual, swap_colors
from movement_zone import get_movement_zone, mass_movement_zone # os.getcwd is Desktop\Chess  ...
from .game_helpers import convert_color_to_player
from .legality_helpers import get_ordinal_collision, get_cardinal_collision, piece_exists_on_pos_offset
from misc.constants import *

'''
For things like pawn promotion status, piece has moved, king in check, move places player in check, etc
'''

def pawn_promotion(player, dest, piece):
    '''Given a piece that moved to dest, checks whether it is a pawn that reached its "end",
    in which case we promote it to QUEEN. Otherwise, does nothing.'''
    # TODO Implement underpromotion to lower than queen 
    end = 8 if player.color == WHITE else 1
    if piece.rank == 'PAWN' and dest[1] == end:
        piece.rank = 'QUEEN'
        piece.visual = get_piece_visual(rank=piece.rank, color=piece.color)

def update_moved_piece(piece):
    '''
    If a piece has never moved, and has made a move, this function is called to update the piece's
    moved param to True.
    '''
    if not piece.moved:
        piece.moved = True

def update_players_check(game):
    '''
    Given a game, updates the check status of p1, p2
    '''
    game.p1.in_check = player_in_check(game.p1, game.p2)
    game.p2.in_check = player_in_check(game.p2, game.p1)

def player_in_check(player, opponent) -> bool:
    '''
    For current player, returns whether they are in check by given opponent.
    '''
    # NOTE King code doesn't work with debug configs...
    assert(player.color in BWSET and opponent.color in BWSET)
    assert(player.color != opponent.color)
    player_king = player.king
    if player_king == None:
        return False # There is no king, hence there is no check condition. Mainly for tests with debug state.
    king_pos = player_king.pos
    board = player.board
    opponent_color = swap_colors(player.color)
    
    # diagonal ray check
    for ordinal in set(['NE', 'SE', 'SW', 'NW']):
        collision_pos = get_ordinal_collision(board, king_pos, ordinal)
        if collision_pos != None:
            col_piece = board.get_piece(collision_pos)
            if col_piece.color != player.color and col_piece.rank in ['BISHOP', 'QUEEN']:
                return True
    
    # straight ray check
    for cardinal in set(['N', 'E', 'S', 'W']):
        collision_pos = get_cardinal_collision(board, king_pos, cardinal)
        if collision_pos != None:
            col_piece = board.get_piece(collision_pos)
            if col_piece.color != player.color and col_piece.rank in ['ROOK', 'QUEEN']:
                return True

    y_offset = 1 if player.color == WHITE else -1 # absolute offset of enemy pawn when it can cap king

    if piece_exists_on_pos_offset(board, king_pos, 
                                  offsets=[[1, y_offset], [-1, y_offset]], 
                                  finding_piece=['PAWN', opponent_color]):
        return True # Opponent PAWN checks
    
    if piece_exists_on_pos_offset(board, king_pos, 
                                  offsets=([[1, 2], [2, 1], [-1, 2], [2, -1],
                                            [1, -2], [-2, 1], [-1, -2], [-2, -1]]), 
                                  finding_piece=['KNIGHT', opponent_color]):
        return True # Opponent KNIGHT checks
    
    if piece_exists_on_pos_offset(board, king_pos, 
                                  offsets=([[1, 1], [1, -1], [-1, 1], [-1, -1], 
                                            [1, 0], [-1, 0], [0, 1], [0, -1]]), 
                                  finding_piece=['KING', opponent_color]):
        return True # Opponent KING checks
    
    return False # Player KING is out of check


def update_player_pawns_leap_status(player, moved_piece=None, prev_pos=None, cur_pos=None, castled=False):
    '''
    Function that goes through the player's pieces, and updates the
    pieces' pawn_two_leap_on_prev_turn param, both activating and deactivating.
    Should be used after make_move() or castle() type methods.
    player: Player
    moved_piece: Piece that was moved from make_move(). Must not be None if player hasn't castled.
    prev_pos: previous position of moved_piece. Must not be None if player hasn't castled.
    cur_pos: current position of moved_piece. Must not be None if player hasn't castled.
    castled: Whether player's move was castle or a traditional move.
    '''
    # FIXME Inefficient?
        
    for piece in player.pieces.values():
        # global reset first
        piece.pawn_two_leap_on_prev_turn = False

    if not castled: # ie traditional move used
        assert(moved_piece != None)
        assert(prev_pos != None)
        assert(cur_pos != None)
        # find a two leaped pawn if it exists, set its param to True.
        if (moved_piece.rank == 'PAWN' and abs(prev_pos[1] - cur_pos[1]) == 2
            and prev_pos[0] == cur_pos[0]):
            player.pieces[moved_piece.name].pawn_two_leap_on_prev_turn = True


def undo_pawn_promotion(piece):
    '''
    Method takes promoted piece, and reverts it back to pawn status.
    '''
    piece.rank = PAWN
    piece.visual = get_piece_visual(rank=piece.rank, color=piece.color)
