from helpers.legality_helpers import get_all_cardinal_tiles_til_collider, get_all_ordinal_tiles_til_collider
from helpers.general_helpers import get_tiles_from_offset_pos, convert_to_movement_set

'''
Functions for retrieving the movement zones of all 6 ranks of pieces.
The return type for these functions will be a set of of (x, y), these 
represent the movement zone of the piece.
'''
def get_movement_zone(board, piece):
    '''
    Gets movement zone of given piece, which is an set of (x, y) which piece
    can move to. 
    Returns empty set if piece is None.
    '''
    if piece == None:
        return set()

    rank = piece.rank
    if rank == 'PAWN':
        return pawn_movement_zone(board=board, piece=piece)
    elif rank == 'ROOK':
        return rook_movement_zone(board=board, piece=piece)
    elif rank == 'BISHOP':
        return bishop_movement_zone(board=board, piece=piece)
    elif rank == 'KNIGHT':
        return knight_movement_zone(board=board, piece=piece)
    elif rank == 'QUEEN':
        return queen_movement_zone(board=board, piece=piece)
    elif rank == 'KING':
        return king_movement_zone(board=board, piece=piece)

    raise Exception('To determine piece movement zone, piece must have one of the 6 ranks!')

def pawn_movement_zone(board, piece):
    '''
    Returns movement zone of given pawn piece.
    '''
    assert(piece.rank == 'PAWN')
    assert(piece.color in ['BLACK', 'WHITE'])
    movement_tiles = []
    colored_ordinal = ['NW', 'NE'] if piece.color == 'WHITE' else ['SW', 'SE']
    colored_cardinal = 'N' if piece.color == 'WHITE' else 'S'

    # first retrieve diagonal tiles in the movement zone.
    for ord_dir in colored_ordinal:
        dir_movement_tiles, collider_found = get_all_ordinal_tiles_til_collider(board=board, 
                                                                                 pos=piece.pos, 
                                                                                 ordinal=ord_dir)
        if not collider_found:
            continue # as this mean there is no piece 1 unit diagonally from this pawn in the ord_dir direction
        elif len(dir_movement_tiles) == 0:
            assert(False)
        elif len(dir_movement_tiles) > 1:
            continue # this means first collider isn't found 1 unit diagonally from this pawn in ord_dir direction
        else: # dir_movement_tiles is singleton
            diag_piece = board.get_piece(pos=dir_movement_tiles[0])
            if diag_piece.color == piece.color:
                continue
            else: # this is a capturable piece
                movement_tiles.append(dir_movement_tiles[0])

    # next add straight tiles to movement_zone.
    (straight_movement_tiles, 
     straight_collider_found) = get_all_cardinal_tiles_til_collider(board=board, 
                                                                    pos=piece.pos, 
                                                                    cardinal=colored_cardinal)
    if straight_collider_found:
        if len(straight_movement_tiles) >= 3:
            if not piece.moved:
                movement_tiles.append(straight_movement_tiles[1]) # ie pawn can move 2 units straight
            movement_tiles.append(straight_movement_tiles[0])
        elif len(straight_movement_tiles) == 2:
            movement_tiles.append(straight_movement_tiles[0])
    else: # no straight collider
        if len(straight_movement_tiles) >= 2:
            if not piece.moved:
                movement_tiles.append(straight_movement_tiles[1])
            movement_tiles.append(straight_movement_tiles[0])
        elif len(straight_movement_tiles) == 1: # might be unreachable, putting it here just in case
            movement_tiles.append(straight_movement_tiles[0])

    return convert_to_movement_set(movement_tiles)

def rook_movement_zone(board, piece):
    '''
    Returns movement zone of given rook piece.
    '''
    assert(piece.rank == 'ROOK' or piece.rank == 'QUEEN') # for queen to reuse function.
    cardinals = ['N', 'E', 'S', 'W']
    movement_tiles = []
    for dir in cardinals:
        dir_movement_tiles, collider_found = get_all_cardinal_tiles_til_collider(board=board, 
                                                                                 pos=piece.pos, 
                                                                                 cardinal=dir)
        if collider_found:
            collider_piece = board.get_piece(pos=dir_movement_tiles[-1])
            if collider_piece.color == piece.color:
                dir_movement_tiles.pop()
        movement_tiles = movement_tiles + dir_movement_tiles

    return convert_to_movement_set(movement_tiles)

def bishop_movement_zone(board, piece):
    '''
    Returns movement zone of given bishop piece.
    '''
    assert(piece.rank == 'BISHOP' or piece.rank == 'QUEEN') # for queen to reuse function.
    ordinals = ['NE', 'SE', 'SW', 'NW']
    movement_tiles = []
    for dir in ordinals:
        dir_movement_tiles, collider_found = get_all_ordinal_tiles_til_collider(board=board,
                                                                                pos=piece.pos,
                                                                                ordinal=dir)
        if collider_found:
            collider_piece = board.get_piece(pos=dir_movement_tiles[-1])
            if collider_piece.color == piece.color:
                dir_movement_tiles.pop()
        movement_tiles = movement_tiles + dir_movement_tiles
    return convert_to_movement_set(movement_tiles)

def queen_movement_zone(board, piece):
    '''
    Returns movement zone of given queen piece.
    '''
    assert(piece.rank == 'QUEEN')
    return rook_movement_zone(board, piece).union(bishop_movement_zone(board, piece))

def knight_movement_zone(board, piece):
    '''
    Returns movement zone of given knight piece.
    '''
    assert(piece.rank == 'KNIGHT')
    offsets = [[1, 2], [2, 1], [-1, 2], [2, -1], [1, -2], [-2, 1], [-1, -2], [-2, -1]]
    return movement_zone_given_offset(board=board,piece=piece, offsets=offsets)

def king_movement_zone(board, piece):
    '''
    Returns movement zone of given king piece.
    '''
    assert(piece.rank == 'KING')
    offsets = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
    return movement_zone_given_offset(board=board,piece=piece, offsets=offsets)

def movement_zone_given_offset(board, piece, offsets):
    '''
    Wrapper for king, knight movement zone sets.
    Note, offsets are array of [+x, +y] offsets.
    ''' 
    our_color = piece.color
    movement_tiles = get_tiles_from_offset_pos(pos=piece.pos, offsets=offsets)
    discard_set = set()
    for coord in movement_tiles:
        coord_piece = board.get_piece(pos=coord)
        if coord_piece != None:
            if our_color == coord_piece.color:
                discard_set.add(tuple(coord))
    movement_tiles_set = convert_to_movement_set(movement_tiles)
    return movement_tiles_set.difference(discard_set)

