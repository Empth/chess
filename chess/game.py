from player import Player
from board import Board
class Game:
    def __init__(self):
        self.board = Board()
        self.p1 = Player(color='WHITE', board=self.board)
        self.p2 = Player(color='BLACK', board=self.board)
        self.turn = 1 # 1 or 2
        print(str(self.board))
        pawn_1 = self.board.get_piece(pos=(1, 2))
        print(self.p1.pieces[pawn_1.name].pos)
        self.board.remove_piece(pos=(1, 2))
        self.board.add_piece(pos=(1, 4), piece=pawn_1)
        self.p1.pieces[pawn_1.name].pos = (1, 4)
        print(self.board)
        print(self.p1.pieces[pawn_1.name].pos)

    def start(self):
        print('hit')



