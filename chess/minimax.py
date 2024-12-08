from helpers.game_helpers import convert_color_to_player
from helpers.general_helpers import swap_colors
from misc.constants import *
import random

num_evaluated_nodes = 0

def evaluate_minimax_of_move(game, move, cur_player, depth, is_maximizing_player=False, 
                             alpha=-MAX, beta=MAX, alpha_beta_mode=True) -> float:
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
    alpha: Minimum guarenteed value that maximizing player will get.
    beta: Maximum guarenteed value that minimizing player will get.
    alpha_beta_mode: Toggle for alpha-beta pruning on/off.

    Note, depth 1 in eval_minimax really behaves like a depth 2 search 
    in the case where cur_player is free to make any move.

    Returns: minimax value of move by cur_player.
    '''
    (cloned_game_after_move, _, 
     cloned_opponent, _) = get_cloned_game_state_based_on_generalized_move(game=game, 
                                                                           player=cur_player, 
                                                                           move=move)
    game.debug_val = num_evaluated_nodes
    return minimax(cur_game=cloned_game_after_move, cur_player=cloned_opponent, 
                   depth=depth, is_maximizing_player=not is_maximizing_player, 
                   alpha=alpha, beta=beta, alpha_beta_mode=alpha_beta_mode)


def minimax(cur_game, cur_player, depth, is_maximizing_player, alpha=-MAX, beta=MAX, alpha_beta_mode=True) -> float:
    '''
    Minimax algorithm.
    cur_game: a Game with state of current game.
    cur_player: whichever Player the 'maximizing_player' refers to (p1 or p2). It's
    assumed that cur_game state is the beginning of cur_player's turn.
    (TODO FIXME Need to update cur_game so that it behaves that way? yes or no????)
    depth: Number of levels deep we want to look ahead from cur_game state.
    is_maximizing_player: bool on whether cur_player is a value maximizing or minimizing player.
    alpha: Minimum guarenteed value that maximizing player will get.
    beta: Maximum guarenteed value that minimizing player will get.
    alpha_beta_mode: Toggle for alpha-beta pruning on/off.

    Returns: minimax value given cur_game state for cur_player.
    '''
    terminal_game = player_is_locked(cur_game, cur_player) # whether cur_player has any other outs, 
                                                            # ie on if its stalemate or checkmate.
    if depth == 0 or terminal_game:
        global num_evaluated_nodes
        num_evaluated_nodes += 1
        if terminal_game: # ie opponent opposing cur_player can't move
            if cur_player.in_check: # checkmate
                penalty_offset = -1 if is_maximizing_player else 1
                return penalty_offset * MAX # MAX penalty on cur_player for getting checkmated.
            else: # stalemate
                return 0
        else:
            return value(cur_game, cur_player, is_maximizing_player)
        
    cur_player_true_legal_moves = get_all_truly_legal_player_moves(cur_game, cur_player) # all genuine legal moves.

    if is_maximizing_player:
        value_num = -MAX
        for move in cur_player_true_legal_moves:
            (cloned_game_after_move, _, 
            cloned_opponent, _) = get_cloned_game_state_based_on_generalized_move(game=cur_game,
                                                                                  player=cur_player,
                                                                                  move=move)
            value_num = max(value_num, 
                            minimax(cloned_game_after_move, 
                                    cloned_opponent,
                                    depth-1, False,
                                    alpha=alpha, beta=beta,
                                    alpha_beta_mode=alpha_beta_mode))
            
            if value_num > beta and alpha_beta_mode:
                break # value_num too big, min player will derive no value exploring this node's branches
            alpha = max(alpha, value_num)
        return value_num
    else:
        value_num = MAX
        for move in cur_player_true_legal_moves:
            (cloned_game_after_move, _, 
            cloned_opponent, _) = get_cloned_game_state_based_on_generalized_move(game=cur_game,
                                                                                  player=cur_player,
                                                                                  move=move)
            value_num = min(value_num, 
                            minimax(cloned_game_after_move, 
                                    cloned_opponent,
                                    depth-1, True,
                                    alpha=alpha, beta=beta,
                                    alpha_beta_mode=alpha_beta_mode))
            
            if value_num < alpha and alpha_beta_mode:
                break # value_num too small, max player will derive no value exploring this node's branches
            beta = min(beta, value_num)
        return value_num


def value(cur_game, cur_player, is_maximizing_player, fuzz=0) -> float:
    '''
    Value function for given cur_player and cur_game, based on the
    cur_player's remaining pieces, opponent's remaining pieces, 
    and cur_player's piece positions (and maybe opponent's piece
    positions).
    fuzz: Variance parameter on amount of randomness added to value.
    Returns: Value
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

    randomness = 0 if fuzz == 0 else random.uniform(-fuzz, fuzz)

    return value + randomness


def get_cloned_game_state_based_on_generalized_move(game, player, move):
    '''
    A wrapper for clone_game_and_get_game_state_based_on_move(), specialized for minimax.
    # TODO this wrapper should be implementable in the clone_game_and_get... method in state_helpers
    # TODO side calls for 'QUEEN', 'KING' should be generalized to 'QC', 'KC' ? but only if
    # that yields any tangible benefits for code reduction.
    Takes in any general 'move', which is either 
    [[x_0, y_0], [x_1, y_1]] pos->dest
    or 'QC'/'KC' castle.
    game: Game. Won't be modified.
    player: The Player making move. Won't be modified.
    move: [[x_0, y_0], [x_1, y_1]], 'QC', 'KC'
    Required: move is truly legal for player (ie for pos->dest, doesn't self suicide into check)
    Returns (in order): the cloned Game, the cloned Player which made the move, 
    the opposing cloned opponent Player, and the cloned Board.
    '''

    (cloned_game_after_move, cloned_player, 
     cloned_opponent, cloned_board) = None, None, None, None
    
    if type(move) == str:
        if move == 'QC':
            assert(player.bool_castle_legal(side='QUEEN', 
                                           opponent=convert_color_to_player(game, 
                                            swap_colors(player.color))))
            (cloned_game_after_move, 
             cloned_player, 
             cloned_opponent,
             cloned_board) = clone_game_and_get_game_state_based_on_move(game, 
                                                                        castle_side_color=['QUEEN', 
                                                                        player.color])
        elif move == 'KC':
            assert(player.bool_castle_legal(side='KING', 
                                           opponent=convert_color_to_player(game, 
                                            swap_colors(player.color))))
            (cloned_game_after_move, 
             cloned_player, 
             cloned_opponent, 
             cloned_board) = clone_game_and_get_game_state_based_on_move(game, 
                                                                        castle_side_color=['KING', 
                                                                        player.color])
        else:
            assert(False)
    else:
        assert(len(move) == 2)
        assert(player.bool_move_legal(pos=move[0], dest=move[1]))
        assert(not move_puts_player_in_check(game, move[0], move[1]))
        (cloned_game_after_move, 
        cloned_player, 
        cloned_opponent, 
        cloned_board) = clone_game_and_get_game_state_based_on_move(game, 
                                                                    pos=move[0], 
                                                                    dest=move[1])
        
    return cloned_game_after_move, cloned_player, cloned_opponent, cloned_board