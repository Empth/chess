
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
        return c_to_a_map[value[0]]+str(value[1])
    
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

class Piece:
    def __init__(self, color: str, rank: str, player, pos=None):
        self.color = color # 'WHITE' or 'BLACK'
        self.rank = rank # 'PAWN', 'ROOK', 'QUEEN', etc
        self.pos = pos # is ordered pair from [8]x[8], and [1, 2] <-> A2
        rank_letter = rank[0] if rank != 'KNIGHT' else 'N'
        self.name = rank_letter + '-' + algebraic_uniconverter(pos)   # eg white pawn in A2 is P-A2. 
                                                                   # Note King is K-XX, and Knight is N-XX
        self.player = player # refers to the Player which this piece belongs to.
        self.visual = get_piece_visual(rank=self.rank, color=self.color)
    
    def __str__(self):
        pos = "None" if self.pos == None else str(self.pos[0]) +', '+str(self.pos[1])
        return ("Name: " + str(self.name) + ", color: " + str(self.color) 
                + ', rank: ' + str(self.rank) + ', position: ' + pos)
    
    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return (self.name == other.name and self.color == other.color 
                and self.rank == other.rank and self.pos == other.pos
                and self.player == other.player)