from helpers.legality_helpers import get_cardinal_collision

'''
Functions for retrieving the movement zones of all 6 ranks of pieces.
The return type for these functions will be an array of [x, y], these 
represent the movement zone of the piece.
'''
def get_movement_zone(board, piece):
    '''
    Gets movement zone of given piece, which is an array of [x, y] which piece
    can move to.
    '''
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
    return []

def rook_movement_zone(board, piece):
    '''
    Returns movement zone of given rook piece.
    '''
    assert(piece.rank == 'ROOK')
    cardinals = ['N', 'E', 'S', 'W']
    for dir in cardinals:
        cardinal_collision = get_cardinal_collision(board=board, pos=piece.pos, cardinal=dir)
    return []

def bishop_movement_zone(board, piece):
    '''
    Returns movement zone of given bishop piece.
    '''
    assert(piece.rank == 'BISHOP')
    return []

def queen_movement_zone(board, piece):
    '''
    Returns movement zone of given queen piece.
    '''
    assert(piece.rank == 'QUEEN')
    return []

def knight_movement_zone(board, piece):
    '''
    Returns movement zone of given knight piece.
    '''
    assert(piece.rank == 'KNIGHT')
    return []

def king_movement_zone(board, piece):
    '''
    Returns movement zone of given king piece.
    '''
    assert(piece.rank == 'KING')
    return []