from piece import Piece


def convert_coord(pos):
    '''
    converts coordinates into python array friendly coordinates for Board
    eg (1, 1) -> (7, 0) or (2, 3) -> (5, 1)
    '''
    return 8-pos[1], pos[0]-1


class Board:
    def __init__(self):
        self.game_board = [[None for x in range(8)] for y in range(8)]  # board with Pieces


    def remove_piece(self, pos) -> Piece:
        '''
        Removes a piece from the board.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        Returns: Removed piece or None if not present.
        Note, this method updates the removed piece position to None.
        Note, this method also removes this piece from said player's collection/pieces.
        '''
        return self.add_or_replace_piece(pos=pos, piece=None)


    def add_or_replace_piece(self, pos, piece: Piece) -> Piece:
        '''
        Adds or replaces an existing piece in the board with piece.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        Returns: Replaced piece or None if not present.
        Note, this method updates the replaced piece position to None if it exists,
        and the added piece position to 'pos'.
        Note, a replaced piece is removed from that player's collection, and
        the added piece's state is updated in that player's collection.
        '''
        x, y = convert_coord(pos)
        replaced = self.game_board[x][y]
        self.game_board[x][y] = piece
        if replaced != None:
            replaced.pos = None
            del replaced.player.pieces[str(replaced)]
        if piece != None:
            piece.player.pieces[str(piece)] = piece
            piece.pos = pos
        return replaced


    def get_piece(self, pos):
        '''
        Gets a piece at pos on the board if it exists. Otherwise returns None.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        return self.game_board[x][y]
    

    def move_piece(self, pos, piece: Piece) -> Piece:
        '''
        We need that piece is not None.
        We assume this move is legal, and that if we replace an existing piece, that replacement is a kill.
        Moves 'piece' to position at pos, and if another piece exists at that pos, we replace it
        with 'piece'. We return that replaced piece, or None otherwise.
        Note, if we kill a piece, the killed piece position updates to None, and our moved piece's position
        updates to pos.
        Note, a killed piece is removed from that player's collection/pieces.
        '''
        if piece == None:
            raise Exception()
        
        taken_piece = self.remove_piece(pos)

        if taken_piece != piece: # sanity check but not required
            raise Exception()
        
        killed_piece = self.add_or_replace_piece(pos, taken_piece)
        return killed_piece


    def __str__(self):
        string = ''
        for i in range(8):
            cur_string = ' '
            for j in range(8):
                cur_piece = self.game_board[i][j]
                if cur_piece == None:
                    cur_string += '[--] '
                else:
                    cur_string += str(cur_piece) + ' '
            cur_string += '\n\n'
            string += cur_string
        return string



