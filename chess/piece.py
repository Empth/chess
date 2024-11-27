from helpers.general_helpers import algebraic_uniconverter, get_piece_visual

class Piece:
    def __init__(self, color: str, rank: str, player, pos=None):
        '''
        is_clone: Whether the piece is a clone of an existing piece or made from scratch.
        '''
        self.color = color # 'WHITE' or 'BLACK'
        self.rank = rank # 'PAWN', 'ROOK', 'QUEEN', etc
        self.pos = pos # is ordered pair from [8]x[8], and [1, 2] <-> A2
        rank_letter = rank[0] if rank != 'KNIGHT' else 'N'
        self.name = rank_letter + '-' + str(algebraic_uniconverter(pos))   # eg white pawn in A2 is P-A2. 
                                                                   # Note King is K-XX, and Knight is N-XX
        self.player = player # refers to the Player which this piece belongs to.
        self.visual = get_piece_visual(rank=self.rank, color=self.color) # ♟
        self.moved = False # True when piece moves; ie changes position from init pos.
        self.pawn_two_leap_on_prev_turn = False # True if this piece if PAWN, it moved on previous turn, and 
                                                # went two squares forward on said previous turn.
    
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
    
    def clone_piece(self, clone_player):
        '''
        Given this piece, returns a deep copy clone of that piece.
        '''
        clone = Piece(color=self.color, rank=self.rank, player=clone_player, pos=self.pos)
        clone.name = self.name
        clone.visual = self.visual
        clone.moved = self.moved
        clone.pawn_two_leap_on_prev_turn = self.pawn_two_leap_on_prev_turn
        return clone