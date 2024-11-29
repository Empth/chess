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

    Returns: minimax value of move by cur_player.
    '''
    clone_game_after_move = None
    if type(move) == str:
        if move == 'QC':
            assert(cur_player.bool_castle_legal(side='QUEEN', 
                                           opponent=convert_color_to_player(game, 
                                            color=swap_colors(cur_player.color))))
            #clone_game_after_move = clone_game_and_get_game_state_based_on_move()
        elif move == 'KC':
            assert(cur_player.bool_castle_legal(side='KING', 
                                           opponent=convert_color_to_player(game, 
                                            color=swap_colors(cur_player.color))))
            #clone_game_after_move = clone_game_and_get_game_state_based_on_move()
        else:
            assert(False)
    else:
        assert(len(move) == 2)
        assert(cur_player.bool_move_legal)
        #clone_game_after_move = clone_game_and_get_game_state_based_on_move()
    #return minimax()
    return 1


def minimax(cur_game, cur_player, depth, is_maximizing_player) -> float:
    '''
    Minimax algorithm.
    cur_game: a Game with state of current game.
    cur_player: whichever Player the 'maximizing_player' refers to (p1 or p2).
    depth: Number of levels deep we want to look ahead from cur_game state.
    is_maximizing_player: bool on whether cur_player is a value maximizing or minimizing player.

    Returns: minimax value given cur_game state for cur_player.
    '''
    return 0 