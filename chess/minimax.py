from helpers.game_helpers import convert_color_to_player, get_opponent
from helpers.general_helpers import swap_colors
from misc.constants import *
import random

count = 0

def minimax(cur_game, cur_player, depth, is_maximizing_player, alpha=-MAX, beta=MAX, alpha_beta_mode=True) -> float:
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
                return penalty_offset * MAX # MAX penalty on cur_player for getting checkmated.
            else: # stalemate
                return 0
        else:
            return value(cur_game, cur_player, is_maximizing_player)

    if is_maximizing_player:
        value_num = -MAX
        j = 0
        for move in all_legal_moves:
            # first arg of omit should be 'not cur_player.in_check'
            success_status = cur_player.attempt_action(move, True)
            '''
            if j == 29:
                if cur_opponent.pieces['P-D7'].pos == [4, 5]:
                    print(cur_game.board)
                    print('hit')
            '''
            assert(success_status)
            value_num = max(value_num, 
                            minimax(cur_game, cur_opponent, depth-1, False,
                                    alpha=alpha, beta=beta,
                                    alpha_beta_mode=alpha_beta_mode))
            cur_game.unmake_turn()
            if value_num > beta and alpha_beta_mode:
                break # value_num too big, min player will derive no value exploring this node's branches
            alpha = max(alpha, value_num)
            j += 1
        return value_num
    else:
        value_num = MAX
        k = 0
        for move in all_legal_moves:
            '''
            if k == 1:
                if cur_opponent.pieces['B-F1'].pos == [2, 5]:
                    print(cur_game.board)
                    print('i')
            '''
            success_status = cur_player.attempt_action(move, True)
            assert(success_status)
            value_num = min(value_num, 
                            minimax(cur_game, cur_opponent, depth-1, True,
                                    alpha=alpha, beta=beta,
                                    alpha_beta_mode=alpha_beta_mode))
            cur_game.unmake_turn()
            if value_num < alpha and alpha_beta_mode:
                break # value_num too small, max player will derive no value exploring this node's branches
            beta = min(beta, value_num)
            k+=1
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