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
                assert(piece.name == code) # sanity check, helped catch a knight is N bug once
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
        legality = self.move_legal(pos=pos, dest=dest)
        if legality[0]:
            self.board.move_piece(pos=dest, piece=self.board.get_piece(pos))
        else:
            print(legality[1])
            return

    def move_legal(self, pos, dest) -> tuple[bool, str]:
        '''
        This checks to see if moving a piece from pos to dest is legal.
        Note, pos, dest are [8]^2 coordinates.
        Returns True, '' or False, error message string.
        '''

        misc_check = self.misc_checks(pos=pos, dest=dest) # helper
        if not misc_check[0]:
            return misc_check
        
        cur_piece = self.board.get_piece(pos=pos)
        assert(cur_piece.pos == pos)
        rank = cur_piece.rank

        if rank == None:
            raise Exception("Piece needs to have rank")
        
        if rank == 'PAWN':
            return self.pawn_move_legal(pos=pos, dest=dest, cur_piece=cur_piece)
        elif rank == 'ROOK':
            return self.rook_move_legal(pos=pos, dest=dest, cur_piece=cur_piece)
                
        return True, 'Placeholder behavior'
    

    def misc_checks(self, pos, dest) -> tuple[bool, str]:
        '''
        Helper for move_legal.
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
        if dest == pos:
            return False, 'Piece cannot stall as a move!'
        
        dest_piece = self.board.get_piece(dest)
        if dest_piece != None:
            if dest_piece.color == cur_piece.color:
                return False, 'Cannot attempt move to a position which already has your colored piece!'
            
        return True, 'Cannot detect any issues with prelim checks'



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
        
        taxicab_distance = taxicab_dist(start=pos, dest=dest)

        if self.pawn_moving_straight_forward(piece=cur_piece, dest=dest):
            if taxicab_distance > 2:
                return False, 'Pawn is moving too far straight'
            if taxicab_distance == 2 and not self.pawn_starting(cur_piece):
                return False, 'Cant move nonstarting pawn 2 units forward'
            
            # Now pawn must be moving either 2 units forward at starting
            # or 1 unit forward generally

            if self.board.get_piece(pos=dest) != None:
                return False, 'Another piece is in dest, so we cant move our pawn forward'
            
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
        

    def rook_move_legal(self, pos, dest, cur_piece) -> tuple[bool, str]:
        '''
        Helper checks if rook move is legal.
        '''
        if dest[0] != pos[0] and dest[1] != pos[1]:
            return False, 'Rook is not moving N/E/S/W!'
        
        # Rook is moving in one of the cardinal directions, North, East, South, or West
        cardinal = cardinal_direction(pos=pos, dest=dest)
        cardinal_collision = self.get_cardinal_collision(pos=pos, cardinal=cardinal)
        if cardinal_collision == None:
            return True, '' # no piece is blocking your direction, you can freely move.
        elif cardinal_collision == dest:
            return True, '' # a piece is the first to block your dest, and from the misc checks, 
                            # it is an opponent piece, so you can capture it.
        else:
            return False, 'A piece is blocking your rook\'s movement!'

    
    def get_cardinal_collision(self, pos, cardinal):
        '''
        Helper for cardinal movement collision.
        For a piece with unlimited cardinal movement, ie rook or queen, returns the position
        of the first piece that something from 'pos' will encounter when moving in 'cardinal' direction.
        Returns None if no such colliding piece exists.
        Required: cardinal is 'N', 'E', 'S', 'W'
        '''

        dictionary = {'N':['y', 1], 'E':['x', 1], 'S':['y', -1], 'W':['x', -1]} # abs_dir, i, sign
        value = dictionary[cardinal]
        abs_dir, sign = value[0], value[1]  # abs_dir: 'x' or 'y'; movement in x dir or y dir;sign differentiates N vs S, E vs W
        i = pos[0] if abs_dir == 'x' else pos[1]

        while True:
            i += sign
            if i-1 not in range(8):
                break
            if abs_dir == 'x':
                if self.board.piece_exists(pos=[i, pos[1]]):
                    return [i, pos[1]]
            else:
                if self.board.piece_exists(pos=[pos[0], i]):
                    return [pos[0], i]
        
        return None