from player import Player
from board import Board
from debug import Debug

class Game:
    def __init__(self, debug=None):

        '''
        debug: is Debug object for testing. None by default.
        '''

        self.board = Board()
        self.p1 = Player(color='WHITE', board=self.board, debug=debug)
        self.p2 = Player(color='BLACK', board=self.board, debug=debug)
        self.turn = 'WHITE' # 'WHITE' or 'BLACK'
        '''
        print(str(self.board))
        pawn_1 = self.board.get_piece(pos=(1, 2))
        print(self.p1.pieces[pawn_1.name].pos)
        self.board.remove_piece(pos=(1, 2))
        self.board.add_or_replace_piece(pos=(1, 4), piece=pawn_1)
        self.p1.pieces[pawn_1.name].pos = (1, 4)
        print(self.board)
        print(self.p1.pieces[pawn_1.name].pos)
        '''

    def start(self):
        print('hit')



