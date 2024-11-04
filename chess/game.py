from player import Player
from board import Board
from debug import Debug
from piece import algebraic_uniconverter
import os

special_command = set(['PAUSE', 'EXIT', 'RESELECT', 'FORFEIT'])

def well_formed(input) -> tuple[bool, str]:
    # Helper checks if pos, dest inputs are well formed
    if type(input) != str:
        return False, 'Input needs to be well-formed!'
    if len(input) != 2:
        return False, 'Input needs to be correctly formatted (e.g. D2)'
    if (input[0].upper() not in set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) or 
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
        self.winner = None # Should be either player 1 or player 2 at win cond
        self.error_message = ''
        self.show_error = False
        self.special_command = ''
        self.exists_command = False


    def reset(self):
        self.__init__()


    def start(self):
        '''
        Starts a new game, or continues an existing game if it was paused.
        '''

        clear_terminal()
        while self.winner == None:
            if self.show_error: 
                self.get_error_message()
                print('\n')
            else:
                print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT (Reselect piece)')
                print('\n')
            print(str(self.board))
            turn_success = self.make_turn()
            if turn_success: 
                self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'
            winner_found = self.check_winner_king_condition()
            if not winner_found:
                clear_terminal()
            if self.exists_command:
                command = self.get_special_command()
                if command == 'PAUSE':
                    break
                if command == 'EXIT':
                    self.reset()
                    break
                if command == 'FORFEIT':
                    self.winner = self.p2 if self.color == 'WHITE' else self.p2
                    break
                if command == 'RESELECT':
                    continue

        if self.winner != None:
            print(str(self.winner.color)+' has won the game!')

    def make_turn(self) -> bool:
        '''
        Returns True if turn executes successful move, otherwise returns False.
        '''
        pos_example = 'E2 or e2' if self.turn == 'WHITE' else 'E7 or e7'
        dest_example = 'E4 or e4' if self.turn == 'WHITE' else 'E5 or e4'
        pos = input('['+str(self.turn)+"\'S TURN] Select piece\'s position (e.g. "+str(pos_example)+"): ")
        if pos.upper() in special_command:
            self.set_special_command(pos.upper())
            return False
        if not self.pos_checker(pos=pos): return False
        pos = pos[0].upper()+pos[1] # to support lowercase
        dest = input('['+str(self.turn)+"\'S TURN] Select the destination for "+
                     str(self.board.get_piece(pos=algebraic_uniconverter(pos)).rank)
                     +" at "+str(pos)+" (e.g. "+str(dest_example)+"): ")
        if dest.upper() in special_command:
            self.set_special_command(dest.upper())
            return False
        if not self.dest_checker(pos=pos, dest=dest): return False
        dest = dest[0].upper()+dest[1] # to support lowercase
        # Move of pos -> dest is legal, now make the move
        cur_player = self.convert_color_to_player(self.turn)
        cur_player.make_move(pos=algebraic_uniconverter(pos[0].upper()+pos[1]), dest=algebraic_uniconverter(dest[0].upper()+dest[1]))
        return True


    def pos_checker(self, pos) -> bool:
        '''
        Helper for turn in picking the right position.
        Also handles the error messages.
        '''
        pos_check, pos_message = well_formed(pos)
        if not pos_check:
            self.set_error_message(pos_message)
            return False
        pos = pos[0].upper()+pos[1]
        if not self.board.piece_exists(algebraic_uniconverter(pos)):
            self.set_error_message('Piece needs to exist at position '+str(pos)+'!')
            return False
        elif self.board.get_piece(algebraic_uniconverter(pos)).color != self.turn:
            self.set_error_message('The ' +str(self.board.get_piece(algebraic_uniconverter(pos)).rank) +' at position '+str(pos)+' is not your own color of '+str(self.turn)+'!')
            return False
        
        return True
    

    def dest_checker(self, pos, dest) -> bool:
        '''
        Helper for turn in picking the right destination, given pos.
        Also handles the error messages.
        '''
        dest_check, dest_message = well_formed(dest)
        if not dest_check:
            self.set_error_message(dest_message)
            return False
        dest = dest[0].upper()+dest[1]
        cur_player = self.convert_color_to_player(color=self.turn)
        move_legal, move_legal_message = cur_player.move_legal(pos=algebraic_uniconverter(pos), 
                                                               dest=algebraic_uniconverter(dest))
        if not move_legal:
            self.set_error_message(move_legal_message)
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
        
    def set_error_message(self, message):
        '''
        Sets error message from error_message, and set error_message on
        '''
        self.error_message = message
        self.show_error = True
    
    def get_error_message(self):
        '''
        Shows error message from error_message, resets error message, and set error_message off
        '''
        print(self.error_message)
        self.error_message = ''
        self.show_error = False

    def set_special_command(self, command):
        '''
        Sets special command from special_command, and set special command detection on
        '''
        self.special_command = command
        self.exists_command = True
    
    def get_special_command(self) -> str:
        '''
        Returns special command from special_command, and resets special command field for game
        and set special command detection off
        '''
        command = self.special_command
        self.special_command = ''
        self.show_error = False
        return command

    
    def check_winner_king_condition(self) -> bool:
        '''
        Checks if a player is missing their king. If so, then the other player is
        declared the winner of the match, by updating winner. At least one player should have their king.
        Boolean is if winner was found (True) or not.
        '''
        p1_has_king = False
        p2_has_king = False
        p1_collection = self.p1.pieces
        p2_collection = self.p2.pieces
        for key in p1_collection:
            if p1_collection[key].rank == 'KING':
                p1_has_king = True
        for key in p2_collection:
            if p2_collection[key].rank == 'KING':
                p2_has_king = True
        assert(p1_has_king or p2_has_king)
        if not p1_has_king:
            self.winner = self.p2
            return True
        if not p2_has_king:
            self.winner = self.p1
            return True
        return False




        
    




