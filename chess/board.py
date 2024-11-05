from piece import Piece
from helpers.general_helpers import convert_coord

'''Chess board and also primitive piece crud add/remove logic on board'''

class Board:
    def __init__(self):
        self.game_board = [[None for x in range(8)] for y in range(8)]  # board with Pieces


    def remove_piece(self, pos) -> Piece | None:
        '''
        Removes a piece from the board.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        Returns: Removed piece or None if not present.
        Note, this method updates the removed piece position to None.
        Note, this method also removes this piece from said player's collection/pieces.
        '''
        return self.add_or_replace_piece(pos=pos, piece=None)


    def add_or_replace_piece(self, pos, piece: Piece | None) -> Piece | None:
        '''
        Adds or replaces an existing piece in the board with piece.

        pos: input format of coordinate (1, 1) (which corresponds to A1)
        piece: piece which we wish to add or already exists and want to place in pos.
        
        Requires: If piece's name already exists in this player's collection, then 'piece'
        must be the same as that named piece in that player's collection. 

        Modifies: Player(s) collection of pieces, current pieces in a collection if 'piece'
        exists, we modify the piece's position so that duplicates are not possible.
        We also get rid of piece on the board so dupes aren't possible.

        Returns: Replaced piece or None if not present.

        Note, this method updates the replaced piece position to None if it exists,
        and the added piece position to 'pos'.
        Note, a replaced piece is removed from that player's collection, and
        the added piece's state is updated in that player's collection.
        '''
        x, y = convert_coord(pos)
        replaced = self.game_board[x][y]
        self.game_board[x][y] = piece
        if piece != None:
            if piece.name in piece.player.pieces:
                if piece != piece.player.pieces[piece.name]:
                    raise Exception('Pieces with the same name from same player should correspond to the same piece')
                if pos != piece.pos:
                    old_x, old_y = convert_coord(piece.pos)
                    self.game_board[old_x][old_y] = None
            piece.player.pieces[piece.name] = piece
            piece.pos = pos
        if replaced != None:
            replaced.pos = None
            del replaced.player.pieces[replaced.name]
        return replaced


    def get_piece(self, pos) -> Piece:
        '''
        Gets a piece at pos on the board if it exists. Otherwise returns None.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        return self.game_board[x][y]
    
    def piece_exists(self, pos) -> bool:
        '''
        Returns boolean of wheather piece exists at position pos.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        return self.get_piece(pos=pos) != None
    

    def move_piece(self, pos, piece: Piece) -> Piece | None:
        '''
        We need that piece is not None.
        Next, we need that 'piece' actually exists in the player's collection, and is identical to its name code 
        in the collection. 
        We assume this move is legal, and that if we replace an existing piece, that replacement is a kill.
        Moves 'piece' to position at pos, and if another piece exists at that pos, we replace it
        with 'piece'. We return that replaced piece, or None otherwise.
        Note, if we kill a piece, the killed piece position updates to None, and our moved piece's position
        updates to pos.
        Note, a killed piece is removed from that player's collection/pieces.
        '''
        if piece == None:
            raise Exception("Piece to be moved can't be None.")
        
        killed_piece = self.add_or_replace_piece(pos, piece)
        return killed_piece


    def __str__(self):
        c_map = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}
        string = ''
        for i in range(8):
            cur_string = str(8-i)+'  '
            for j in range(8):
                cur_piece = self.game_board[i][j]
                if cur_piece == None:
                    checkerboard_color = (i + j) % 2
                    if checkerboard_color == 0: 
                        cur_string += '[--] '
                    else:
                        cur_string += '[  ] '
                else:
                    cur_string += '[' + cur_piece.visual + ' ] '
            cur_string += '\n\n'
            string += cur_string
        string += '    Aa   Bb   Cc   Dd   Ee   Ff   Gg   Hh   \n\n'
        return string



