from piece import Piece, algebraic_uniconverter, convert_letter_to_rank
from board import Board


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
                pawn_piece = Piece(color=self.color, rank='PAWN', pos=(i+1, pawn_row_pos), player=self)
                self.pieces[pawn_piece.name] = pawn_piece
                main_piece = Piece(color=self.color, rank=main_row[i], pos=(i+1, main_row_pos), player=self)
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
        This moves a piece at pos to dest, if said move is legal.
        Note, pos, dest are [8]^2 coordinates.
        '''
        if not self.move_legal(pos, dest):
            return
        
        if self.board.get_piece(pos) == None:
            return

    def move_legal(self, pos, dest) -> bool:
        '''
        This checks to see if moving a piece from pos to dest is legal.
        Note, pos, dest are [8]^2 coordinates.
        '''
        return True
