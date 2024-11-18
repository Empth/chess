from game import Game
from tests import set_up_debug

if __name__ == "__main__":
    debug=None
    '''
    white_pieces = ['R-A1', 'N-B1', 'B-C1', 'Q-D1', 'K-E1', 'B-F1', 'N-G1', 'R-H1']
    black_pieces = ['R-A8', 'N-B8', 'B-C8', 'Q-D8', 'K-E8', 'B-F8', 'N-G8', 'R-H8']
    debug = set_up_debug(white_pieces=white_pieces, black_pieces=black_pieces)
    '''
    my_game = Game(debug=debug)
    my_game.start()
    