from piece import Piece
from board import Board
from move_legal import pawn_move_legal, rook_move_legal, bishop_move_legal, knight_move_legal, queen_move_legal, king_move_legal
from helpers.state_helpers import pawn_promotion
from helpers.general_helpers import check_in_bounds, algebraic_uniconverter, convert_letter_to_rank

'''
Player who gets to make chess moves.
'''

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
            main_row = ['ROOK', 'KNIGHT', 'BISHOP', 'QUEEN', 'KING', 'BISHOP', 'KNIGHT', 'ROOK']
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
        legality, message = self.move_legal(pos=pos, dest=dest)
        if legality:
            moving_piece = self.board.get_piece(pos)
            self.board.move_piece(pos=dest, piece=moving_piece)
            pawn_promotion(player=self, dest=dest, piece=moving_piece)
        else:
            print(message)
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
        
        # Note no teamkill is delegated by X_move_legal functions, to have error messages make sense
        
        if rank == 'PAWN':
            return pawn_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'ROOK':
            return rook_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'BISHOP':
            return bishop_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KNIGHT':
            return knight_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'QUEEN':
            return queen_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KING':
            return king_move_legal(player=self, pos=pos, dest=dest)
                
        return False, 'Rank of piece at position ' +str(algebraic_uniconverter(pos))+ ' does not match any of the 6 classes.'
    

    def misc_checks(self, pos, dest) -> tuple[bool, str]:
        '''
        Helper for move_legal.
        '''

        if not check_in_bounds(pos) or not check_in_bounds(dest):
            return False, 'Given coordinates '+str(pos)+' is out of bounds' # unreachable?
        cur_piece = self.board.get_piece(pos=pos)
        if cur_piece == None:
            return False, 'No piece at position '+str(algebraic_uniconverter(pos))+' exists'
        if type(cur_piece) != Piece:
            return False, 'Object at '+str(algebraic_uniconverter(pos))+' needs to be a piece!' # probably unreachable
        if cur_piece.color != self.color:
            return False, 'Color of selected piece doesnt match players color of '+str(self.color)+'!'
        if dest == pos:
            return False, 'Piece cannot stall as a move!'
            
        return True, 'Cannot detect any issues with prelim checks'
    

    def bool_move_legal(self, pos, dest) -> bool:
        '''
        Returns boolean value of move_legal's tuple output.
        Mainly for use when testing truth values of move legality.
        '''
        return self.move_legal(pos=pos, dest=dest)[0]