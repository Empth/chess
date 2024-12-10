from helpers.game_helpers import convert_color_to_player, get_opponent
from helpers.general_helpers import swap_colors, get_tuple, rotate_coordinates, convert_coord
from helpers.state_helpers import is_endgame
from misc.constants import *
from misc.tables import *
import random

count = 0

def minimax(cur_game, cur_player, depth, is_maximizing_player, alpha=-MAX, beta=MAX, 
            alpha_beta_mode=True, shuffle=False, first_call=True):
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
    shuffle: Randomize order of all_legal_moves or not.
    first_call: Whether minimax was first called from non-minimax 
    (for progress bar).

    Returns: minimax value given cur_game state for cur_player.
    '''
    cur_opponent = get_opponent(cur_game, cur_player)
    all_legal_moves = cur_player.get_all_legal_moves()
    mvv_lva_sorted_moves = mvv_lva_order_moves(cur_game, cur_player, all_legal_moves)
    assert(len(all_legal_moves) == len(mvv_lva_sorted_moves))
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
    i = 0
    for move in mvv_lva_sorted_moves:
        success_status = cur_player.attempt_action(move, True)
        assert(success_status)
        move_score, opponent_move = minimax(cur_game, cur_opponent, depth-1, 
                                            not is_maximizing_player,
                                            alpha, beta, alpha_beta_mode, 
                                            shuffle, first_call=False)
        if player_polarity * move_score > player_polarity * best_score:
            best_score = move_score
            best_move = move

        cur_game.unmake_turn()

        if first_call:
            i += 1
            print(str(i)+'/'+str(n)+' '+str(move))

        if alpha_beta_mode:
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
    game_value = 0 # game_value is absolute, ie want >>0 for maximizing player, want << 0 for min player
    offset = 1 if is_maximizing_player else -1 # multiplicative offset for max/min player
    is_end = is_endgame(cur_game)
    opponent = convert_color_to_player(cur_game, color=swap_colors(cur_player.color))
    player_score = get_player_score(cur_player, is_end)
    opponent_score = get_player_score(opponent, is_end)
    game_value = offset * (player_score - opponent_score)
    random.seed(42)
    randomness = 0 if fuzz == 0 else random.uniform(-fuzz, fuzz)

    return game_value + randomness


def get_player_score(player, is_endgame) -> float:
    '''
    Get pure material value of this player's pieces,
    plus piece penalties from strength of individual piece 
    positions from piece square table.
    Score is raw (e.g. positive)
    is_endgame: If game is in endgame.
    '''
    rotate_pos = (player.color == BLACK) # rotate positions on PENALTY table if BLACK player
    king_suffix = 'END' if is_endgame else 'MID'
    value = 0
    penalty = 0
    for piece in player.pieces.values():
        rank = piece.rank
        penalty_code = rank if rank != KING else rank+king_suffix # key for PENALTY table
        value += VALUE[rank]
        piece_pos = piece.pos if not rotate_pos else rotate_coordinates(piece.pos)
        x, y = convert_coord(piece_pos)
        penalty += PENALTY[penalty_code][x][y]

    return value + penalty


def mvv_lva_order_moves(game, player, move_arr):
    '''
    Given a list of player's legal moves, order player's 
    capturing moves according to MVV-LVA, and put them in the front
    of the returning array.
    We treat en passant as a non-capture for convinience.
    Castle moves sits in non-capture portion of array.
    Returns: Reordered move array.
    '''
    non_capture_moves = []
    unsorted_capture_moves = []
    sorted_capture_moves = []
    board = game.board
    cap_move_score_map = {} # maps from idx of capturing pos->dest move 
                        # in unsorted_capture_moves array to its MVV-LVA score
    value_map = RANK_VALUE_MAP
    n = len(value_map)
    # split non_capture_moves and capture_moves
    for move in move_arr:
        if type(move) == str:
            assert(move in KQSET)
            non_capture_moves.append(move)
        else:
            pos, dest = move
            if not board.piece_exists(dest):
                # move does not capture
                non_capture_moves.append(move)
            else:
                piece_on_dest = board.get_piece(dest)
                assert(piece_on_dest != None)
                if piece_on_dest.color == player.color:
                    # move does not capture teammate
                    non_capture_moves.append(move)
                else:
                    unsorted_capture_moves.append(move)



    # build up our move->score map with capturing moves
    i = 0
    for move in unsorted_capture_moves:
        pos, dest = move
        victim = board.get_piece(dest)
        aggressor = board.get_piece(pos)
        assert(aggressor != None)
        assert(victim != None)
        assert(victim.rank != KING)
        victim_value = value_map[victim.rank]
        aggressor_value = value_map[aggressor.rank]
        cap_move_score_map[i] = n * victim_value + (n - 1 - aggressor_value)
        # ^ zig-zag bijection, highest score is 6*4 + 5 = 29 (PxQ) 
        # and lowest is 6*0 + 0 = 0 (KxP)
        i += 1

    sorted_capture_idx = sorted(cap_move_score_map, # type: ignore
                                    key=cap_move_score_map.get, # type: ignore
                                    reverse=True) # type: ignore
    
    for idx in sorted_capture_idx:
        sorted_capture_moves.append(unsorted_capture_moves[idx])


    return sorted_capture_moves+non_capture_moves


