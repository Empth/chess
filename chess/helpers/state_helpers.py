from .general_helpers import get_piece_visual

'''
For things like pawn promotion status, piece has moved, king in check, etc
'''

def pawn_promotion(player, dest, piece):
    '''Given a piece that moved to dest, checks whether it is a pawn that reached its "end",
    in which case we promote it to QUEEN. Otherwise, does nothing.'''
    # TODO Implement underpromotion to lower than queen 
    end = 8 if player.color == 'WHITE' else 1
    if piece.rank == 'PAWN' and dest[1] == end:
        piece.rank = 'QUEEN'
        piece.visual = get_piece_visual(rank=piece.rank, color=piece.color)

def update_moved_piece(piece):
    '''
    If a piece has never moved, and has made a move, this function is called to update the piece's
    moved param to True.
    '''
    if not piece.moved:
        piece.moved = True