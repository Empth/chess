from misc.constants import *

class Debug:
    def __init__(self, board_state={}, turn_state=None):
        '''
        Debug object containing misc info for testing

        board_state: dictionary of keys 'BLACK' or 'WHITE' pointing to array indicating color's
        corresponding piece name codes and initial position, eg K-A5 in board_state['BLACK'] corresponds to
        black's king in position A5. Empty array/no key means no pieces for said color.

        turn_state: which color starts first (1 or 2)
        '''

        for key in board_state:
            assert(key in BWSET)

        self.board_state = board_state
        self.turn_state = turn_state
