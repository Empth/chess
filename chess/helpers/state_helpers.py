from .general_helpers import get_piece_visual, swap_colors
from movement_zone import get_movement_zone, mass_movement_zone # os.getcwd is Desktop\Chess  ...
from .game_helpers import convert_color_to_player
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
    #print(player.pieces.keys())
    #print(opponent.pieces.keys())
    player_king = player.king
    if player_king == None:
        return False # There is no king, hence there is no check condition. Mainly for tests with debug state.
    return (tuple(player_king.pos) in mass_movement_zone(player.board, opponent))

def move_puts_player_in_check(game, pos, dest) -> bool:
    '''
    For player with piece on pos, returns boolean on whether its own pos->dest
    (must be movement zone legal) move will have its king in check or not.
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
     opponent_clone, _) = clone_game_and_get_game_state_based_on_move(game, pos, dest)
    for legal_move in opponent_clone.get_all_player_move_options(): # Note legal_move is [[x_0, y_0], [x_1, y_1]]
        op_pos, op_dest = legal_move[0], legal_move[1]
        assert(opponent_clone.move_legal(op_pos, op_dest))
        if not move_puts_player_in_check(game_clone, op_pos, op_dest): 
            # ^ this method puts a clone inside of the clone, so it doesn't modify this clone's state.
            return False
    return True

def clone_game_and_get_game_state_based_on_move(game, pos, dest):
    '''
    Given a movement zone legal pos->dest move by some player, makes a clone of the board state after doing that pos->dest
    move. Updates this game's game_clone param with that cloned game which made the pos->dest move. 
    
    Returns (in order): the cloned Game, the cloned Player which made the pos->dest move,
    the opposing cloned opponent Player, and the cloned Board.
    '''
    game.clone_game()
    game_clone = game.game_clone
    board_clone = game_clone.board
    cur_player_color = board_clone.get_piece(pos=pos).color
    opponent_color = swap_colors(cur_player_color)
    assert(game_clone.p1.color != game_clone.p2.color)
    assert(cur_player_color in BWSET and opponent_color in BWSET)
    assert(cur_player_color != opponent_color)
    cur_player_clone = convert_color_to_player(game=game_clone, color=cur_player_color)
    opponent_clone = convert_color_to_player(game=game_clone, color=opponent_color)
    assert(cur_player_clone.color == cur_player_color and opponent_clone.color == opponent_color)
    assert(cur_player_clone.move_legal(pos, dest))
    cur_player_clone.make_move(pos, dest)
    update_players_check(game_clone) 
    # FIXME ^ smells because we have to update player's check outside of make_move() being called every time, which
    # will lead to bugs. Refactor this please, maybe the fix is having Players refer to game..., due to make_move()
    # being called from Player, this has its own can of worms however...

    return game_clone, cur_player_clone, opponent_clone, board_clone


def castle_locks_opponent(game, player, opponent, side) -> bool:
    '''
    Returns True if the castling move made by a player locks its opponent into a
    position where any subsequent move it takes leads to its king being captured. False otherwise.
    Modifies game's game_clone state with all of the hypothetical states.
    side: 'QUEEN' or 'KING'
    '''
    assert(side in ['KING', 'QUEEN'])
    (game_clone, _, 
     opponent_clone, _) = clone_game_and_get_game_state_based_on_castle(game, player, side)
    for legal_move in opponent_clone.get_all_player_move_options(): # Note legal_move is [[x_0, y_0], [x_1, y_1]]
        op_pos, op_dest = legal_move[0], legal_move[1]
        assert(opponent_clone.move_legal(op_pos, op_dest))
        if not move_puts_player_in_check(game_clone, op_pos, op_dest): 
            # ^ this method puts a clone inside of the clone, so it doesn't modify this clone's state.
            return False
    return True


def clone_game_and_get_game_state_based_on_castle(game, player, side):
    '''
    Like clone_game_and_get_game_state_based_on_move but we do a castle instead.
    '''
    assert(side in ['KING', 'QUEEN'])
    game.clone_game()
    game_clone = game.game_clone
    board_clone = game_clone.board
    cur_player_color = player.color
    opponent_color = swap_colors(cur_player_color)
    assert(game_clone.p1.color != game_clone.p2.color)
    assert(cur_player_color in BWSET and opponent_color in BWSET)
    assert(cur_player_color != opponent_color)
    cur_player_clone = convert_color_to_player(game=game_clone, color=cur_player_color)
    opponent_clone = convert_color_to_player(game=game_clone, color=opponent_color)
    assert(cur_player_clone.color == cur_player_color and opponent_clone.color == opponent_color)
    assert(cur_player_clone.castle_legal(side, opponent_clone))
    cur_player_clone.castle(side, opponent_clone)
    update_players_check(game_clone) 
    # FIXME ^ smells because we have to update player's check outside of make_move() being called every time, which
    # will lead to bugs. Refactor this please, maybe the fix is having Players refer to game..., due to make_move()
    # being called from Player, this has its own can of worms however...

    return game_clone, cur_player_clone, opponent_clone, board_clone




