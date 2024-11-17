from helpers.general_helpers import taxicab_dist, cardinal_direction, ordinal_direction, convert_to_movement_set, get_tiles_from_offset_pos
from helpers.legality_helpers import (pawn_moving_straight_forward, pawn_moving_diagonal_forward, pawn_starting, 
                              get_cardinal_collision, get_ordinal_collision, cardinal_dest_between_collider, 
                              ordinal_dest_between_collider)

'''
Piece legality checker for the 6 ranks of pieces.
'''

def pawn_move_legal(player, pos, dest) -> tuple[bool, str]: # type: ignore

    '''
    Helper checks if pawn move is legal.
    '''

    # TODO refactor this to use logic from 'moved' param of piece for 2 tile movement
    # also need to refactor tests if doing this. 

    cur_piece = player.board.get_piece(pos=pos)
    
    taxicab_distance = taxicab_dist(start=pos, dest=dest)

    if pawn_moving_straight_forward(player=player, piece=cur_piece, dest=dest):
        if taxicab_distance > 2:
            return False, str(player.board.get_piece(pos=pos).rank)+' is moving too far straight!'
        if taxicab_distance == 2 and not pawn_starting(player=player, piece=cur_piece):
            return False, 'Cannot move a nonstarting '+str(player.board.get_piece(pos=pos).rank)+' 2 units forward!'
        
        # Now pawn must be moving either 2 units forward at starting
        # or 1 unit forward generally
        # By extension, pawn is cardinally moving north or south.
        cardinal = cardinal_direction(pos=pos, dest=dest)
        cardinal_collision = get_cardinal_collision(board=player.board, pos=pos, cardinal=cardinal) # None or [x, y]

        if cardinal_collision == None:
            return True, '' # no piece is blocking your direction, you can freely move.
        elif cardinal_dest_between_collider(init_pos=pos, collider_pos=cardinal_collision, dest=dest, cardinal=cardinal, is_pawn=True):
            return True, '' # No piece blocking the direction to your straight destination.
        else:
            return False, 'A piece is blocking your '+str(player.board.get_piece(pos=pos).rank)+'\'s forward movement!'
        
    elif pawn_moving_diagonal_forward(player=player, piece=cur_piece, dest=dest):
        if taxicab_distance >= 4:
            return False, 'Moving '+str(player.board.get_piece(pos=pos).rank)+' too far diagonally!'
        # Now pawn is 1 unit diagonally forward
        assert(taxicab_distance == 2)
        diag_piece = player.board.get_piece(pos=dest)
        if diag_piece == None:
            return False, 'You can only move '+str(player.board.get_piece(pos=pos).rank)+' diagonally via capture!'
        if diag_piece.color == cur_piece.color:
            return False, 'You cannot move to an ally location with your '+str(player.board.get_piece(pos=pos).rank)+'!'
        # Now we know this is a 1 unit diagonally capture of an opposing piece.
        return True, ''
    else:
        return False, str(player.board.get_piece(pos=pos).rank)+' is making an illegal move!'
    

def rook_move_legal(player, pos, dest) -> tuple[bool, str]:
    '''
    Helper checks if rook move is legal.
    '''
    if dest[0] != pos[0] and dest[1] != pos[1]:
        return False, str(player.board.get_piece(pos=pos).rank)+ ' is not moving in a striaght direction!'
    
    # Rook is moving in one of the cardinal directions, North, East, South, or West
    cardinal = cardinal_direction(pos=pos, dest=dest)
    cardinal_collision = get_cardinal_collision(board=player.board, pos=pos, cardinal=cardinal) # None or [x, y]
    if cardinal_collision == None:
        return True, '' # no piece is blocking your direction, you can freely move.
    
    collider_piece = player.board.get_piece(pos=cardinal_collision) # mainly to check no team kill
    team_kill = (dest == cardinal_collision and collider_piece.color == player.color)
    if (cardinal_dest_between_collider(init_pos=pos, collider_pos=cardinal_collision, dest=dest, cardinal=cardinal)
            and not team_kill):
        return True, '' # No piece blocking your direction, or the first piece to block your direction
                        # is one we can go to and capture.
    elif team_kill:
        return False, 'You cannot move to an ally location with your '+str(player.board.get_piece(pos=pos).rank)+'!'
    else: # then a piece is blocking rook's way
        return False, 'A piece is blocking your '+str(player.board.get_piece(pos=pos).rank)+'\'s movement!'


def bishop_move_legal(player, pos, dest) -> tuple[bool, str]:
    '''
    Helper checks if bishop move is legal.
    '''
    if abs(pos[0] - dest[0]) != abs(pos[1] - dest[1]):
        return False, str(player.board.get_piece(pos=pos).rank)+ ' is not moving in a diagonal direction!'
    
    # Bishop is now moving in one of the ordinal directions, NE/SE/SW/NW.
    ordinal = ordinal_direction(pos=pos, dest=dest)
    ordinal_collision = get_ordinal_collision(board=player.board, pos=pos, ordinal=ordinal)
    if ordinal_collision == None:
        return True, '' # No piece is blocking your direction, you can freely move
    collider_piece = player.board.get_piece(pos=ordinal_collision) # mainly to check no team kill
    team_kill = (dest == ordinal_collision and collider_piece.color == player.color)
    if (ordinal_dest_between_collider(init_pos=pos, collider_pos=ordinal_collision, dest=dest, ordinal=ordinal)
        and not team_kill):
        return True, '' # No piece blocking your direction, or the first piece to block your direction
                        # is one we can go to and capture.
    elif team_kill:
        return False, 'You cannot move to an ally location with your '+str(player.board.get_piece(pos=pos).rank)+'!'
    else: # then a piece is blocking bishop's way
        return False, 'A piece is blocking your '+str(player.board.get_piece(pos=pos).rank)+'\'s movement!'
    

def knight_move_legal(player, pos, dest) -> tuple[bool, str]:
    '''
    Helper checks if knight move is legal.
    '''
    offsets = [[1, 2], [2, 1], [-1, 2], [2, -1], [1, -2], [-2, 1], [-1, -2], [-2, -1]]
    return non_collisional_piece_move_legal(player=player, pos=pos, dest=dest, offsets=offsets)


def queen_move_legal(player, pos, dest) -> tuple[bool, str]:
    '''
    Helper checks if queen move is legal.
    '''

    cardinal = (dest[0] == pos[0] or dest[1] == pos[1])
    ordinal = (abs(pos[0] - dest[0]) == abs(pos[1] - dest[1]))
    if not cardinal and not ordinal:
        return False, 'Queen is not moving straight or diagonally!'
    
    assert(cardinal != ordinal)
    
    valid = True
    message = ''
    if cardinal:
        valid, message = rook_move_legal(player=player, pos=pos, dest=dest)
    if ordinal:
        valid, message = bishop_move_legal(player=player, pos=pos, dest=dest)

    return valid, message


def king_move_legal(player, pos, dest) -> tuple[bool, str]:
    '''
    Helper checks if king move is legal.
    '''
    offsets = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
    return non_collisional_piece_move_legal(player=player, pos=pos, dest=dest, offsets=offsets)


def non_collisional_piece_move_legal(player, pos, dest, offsets) -> tuple[bool, str]:
    '''
    Movement legality check for noncollisional movers, which are just king and knight.
    Offsets is a list of [+x, +y] offsets corresponding to movement types ie knight is [+1, +2],
    king is [+1, +1] or [+1, +0].
    Like other piece move checkers, returns legality bool, error message string.
    '''

    if (tuple(dest) in convert_to_movement_set(get_tiles_from_offset_pos(pos=pos, 
                                                                          offsets=offsets))):
        dest_piece = player.board.get_piece(pos=dest)
        if dest_piece == None:
            return True, '' # empty space
        elif dest_piece.color == player.color:
            return False, 'You cannot move to an ally location with your '+str(player.board.get_piece(pos=pos).rank)+'!'
        else:
            return True, '' # enemy capture
    else:
        return False, 'This is not a valid '+str(player.board.get_piece(pos=pos).rank)+' move!'