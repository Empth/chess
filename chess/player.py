from piece import Piece
from board import Board

class Player:
    def __init__(self, color: str, board: Board):
        self.color = color
        self.pieces = {} # key is Piece name, value is Piece, its a collection of this player's pieces
        self.board = board
        self.collect_pieces() 
        self.set_pieces_on_board()
        
    def collect_pieces(self):
        '''
        Builds piece collection and their positions for this player
        '''
        assert(self.color == 'WHITE' or self.color == 'BLACK')
        main_row = ['ROOK', 'KNIGHT', 'BISHOP', 'KING', 'QUEEN', 'BISHOP', 'KNIGHT', 'ROOK']
        main_row_pos = 1 if self.color == 'WHITE' else 8
        pawn_row_pos = 2 if self.color == 'WHITE' else 7
        for i in range(8):
            pawn_piece = Piece(color=self.color, rank='PAWN', pos=(i+1, pawn_row_pos))
            self.pieces[pawn_piece.name] = pawn_piece
            main_piece = Piece(color=self.color, rank=main_row[i], pos=(i+1, main_row_pos))
            self.pieces[main_piece.name] = main_piece

    def set_pieces_on_board(self):
        '''
        Sets this player's pieces on the board, for the start of the game.
        '''
        for piece in self.pieces.values():
            self.board.add_piece(pos=piece.pos, piece=piece)
