

def algebraic_converter(pos):
    '''
    converts algebraic notation into coordinate notation ala A1 -> (1, 1)
    '''
    map = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}
    return map[pos[0]]+str(pos[1])

class Piece:
    def __init__(self, color: str, rank: str, pos=None):
        self.color = color
        self.rank = rank # 'PAWN', 'ROOK', 'QUEEN', etc
        self.pos = pos # is ordered pair from [8]x[8], and (1, 2) <-> A2
        rank_letter = rank[0] if rank[0] != 'KNIGHT' else 'N'
        self.name = rank_letter + '-' + algebraic_converter(pos)   # eg white pawn in A2 is P-A2. 
                                                                        # Note King is K-XX, and Knight is N-XX
    
    def __str__(self):
        return self.name