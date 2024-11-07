'''
General helper functions for positional math, will generally not require Player state.
'''

def taxicab_dist(start, dest):

    '''
    Finds the taxicab tile distance from position start to dest.
    '''

    return abs(start[0]-dest[0])+abs(start[1]-dest[1])

def check_in_bounds(coord):
    '''
    Checks to see if coordinates are in bounds, ie they're in 1,...,8
    '''
    return coord[0]-1 in range(8) and coord[1]-1 in range(8)

def cardinal_direction(pos, dest) -> str:
    '''
    Helper returns 'N'/ 'E' / 'S' / 'W' direction of pos -> dest
    Required: pos, dest are horizontally or vertically aligned, but not equal. 
    '''
    assert(pos != dest)
    assert(pos[0] == dest[0] or pos[1] == dest[1])

    if pos[0] == dest[0]: # vertically aligned
        if pos[1] < dest[1]:
            return 'N'
        else:
            return 'S'
    else: # horizontally aligned
        if pos[0] < dest[0]:
            return 'E'
        else:
            return 'W'

def ordinal_direction(pos, dest) -> str:
    '''
    Helper returns the ordinal direction 'NE', 'SE', 'SW', 'NW' from pos->dest
    Required: pos -> dest is diagonal, and pos != dest
    '''
    assert(pos != dest)
    assert(abs(pos[0] - dest[0]) == abs(pos[1] - dest[1]))

    dir = ''

    if dest[1] > pos[1]: # moving north
        dir += 'N'
    else: # moving south
        dir += 'S'

    if dest[0] > pos[0]: # moving east
        dir += 'E'
    else: # moving west
        dir += 'W'

    return dir

def convert_coord(pos):
    '''
    converts coordinates into python array friendly coordinates for Board
    eg (1, 1) -> (7, 0) or (2, 3) -> (5, 1)
    '''
    return 8-pos[1], pos[0]-1

def algebraic_uniconverter(value):
    '''
    converts algebraic notation into coordinate notation ala A1 -> (1, 1)
    or vice versa ala (3, 1) -> C1.
    Complains with Exception if inputs are ill posed. 
    '''
    c_to_a_map = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}
    a_to_c_map = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}

    if type(value) != str:
        if len(value) != 2:
            raise Exception()
        elif value[0]-1 not in range(8) or value[1]-1 not in range(8):
            raise Exception()
    else:
        if value[0] not in a_to_c_map.keys() or int(value[1])-1 not in range(8):
            raise Exception()
        
    if type(value) == str:
        return [a_to_c_map[value[0]], int(value[1])]
    else:
        return c_to_a_map[int(value[0])]+str(value[1])
    
def convert_letter_to_rank(letter):
    '''
    converts letter to rank, ie 'N' -> 'KNIGHT' or 'K' -> 'KING'
    '''
    converter = {'P': 'PAWN', 'R': 'ROOK', 'N': 'KNIGHT', 'B': 'BISHOP', 'K': 'KING', 'Q': 'QUEEN'}
    return converter[letter]

def get_piece_visual(rank, color):
    white_map = {'PAWN':'♟', 'ROOK':'♜', 'KNIGHT':'♞', 'BISHOP':'♝', 'QUEEN':'♛', 'KING':'♚'}
    black_map = {'PAWN':'♙', 'ROOK':'♖', 'KNIGHT':'♘', 'BISHOP':'♗', 'QUEEN':'♕', 'KING':'♔'}
    assert(color in ['BLACK', 'WHITE'])
    if color == 'WHITE':
        return white_map[rank]
    else:
        return black_map[rank]
    
def convert_to_movement_set(arr):
    '''
    Takes an array of arrays and returns it as a set of tuples.
    Mainly for movement zone.
    '''
    output = set()
    for sub_arr in arr:
        output.add(tuple(sub_arr))
    return output

def get_tiles_from_offset_pos(pos, offsets):
    '''
    Calculation logic to pass onto non_collisional_piece_move_legal, and king, knight movement zone methods.
    Returns an array of all in range [x, y] given position and list of offsets.
    Note, this does not account for tiles with same color as pos piece, which are not excluded from this output.
    Those must be handled by the caller.
    '''
    movement_tiles = []
    x, y = pos[0], pos[1]
    for offset in offsets:
        new_x, new_y = x+offset[0], y+offset[1]
        if new_x-1 not in range(8) or new_y-1 not in range(8):
            continue
        movement_tiles.append([new_x, new_y])
            
    return movement_tiles
