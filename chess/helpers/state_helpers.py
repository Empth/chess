from .general_helpers import get_piece_visual, swap_colors
from movement_zone import get_movement_zone, mass_movement_zone # os.getcwd is Desktop\Chess  ...
from .game_helpers import convert_color_to_player
from .legality_helpers import get_ordinal_collision, get_cardinal_collision, piece_exists_on_pos_offset
from misc.constants import *
import random

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

def move_puts_player_in_check(game, pos, dest) -> bool:
    '''
    For player with piece on pos, returns boolean on whether its own pos->dest
    (must be movement zone legal) move will have its king in check or not.
    Updates game's game_clone state with the hypothetical game.
    '''
    cur_player = game.board.get_piece(pos).player
    assert(cur_player.bool_move_legal(pos, dest))
    _, cur_player_clone, opponent_clone, _ = clone_game_and_get_game_state_based_on_move(game, pos, dest)
    return player_in_check(player=cur_player_clone, opponent=opponent_clone)

def move_locks_opponent(game, pos=None, dest=None, castle_side_color=[]) -> bool:
    '''
    Returns True if the move (either pos->dest or castle) made by a player locks its opponent into a
    position where any subsequent move it takes leads to its king being captured. False otherwise.
    Modifies game's game_clone state with all of the hypothetical states.
    Note the pos->dest move must be movement zone legal and the castle move must generally be legal.
    pos: position [x_0, y_0]
    dest: destination [x_1, y_1]
    castle_side_color: Empty array by default. Otherwise, is size two array
    where first elt is string 'KING' or 'QUEEN' (side) and second elt is string
    'BLACK' or 'WHITE' (color initiating castle).
    '''
    game_clone, opponent_clone = None, None

    if castle_side_color == []: # its a pos->dest move
        (game_clone, _, 
        opponent_clone, _) = clone_game_and_get_game_state_based_on_move(game, pos, dest)
    else: # its a castle
        assert(len(castle_side_color) == 2)
        assert(castle_side_color[0] in ['KING', 'QUEEN'])
        assert(castle_side_color[1] in BWSET)
        (game_clone, _, 
        opponent_clone, _) = clone_game_and_get_game_state_based_on_move(game, None, None, castle_side_color)
     # ^ These cloned states have made the move by the current player
    return player_is_locked(game_clone, opponent_clone)

def clone_game_and_get_game_state_based_on_move(game, pos=None, dest=None, castle_side_color=[]):
    '''
    Given a movement zone legal pos->dest (or a legal castle) 
    move by some player, makes a clone of the board state after doing that pos->dest (or castle)
    move. Updates this game's game_clone param with that cloned game which made the pos->dest 
    (or castle) move. 

    castle_side_color: Empty array by default. Otherwise, is size two array
    where first elt is string 'KING' or 'QUEEN' (side) and second elt is string
    'BLACK' or 'WHITE' (color initiating castle).
    
    Returns (in order): the cloned Game, the cloned Player which made the move,
    the opposing cloned opponent Player, and the cloned Board.
    '''
    cur_player, cur_player_color, opponent_color = None, None, None

    if castle_side_color == []: # its a pos->dest move
        cur_player = game.board.get_piece(pos=pos).player
        cur_player_color = cur_player.color
        opponent_color = swap_colors(cur_player_color)
        assert(cur_player.bool_move_legal(pos, dest)) 
        # ^ hinges on promise that this is a pure viewer with no modifications to game's state
    else: # its a castle
        assert(len(castle_side_color) == 2)
        assert(castle_side_color[0] in ['KING', 'QUEEN'])
        assert(castle_side_color[1] in BWSET)
        side = castle_side_color[0]
        cur_player_color = castle_side_color[1]
        cur_player = convert_color_to_player(game, cur_player_color)
        opponent_color = swap_colors(cur_player_color)
        opponent = convert_color_to_player(game, opponent_color)
        assert(cur_player.bool_castle_legal(side, opponent)) 
        # ^ hinges on promise that this is a pure viewer with no modifications to game's state

    game_clone = game.clone_game()
    board_clone = game_clone.board
    assert(game_clone.p1.color != game_clone.p2.color)
    assert(cur_player_color in BWSET and opponent_color in BWSET)
    assert(cur_player_color != opponent_color)
    cur_player_clone = convert_color_to_player(game=game_clone, color=cur_player_color)
    opponent_clone = convert_color_to_player(game=game_clone, color=opponent_color)
    assert(cur_player_clone.color == cur_player_color and opponent_clone.color == opponent_color)

    if castle_side_color == []: # its a pos->dest move
        assert(cur_player_clone.bool_move_legal(pos, dest))
        cur_player_clone.make_move(pos, dest)
    else: # its a castle
        assert(cur_player_clone.bool_castle_legal(side, opponent_clone))
        cur_player_clone.castle(side, opponent_clone)

    return game_clone, cur_player_clone, opponent_clone, board_clone

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

def get_all_truly_legal_player_moves(game, player, shuffle=False):
    '''
    Given game, player, get an array of all possible player moves which
    are movement zone legal, and which does not leave said player in check (ie check legal).
    An elt of this array is [[x_0, y_0], [x_1, y_1]] if it denotes a pos->dest move, and is
    string 'QC' or 'KC' if it refers to a castle (king or queenside).
    shuffle: Whether to randomize returned array or not.

    As corollary, if an empty array returns, it means player is in checkmate or stalemate.
    '''
    movement_zone_legal_player_moves = player.get_all_player_move_options() # a bunch of these may lead into check
    truly_legal_player_moves = [] # all moves that don't keep or move player into check
    for move in movement_zone_legal_player_moves:
        if not move_puts_player_in_check(game=game, pos=move[0], dest=move[1]):
            truly_legal_player_moves.append(move)

    opponent_color = swap_colors(player.color)
    opponent = convert_color_to_player(game=game, color=opponent_color) # TODO I repeat this idiom alot, maybe it can be its own method?

    if player.bool_castle_legal('QUEEN', opponent):
        truly_legal_player_moves.append('QC')

    if player.bool_castle_legal('KING', opponent):
        truly_legal_player_moves.append('KC')

    if shuffle:
        random.shuffle(truly_legal_player_moves)

    return truly_legal_player_moves


def player_is_locked(game, player):
    '''
    Returns boolean value on if player is in checkmate or stalemate deadlocked position
    '''
    # Exploit corollary of get_all_truly_legal_player_moves, that 
    # returning [] -> checkmate/stalemate.

    return len(get_all_truly_legal_player_moves(game, player)) == 0



