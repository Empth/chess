from helpers.game_helpers import convert_color_to_player, get_opponent
from helpers.general_helpers import swap_colors
from misc.constants import *
import random

count = 0

def minimax(cur_game, cur_player, depth, is_maximizing_player, alpha=-MAX, beta=MAX, alpha_beta_mode=True):
    '''
    Minimax algorithm.
    cur_game: a Game with state of current game.
    cur_player: whichever Player the 'maximizing_player' refers to (p1 or p2). It's
    assumed that cur_game state is the beginning of cur_player's turn.
    depth: Number of levels deep we want to look ahead from cur_game state.
    is_maximizing_player: bool on whether cur_player is a value maximizing or minimizing player.
    alpha: Minimum guarenteed value that maximizing player will get.
    beta: Maximum guarenteed value that minimizing player will get.
    alpha_beta_mode: Toggle for alpha-beta pruning on/off.

    Returns: minimax value given cur_game state for cur_player.
    '''
    cur_opponent = get_opponent(cur_game, cur_player)
    all_legal_moves = cur_player.get_all_legal_moves()
    n = len(all_legal_moves)
    terminal_game = (n == 0) # whether cur_player has any other outs, 
                            # ie on if its stalemate or checkmate.
    if depth == 0 or terminal_game:
        if terminal_game: # ie cur_player can't move
            if cur_player.in_check: # checkmate
                penalty_offset = -1 if is_maximizing_player else 1
                return penalty_offset * MAX, None # MAX penalty on cur_player for getting checkmated.
            else: # stalemate
                return float(0), None
        else:
            return value(cur_game, cur_player, is_maximizing_player), None
        
    player_polarity = 1 if is_maximizing_player else -1
    best_score = -MAX if is_maximizing_player else MAX # the best guarenteeable score for cur_player
    best_move = None
    for move in all_legal_moves:
        success_status = cur_player.attempt_action(move, True)
        assert(success_status)
        move_score, opponent_move = minimax(cur_game, cur_opponent, depth-1, 
                                            not is_maximizing_player,
                                            alpha, beta, alpha_beta_mode)
        if player_polarity * move_score > player_polarity * best_score:
            best_score = move_score
            best_move = move

        cur_game.unmake_turn()
        if is_maximizing_player:
            if best_score > beta:
                break # best_score is too big, min player from above will derive 
                        # no value exploring this node's branches.
            alpha = max(alpha, best_score)
        else:
            if best_score < alpha:
                break # best_score is too small, max player from above will derive 
                        # no value exploring this node's branches.
            beta = min(beta, best_score)

    return best_score, best_move


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