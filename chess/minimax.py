from helpers.state_helpers import clone_game_and_get_game_state_based_on_move
from helpers.game_helpers import convert_color_to_player
from helpers.general_helpers import swap_colors

def evaluate_minimax_after_move(game, move, cur_player, depth, is_maximizing_player=False) -> float:
    '''
    Minimax value returns the minimax value after 'move' is used
    by 'cur_player' on 'game', with search performed 'depth' levels deep.
    Assuming minimax() is always only called by an ai agent, we
    assumed the caller to be a minimizing player by default.
    Basically, this is a wrapper for minimax(), that justs passes
    in a clone of game that has cur_player make the move.

    game: Game we wish to make move on.
    move: [[x_0, y_0], [x_1, y_1]] pos->dest array OR string 'QC'/'KC' for castle.
    Said move MUST be verified as legal beforehand.
    cur_player: Player that executes move.
    depth: Number of levels deep we want to look ahead, after making 'move'.
    is_maximizing_player: bool on whether cur_player is a value maximizing or minimizing player.
    False by default, assuming cur_player is always called to be the ai agent.

    Note, depth 1 in eval_minimax really behaves like a depth 2 search 
    in the case where cur_player is free to make any move.

    Returns: minimax value of move by cur_player.
    '''
    cloned_game_after_move, cloned_player = None, None
    if type(move) == str:
        if move == 'QC':
            assert(cur_player.bool_castle_legal(side='QUEEN', 
                                           opponent=convert_color_to_player(game, 
                                            color=swap_colors(cur_player.color))))
            (cloned_game_after_move, 
             cloned_player, 
             cloned_opponent, _) = clone_game_and_get_game_state_based_on_move(game, 
                                                                                castle_side_color=['QUEEN', 
                                                                                cur_player.color])
        elif move == 'KC':
            assert(cur_player.bool_castle_legal(side='KING', 
                                           opponent=convert_color_to_player(game, 
                                            color=swap_colors(cur_player.color))))
            (cloned_game_after_move, 
             cloned_player, 
             cloned_opponent, _) = clone_game_and_get_game_state_based_on_move(game, 
                                                                                castle_side_color=['KING', 
                                                                                cur_player.color])
        else:
            assert(False)
    else:
        assert(len(move) == 2)
        assert(cur_player.bool_move_legal(pos=move[0], dest=move[1]))
        (cloned_game_after_move, 
        cloned_player, 
        cloned_opponent, _) = clone_game_and_get_game_state_based_on_move(game, 
                                                                           pos=move[0], 
                                                                           dest=move[1])
        
    return minimax(cur_game=cloned_game_after_move, cur_player=cloned_opponent, 
                   depth=depth, is_maximizing_player=not is_maximizing_player)


def minimax(cur_game, cur_player, depth, is_maximizing_player) -> float:
    '''
    Minimax algorithm.
    cur_game: a Game with state of current game.
    cur_player: whichever Player the 'maximizing_player' refers to (p1 or p2). It's
    assumed that cur_game state is the beginning of cur_player's turn.
    (TODO FIXME Need to update cur_game so that it behaves that way? yes or no?)
    depth: Number of levels deep we want to look ahead from cur_game state.
    is_maximizing_player: bool on whether cur_player is a value maximizing or minimizing player.

    Returns: minimax value given cur_game state for cur_player.
    '''
    terminal_game = False # whether cur_player has any other outs, 
    # ie on if its stalemate or checkmate.
    if depth == 0 or terminal_game:
        if terminal_game: # ie opponent opposing cur_player can't move
            penalty_offset = -1 if is_maximizing_player else 1
            return penalty_offset * 1000 # TODO 0 for stalemate, ±1000 penalty on cur_player for getting checkmated.
        else:
            return value(cur_game, cur_player, is_maximizing_player)
    if is_maximizing_player:
        value_num = -1000
    else:
        value_num = 1000

    return value_num


def value(cur_game, cur_player, is_maximizing_player) -> float:
    '''
    Value function for given cur_player and cur_game, based on the
    cur_player's remaining pieces, opponent's remaining pieces, 
    and cur_player's piece positions (and maybe opponent's piece
    positions).
    '''
    # TODO make it additionally factor in board position.
    value = 0 # value is absolute, ie want >>0 for maximizing player, want << 0 for min player
    offset = 1 if is_maximizing_player else -1 # multiplicative offset for max/min player
    opponent = convert_color_to_player(cur_game, color=swap_colors(cur_player.color))
    rank_point = {'PAWN': 1, 'KNIGHT': 3, 'BISHOP': 3, 'ROOK': 5, 'QUEEN': 9}
    cur_player_king_exists, opponent_king_exists = False, False
    for piece in cur_player.pieces.values():
        if piece.rank == 'KING':
            cur_player_king_exists = True
            continue # king should always exist, and is priceless
        value += offset * rank_point[piece.rank]

    for piece in opponent.pieces.values():
        if piece.rank == 'KING':
            opponent_king_exists = True
            continue # king should always exist, and is priceless
        value -= offset * rank_point[piece.rank]

    assert(cur_player_king_exists and opponent_king_exists)

    return value