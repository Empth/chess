from .general_helpers import get_piece_visual
from movement_zone import get_movement_zone, mass_movement_zone # os.getcwd is Desktop\Chess  ...
from .game_helpers import convert_color_to_player

'''
For things like pawn promotion status, piece has moved, king in check, move places player in check, etc
'''

def pawn_promotion(player, dest, piece):
    '''Given a piece that moved to dest, checks whether it is a pawn that reached its "end",
    in which case we promote it to QUEEN. Otherwise, does nothing.'''
    # TODO Implement underpromotion to lower than queen 
    end = 8 if player.color == 'WHITE' else 1
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
    assert(player.color in ['WHITE', 'BLACK'] and opponent.color in ['WHITE', 'BLACK'])
    assert(player.color != opponent.color)
    #print(player.pieces.keys())
    #print(opponent.pieces.keys())
    player_king_code = 'K-E1' if player.color == 'WHITE' else 'K-E8'
    player_king_position = player.pieces[player_king_code].pos
    return (tuple(player_king_position) in mass_movement_zone(player.board, opponent))

def move_puts_player_in_check(game, pos, dest) -> bool:
    '''
    For player with piece on pos, returns boolean on whether its own pos->dest
    (must be movement zone legal) move puts its king into check.
    Updates game's game_clone state with the hypothetical game.
    '''
    _, cur_player_clone, opponent_clone, _ = clone_game_and_get_game_state_based_on_move(game, pos, dest)
    return player_in_check(player=cur_player_clone, opponent=opponent_clone)

def move_locks_opponent(game, pos, dest) -> bool:
    '''
    Returns True if the pos->dest move made by a player locks its opponent into a
    position where any subsequent move it takes leads to its king being captured. False otherwise.
    Modifies game's game_clone state with all of the hypothetical states.
    '''
    # These cloned states have made the pos->dest move by cur_player
    (game_clone, _, 
     opponent_clone, board_clone) = clone_game_and_get_game_state_based_on_move(game, pos, dest)
    for op_piece in opponent_clone.pieces.values(): # opponent piece
        arr_op_piece_pos = op_piece.pos # recall this is [x, y] in [1-8, 1-8]
        op_piece_movement_zone = get_movement_zone(board=board_clone, piece=op_piece) # recall this is set of ordered pair tuples.
        for op_piece_dest in op_piece_movement_zone:
            arr_op_piece_dest = list(op_piece_dest) # this converts dest into [x, y]
            assert(opponent_clone.move_legal(arr_op_piece_pos, arr_op_piece_dest))
            if not move_puts_player_in_check(game_clone, arr_op_piece_pos, arr_op_piece_dest): 
                # ^ this method puts a clone inside of the clone, so it doesn't modify clone's state.
                return False
    return True

def clone_game_and_get_game_state_based_on_move(game, pos, dest):
    '''
    Given a movement zone legal pos->dest move by some player, makes a clone of the board state after doing that pos->dest
    move. Updates this game's game_clone param with that cloned game which made the pos->dest move. 
    
    Returns (in order): the cloned Game, the cloned Player which made the pos->dest move,
    the opposing cloned opponent Player, and the cloned Board.
    '''
    # TODO variable names for 'BLACK', 'WHITE' which is used too often...
    game.clone_game()
    game_clone = game.game_clone
    board_clone = game_clone.board
    cur_player_color = board_clone.get_piece(pos=pos).color
    opponent_color = 'WHITE' if cur_player_color == 'BLACK' else 'BLACK'
    assert(game_clone.p1.color != game_clone.p2.color)
    assert(cur_player_color in ['WHITE', 'BLACK'] and opponent_color in ['WHITE', 'BLACK'])
    assert(cur_player_color != opponent_color)
    cur_player_clone = convert_color_to_player(game=game_clone, color=cur_player_color)
    opponent_clone = convert_color_to_player(game=game_clone, color=opponent_color)
    assert(cur_player_clone.color == cur_player_color and opponent_clone.color == opponent_color)
    assert(cur_player_clone.move_legal(pos, dest))
    cur_player_clone.make_move(pos, dest)

    return game_clone, cur_player_clone, opponent_clone, board_clone




