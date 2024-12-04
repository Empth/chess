from misc.constants import *
from .general_helpers import ordinal_direction

'''
Helper functions for move legality and error message handling flow.
'''

def pawn_moving_straight_forward(player, piece, dest):

    '''
    Checks to see if the pawn is moving strictly straight and forward
    '''

    if piece.rank != 'PAWN':
        raise Exception("Piece needs to be a pawn!")
    
    if piece.color == WHITE:
        if piece.pos[0] == dest[0] and piece.pos[1] < dest[1]:
            return True
    elif piece.color == BLACK:
        if piece.pos[0] == dest[0] and piece.pos[1] > dest[1]:
            return True
    else:
        raise Exception("Piece needs to have a B/W color!")

    return False

def pawn_moving_diagonal_forward(player, piece, dest):
    '''
    Checks to see if the pawn is moving strictly diagonally forward
    '''

    if piece.rank != 'PAWN':
        raise Exception("Piece needs to be a pawn!")
    
    diagonal_check = (abs(piece.pos[0] - dest[0]) == abs(piece.pos[1] - dest[1])) # same x, y distances

    if piece.color == WHITE:
        if piece.pos[1] < dest[1] and diagonal_check:
            return True
    elif piece.color == BLACK:
        if piece.pos[1] > dest[1] and diagonal_check:
            return True
    else:
        raise Exception("Piece needs to have a B/W color!")

    return False

def cardinal_dest_between_collider(init_pos, collider_pos, dest, cardinal, is_pawn=False):
    '''
    Helper for rooks/queens cardinal directional movers.
    Also applicable for pawns, with their custom collision logic.
    Checks to see if dest is in between init_pos and collider_pos (inclusive),
    wrt cardinal direction. If so, returns True, otherwise, returns False.
    '''
    if not is_pawn:
        if cardinal == 'N':
            return init_pos[1] <= dest[1] <= collider_pos[1]
        elif cardinal == 'S':
            return collider_pos[1] <= dest[1] <= init_pos[1]
        elif cardinal == 'E':
            return init_pos[0] <= dest[0] <= collider_pos[0]
        elif cardinal == 'W':
            return collider_pos[0] <= dest[0] <= init_pos[0]
        else:
            raise Exception('Wrong cardinal input!')
    else:
        assert(cardinal in ['N', 'S'])
        if cardinal == 'N':
            return init_pos[1] < dest[1] < collider_pos[1]
        else:
            assert(cardinal == 'S')
            return collider_pos[1] < dest[1] < init_pos[1]


def get_cardinal_collision(board, pos, cardinal):
    '''
    Helper for cardinal movement collision.
    For a piece with unlimited cardinal movement, ie rook or queen, returns the position
    of the first piece that something from 'pos' will encounter when moving in 'cardinal' direction.
    Returns None if no such colliding piece exists.
    Required: cardinal is 'N', 'E', 'S', 'W'
    '''
    assert(cardinal in set(['N', 'E', 'S', 'W']))

    movement_tiles, collider_encountered = get_all_cardinal_tiles_til_collider(board=board, pos=pos,
                                                                               cardinal=cardinal)
    if collider_encountered:
        return movement_tiles[-1] # read documentation of get_all_cardinal_ on why this will work
    else:
        return None
    

def get_all_cardinal_tiles_til_collider(board, pos, cardinal):
    '''
    Helper for straight movers. Core logic for get_cardinal_collision, rook_movement_zone.
    Given pos, cardinal, returns two values. First is an array of all tiles in order 
    when starting movement out of pos in the cardinal direction,
    up to and including the first colliding tile in cardinal direction.
    For example, for an D4 (pos 4,4) Rook headed North, with collider on D7 (pos 4,7), we return
    [[4,5], [4,6], [4,7]] in that order of tile movement.
    Second return value is boolean for whether a collider was encountered or not.
    '''
    assert(cardinal in set(['N', 'E', 'S', 'W']))
    dictionary = {'N':['y', 1], 'E':['x', 1], 'S':['y', -1], 'W':['x', -1]} # abs_dir, i, sign
    value = dictionary[cardinal]
    abs_dir, sign = value[0], value[1]  # abs_dir: 'x' or 'y'; movement in x dir or y dir;sign differentiates N vs S, E vs W
    i = pos[0] if abs_dir == 'x' else pos[1]
    collider_encountered = False
    movement_tiles = []

    while True:
        i += sign
        if i-1 not in range(8):
            break # we went out of bounds
        if abs_dir == 'x':
            movement_tiles.append([i, pos[1]])
            if board.piece_exists(pos=[i, pos[1]]):
                collider_encountered = True
                break
        else:
            movement_tiles.append([pos[0], i])
            if board.piece_exists(pos=[pos[0], i]):
                collider_encountered = True
                break

    return movement_tiles, collider_encountered

def get_ordinal_collision(board, pos, ordinal):
    '''
    Helper for ordinal movement collision.
    For a piece with unlimited ordinal movement, ie bishop or queen, returns the position
    of the first piece that something from 'pos' will encounter when moving in the 'ordinal' direction.
    Returns None if no such colliding piece exists.
    Required: cardinal is 'NE', 'SE', 'SW', 'NW'
    '''
    assert(ordinal in set(['NE', 'SE', 'SW', 'NW']))
    movement_tiles, collider_encountered = get_all_ordinal_tiles_til_collider(board=board, pos=pos,
                                                                               ordinal=ordinal)
    if collider_encountered:
        return movement_tiles[-1] # read documentation of get_all_ordinal_ on why this will work
    else:
        return None

def get_all_ordinal_tiles_til_collider(board, pos, ordinal):
    '''
    Helper for diagonal movers. Core logic for get_ordinal_collision, bishop_movement_zone.
    Given pos, ordinal, returns two values. First is an array of all tiles in order 
    when starting movement out of pos in the ordinal direction,
    up to and including the first colliding tile in said ordinal direction.
    For example, for an D4 (pos 4,4) Bishop headed NE, with collider on G7 (pos 7,7), we return
    [[5,5], [6,6], [7,7]] in that order of tile movement.
    Second return value is boolean for whether a collider was encountered or not.
    '''
    assert(ordinal in set(['NE', 'SE', 'SW', 'NW']))
    dictionary = {'NE': [1, 1], 'SE': [1, -1], 'SW': [-1, -1], 'NW': [-1, 1]} # x_dir, y_dir
    value = dictionary[ordinal]
    x_dir, y_dir = value[0], value[1]
    x, y = pos[0], pos[1]
    collider_encountered = False
    movement_tiles = []

    while True:
        x += x_dir
        y += y_dir
        if x-1 not in range(8) or y-1 not in range(8):
            break # we went oob
        movement_tiles.append([x, y])
        if board.piece_exists(pos=[x, y]):
            collider_encountered = True
            break

    return movement_tiles, collider_encountered


def ordinal_dest_between_collider(init_pos, collider_pos, dest, ordinal):
    '''
    Helper for bishops/queens ordinal directional movers.
    Checks to see if dest is in between init_pos and collider_pos (inclusive), 
    wrt ordinal direction. If so, returns True, otherwise, returns False.
    '''
    if ordinal == 'NE':
        assert((init_pos[0] <= dest[0] <= collider_pos[0]) == 
                (init_pos[1] <= dest[1] <= collider_pos[1]))
        return init_pos[0] <= dest[0] <= collider_pos[0]
    elif ordinal == 'SE':
        assert((init_pos[0] <= dest[0] <= collider_pos[0]) == 
                (collider_pos[1] <= dest[1] <= init_pos[1]))
        return init_pos[0] <= dest[0] <= collider_pos[0]
    elif ordinal == 'SW':
        assert((collider_pos[0] <= dest[0] <= init_pos[0]) == 
                (collider_pos[1] <= dest[1] <= init_pos[1]))
        return collider_pos[0] <= dest[0] <= init_pos[0]
    elif ordinal == 'NW':
        assert((collider_pos[0] <= dest[0] <= init_pos[0]) == 
                (init_pos[1] <= dest[1] <= collider_pos[1]))
        return collider_pos[0] <= dest[0] <= init_pos[0]
    else:
        raise Exception('Wrong ordinal input!')
    

def non_bool_en_passant_legal(piece, dest, player) -> tuple[bool, str]:
    '''
    Method checks if attempted piece to dest en passant move is legal.
    player: Player of pawn initiating en passant.
    Required: Piece on pos is PAWN, pos->dest move is 1 diagonal unit in color's forward direction,
    dest is an in range tile, board at dest is empty. If one of these fails, an assertion error is given.
    Returns: Legality boolean, error message string OR special command 'EN PASSANT' if legal.
    The special command 'EN PASSANT' tells the caller to initiate an en passant move.
    '''
    assert(player.color in BWSET)
    assert(piece.rank == 'PAWN')
    assert(pawn_moving_diagonal_forward(player, piece, dest))
    assert(not player.board.piece_exists(dest))
    pos = piece.pos
    ord_dir = ordinal_direction(pos, dest)
    look = ord_dir[1] # 'E' or 'W' in absolute cardinal direction, white bottom, black top.
                        # look here to check if 1) Opposite colored Pawn exists
                        # 2) that they 2 leaped the previous turn before.
                        # If so, you can return True.
    assert(look in set(['E', 'W']))
    offset = 1 if look == 'E' else -1
    assert(pos[0]+offset == dest[0]) # sanity checks
    assert(dest[0]-1 in range(8) and dest[1]-1 in range(8))
    looked_at_piece = player.board.get_piece([pos[0]+offset, pos[1]])
    if looked_at_piece == None:
        return (False, 'You can only move '+str(player.board.get_piece(pos=pos).rank)+
                ' diagonally via capture or en passant!') # same as before
    if looked_at_piece.rank != 'PAWN' or looked_at_piece.color == player.color:
        return (False, 'You can only move '+str(player.board.get_piece(pos=pos).rank)
                +' diagonally via capture or en passant!')
    else: # looked_at_piece is pawn and opponent color. 1) is cleared.
        if not looked_at_piece.pawn_two_leap_on_prev_turn:
            return (False, 'Cannot en passant here as opposing PAWN did not move two '
                    +'tiles forward on the previous turn!')
        else:
            return True, 'EN PASSANT'


def bool_en_passant_legal(piece, dest, player) -> bool:
    return non_bool_en_passant_legal(piece, dest, player)[0]

def piece_exists_on_pos_offset(board, pos, offsets, finding_piece) -> bool:
    '''
    Finds whether a 'finding_piece' with rank, color exists, on any in bounds
    pos+offset[i] position on board.
    board: board
    pos: [x, y] in [8]^2
    offsets: array of [deltax, deltay] offsets
    finding_piece: len 2 array with string params of RANK, COLOR in that order
    Returns: False if no such piece exists on board. Otherwise, returns True.
    '''
    assert(pos[0]-1 in range(8) and pos[1]-1 in range(8))
    assert(len(finding_piece) == 2)
    assert(finding_piece[1] in BWSET)
    for offset in offsets:
        x, y = pos[0]+offset[0], pos[1]+offset[1] # x, y still [8]^2 notation
        if x-1 not in range(8) or y-1 not in range(8):
            continue
        gotten_piece = board.get_piece([x, y])
        if gotten_piece == None:
            continue
        if gotten_piece.rank == finding_piece[0] and gotten_piece.color == finding_piece[1]:
            return True
        
    return False

    
