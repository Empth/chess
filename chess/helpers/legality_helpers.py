from misc.constants import *

'''
Helper functions for move legality and error message handling flow.
'''

def pawn_starting(player: 'Player', piece): # type: ignore
    '''
    Checks to see if 'piece', which must be a pawn, is in a starting position.
    '''

    if piece.rank != 'PAWN':
        raise Exception("Piece needs to be a pawn")
    
    if piece.color == WHITE:
        if piece.pos[1] == 2:
            return True
    elif piece.color == BLACK:
        if piece.pos[1] == 7:
            return True
    else:
        raise Exception("Piece needs to have a B/W color")

    return False

def pawn_moving_straight_forward(player, piece, dest):

    '''
    Checks to see if the pawn is moving strictly straight and forward
    '''

    if piece.rank != 'PAWN':
        raise Exception("Piece needs to be a pawn")
    
    if piece.color == WHITE:
        if piece.pos[0] == dest[0] and piece.pos[1] < dest[1]:
            return True
    elif piece.color == BLACK:
        if piece.pos[0] == dest[0] and piece.pos[1] > dest[1]:
            return True
    else:
        raise Exception("Piece needs to have a B/W color")

    return False

def pawn_moving_diagonal_forward(player, piece, dest):
    '''
    Checks to see if the pawn is moving strictly diagonally forward
    '''

    if piece.rank != 'PAWN':
        raise Exception("Piece needs to be a pawn")
    
    diagonal_check = (abs(piece.pos[0] - dest[0]) == abs(piece.pos[1] - dest[1])) # same x, y distances

    if piece.color == WHITE:
        if piece.pos[1] < dest[1] and diagonal_check:
            return True
    elif piece.color == BLACK:
        if piece.pos[1] > dest[1] and diagonal_check:
            return True
    else:
        raise Exception("Piece needs to have a B/W color")

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