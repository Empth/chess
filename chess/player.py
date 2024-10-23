from piece import Piece, algebraic_uniconverter, convert_letter_to_rank
from board import Board

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


class Player:
    def __init__(self, color: str, board: Board, debug=None):
        self.color = color
        self.pieces = {} # key is Piece name, value is Piece, its a collection of this player's pieces
        self.board = board
        self.collect_pieces(debug=debug) 
        self.set_pieces_on_board()

        
    def collect_pieces(self, debug=None):
        '''
        Builds piece collection and their positions for this player
        '''
        if debug == None:
            assert(self.color == 'WHITE' or self.color == 'BLACK')
            main_row = ['ROOK', 'KNIGHT', 'BISHOP', 'KING', 'QUEEN', 'BISHOP', 'KNIGHT', 'ROOK']
            main_row_pos = 1 if self.color == 'WHITE' else 8
            pawn_row_pos = 2 if self.color == 'WHITE' else 7
            for i in range(8):
                pawn_piece = Piece(color=self.color, rank='PAWN', pos=[i+1, pawn_row_pos], player=self)
                self.pieces[pawn_piece.name] = pawn_piece
                main_piece = Piece(color=self.color, rank=main_row[i], pos=[i+1, main_row_pos], player=self)
                self.pieces[main_piece.name] = main_piece
        elif self.color in debug.board_state:
            player_board_state = debug.board_state[self.color]
            for code in player_board_state:
                piece = Piece(color=self.color, rank=convert_letter_to_rank(code[0]), 
                              pos=algebraic_uniconverter(code[2:]), player=self)
                assert(piece.name == code)
                self.pieces[piece.name] = piece
            


    def set_pieces_on_board(self):
        '''
        Sets this player's pieces on the board, for the start of the game.
        '''
        for piece in self.pieces.values():
            self.board.add_or_replace_piece(pos=piece.pos, piece=piece)


    def make_move(self, pos, dest):
        '''
        This moves a piece at pos to dest if said move is legal.
        Note, pos, dest are [8]^2 coordinates.
        '''
        if self.move_legal(pos=pos, dest=dest)[0]:
            self.board.move_piece(pos=dest, piece=self.board.get_piece(pos))
        else:
            print('Move is not legal!')
            return

    def move_legal(self, pos, dest) -> tuple[bool, str]:
        '''
        This checks to see if moving a piece from pos to dest is legal.
        Note, pos, dest are [8]^2 coordinates.
        Returns True, '' or False, error message string.
        '''
        if not check_in_bounds(pos) or not check_in_bounds(dest):
            return False, 'Given coordinates '+str(pos)+' is out of bounds'
        cur_piece = self.board.get_piece(pos=pos)
        if cur_piece == None:
            return False, 'No piece with position '+str(pos)+' exists'
        if type(cur_piece) != Piece:
            return False, 'Object in pos needs to be piece!'
        if cur_piece.color != self.color:
            return False, 'Color of selected piece doesnt match players color!'

        rank = cur_piece.rank

        if rank == None:
            raise Exception("Piece needs to have rank")
        
        if rank == 'PAWN':
            return self.pawn_move_legal(pos=pos, dest=dest, cur_piece=cur_piece)
                
        return False, 'Misc error'


    def pawn_starting(self, piece):
        '''
        Checks to see if 'piece', which must be a pawn, is in a starting position.
        '''

        if piece.rank != 'PAWN':
            raise Exception("Piece needs to be a pawn")
        
        if piece.color == 'WHITE':
            if piece.pos[1] == 2:
                return True
        elif piece.color == 'BLACK':
            if piece.pos[1] == 7:
                return True
        else:
            raise Exception("Piece needs to have a B/W color")

        return False
    
    def pawn_moving_straight_forward(self, piece, dest):

        '''
        Checks to see if the pawn is moving strictly straight and forward
        '''

        if piece.rank != 'PAWN':
            raise Exception("Piece needs to be a pawn")
        
        if piece.color == 'WHITE':
            if piece.pos[0] == dest[0] and piece.pos[1] < dest[1]:
                return True
        elif piece.color == 'BLACK':
            if piece.pos[0] == dest[0] and piece.pos[1] > dest[1]:
                return True
        else:
            raise Exception("Piece needs to have a B/W color")

        return False
    
    def pawn_moving_diagonal_forward(self, piece, dest):
        '''
        Checks to see if the pawn is moving strictly diagonally forward
        '''

        if piece.rank != 'PAWN':
            raise Exception("Piece needs to be a pawn")
        
        diagonal_check = (abs(piece.pos[0] - dest[0]) == abs(piece.pos[1] - dest[1])) # same x, y distances

        if piece.color == 'WHITE':
            if piece.pos[1] < dest[1] and diagonal_check:
                return True
        elif piece.color == 'BLACK':
            if piece.pos[1] > dest[1] and diagonal_check:
                return True
        else:
            raise Exception("Piece needs to have a B/W color")

        return False
    
    def pawn_move_legal(self, pos, dest, cur_piece) -> tuple[bool, str]:

        '''
        Helper checks if pawn move is legal.
        '''
        if cur_piece.pos != pos:
            return False, 'weird!'+str(cur_piece.pos) +'<- cur piece pos vs pos->' +str(pos)
        
        taxicab_distance = taxicab_dist(start=pos, dest=dest)

        if self.pawn_moving_straight_forward(piece=cur_piece, dest=dest):
            if taxicab_distance > 2:
                return False, 'Pawn is moving too far straight'
            if taxicab_distance == 2 and not self.pawn_starting(cur_piece):
                return False, 'Cant move nonstarting pawn 2 units forward'
            
            # Now pawn must be moving either 2 units forward at starting
            # or 1 unit forward generally

            if self.board.get_piece(pos=dest) != None:
                return False, 'Another pawn is in dest, so we cant move our pawn forward'
            
            return True, '' # We can proceed forward to the forward blank space.
        elif self.pawn_moving_diagonal_forward(piece=cur_piece, dest=dest):
            if taxicab_distance >= 4:
                return False, "Moving pawn too diagonally"
            # Now pawn is 1 unit diagonally forward
            assert(taxicab_distance == 2)
            diag_piece = self.board.get_piece(pos=dest)
            if diag_piece == None:
                return False, 'we can only move pawn diagonally via capture'
            if diag_piece.color == cur_piece.color:
                return False, 'We cant team kill with our pawn'
            # Now we know this is a 1 unit diagonally capture of an opposing piece.
            return True, ''
        else:
            return False, 'Pawn is not moving forward or is not moving straight/diagonal.'
