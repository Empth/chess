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


    def remove_piece(self, pos):
        '''
        Removes a piece from the board.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        self.game_board[x][y] = None


    def add_piece(self, pos, piece: Piece):
        '''
        Adds a piece to the board.
        Don't use this to replace pieces.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        if self.game_board[x][y] != None:
            raise Exception("Don't replace pieces with this method.")
        self.game_board[x][y] = piece


    def replace_piece(self, pos, piece: Piece):
        '''
        Replaces an existing piece in the board with piece.
        Don't use this to newly add pieces.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        if self.game_board[x][y] == None:
            raise Exception("Don't add pieces with this method.")
        self.game_board[x][y] = piece

    def get_piece(self, pos):
        '''
        Gets a piece at pos on the board if it exists. Otherwise returns None.
        pos: input format of coordinate (1, 1) (which corresponds to A1)
        '''
        x, y = convert_coord(pos)
        return self.game_board[x][y]


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



