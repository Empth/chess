from player import Player
from board import Board
from debug import Debug
from piece import algebraic_uniconverter
import os

def well_formed(input) -> tuple[bool, str]:
    # Helper checks if pos, dest inputs are well formed
    if type(input) != str:
        return False, 'Input needs to be well-formed!'
    if len(input) != 2:
        return False, 'Input needs to be correctly formatted (e.g. D2)'
    if (input[0] not in set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) or 
        input[1] not in set(['1', '2', '3', '4', '5', '6', '7', '8'])):
        return False, 'Input needs to be correctly formatted (e.g. D2)'
    return True, ''

def clear_terminal():
    '''
    Clears the terminal.
    '''
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

class Game:
    def __init__(self, debug=None):

        '''
        debug: is Debug object for testing. None by default.
        '''

        self.board = Board()
        self.p1 = Player(color='WHITE', board=self.board, debug=debug)
        self.p2 = Player(color='BLACK', board=self.board, debug=debug)
        self.turn = self.p1.color  # 'WHITE' or 'BLACK'
        self.winner = None # Should be either the Player player 1 or player 2 at win cond
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
        clear_terminal()
        while self.winner == None:
            print(str(self.board))
            turn_success = self.make_turn()
            if turn_success: 
                self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'
            clear_terminal()

    def make_turn(self) -> bool:
        '''
        Returns True if turn executes successful move, otherwise returns False.
        '''
        pos_example = 'E2' if self.turn == 'WHITE' else 'E7'
        dest_example = 'E4' if self.turn == 'WHITE' else 'E5'
        pos = input('['+str(self.turn)+"\'S TURN] Select piece\'s position (e.g. "+str(pos_example)+"): ")
        if not self.pos_checker(pos=pos): return False
        dest = input('['+str(self.turn)+"\'S TURN] Select the destination for "+
                     str(self.board.get_piece(pos=algebraic_uniconverter(pos)).rank)
                     +" at "+str(pos)+" (e.g. "+str(dest_example)+"): ")
        if not self.dest_checker(pos=pos, dest=dest): return False
        # Move of pos -> dest is legal, now make the move
        cur_player = self.convert_color_to_player(self.turn)
        cur_player.make_move(pos=algebraic_uniconverter(pos), dest=algebraic_uniconverter(dest))
        return True


    def pos_checker(self, pos) -> bool:
        '''
        Helper for turn in picking the right position.
        Also handles the error messages.
        '''
        pos_check, pos_message = well_formed(pos)
        if not pos_check:
            print(pos_message)
            return False
        if not self.board.piece_exists(algebraic_uniconverter(pos)):
            print('Piece needs to exist at position '+str(pos)+'!')
            return False
        elif self.board.get_piece(algebraic_uniconverter(pos)).color != self.turn:
            print('The piece at position '+str(pos)+' is not your own color of '+str(self.turn)+'!')
            return False
        
        return True
    

    def dest_checker(self, pos, dest) -> bool:
        '''
        Helper for turn in picking the right destination, given pos.
        Also handles the error messages.
        '''
        dest_check, dest_message = well_formed(dest)
        if not dest_check:
            print(dest_message)
            return False
        cur_player = self.convert_color_to_player(color=self.turn)
        move_legal, move_legal_message = cur_player.move_legal(pos=algebraic_uniconverter(pos), 
                                                               dest=algebraic_uniconverter(dest))
        if not move_legal:
            print(move_legal_message)
            return False
        return True
        
    def convert_color_to_player(self, color) -> Player:
        '''
        Helper returns player 1 if color is WHITE, otherwise player 2
        if color is BLACK.
        '''
        assert(color in ['BLACK', 'WHITE'])
        if color == 'WHITE':
            return self.p1
        else:
            return self.p2    



        
    




