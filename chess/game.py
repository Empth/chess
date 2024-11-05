from player import Player
from board import Board
from debug import Debug
from helpers.general_helpers import algebraic_uniconverter
from helpers.game_helpers import (clear_terminal, get_error_message, get_special_command, set_error_message, set_special_command, 
                          check_winner_king_condition, pos_checker, dest_checker, convert_color_to_player)

'''File contains The Game logic.'''

special_command_set = set(['PAUSE', 'EXIT', 'RESELECT', 'FORFEIT'])

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
                get_error_message(game=self)
                print('\n')
            else:
                print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT')
                print('\n')
            print(str(self.board))
            turn_success = self.make_turn()
            if turn_success: 
                self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'
            winner_found = check_winner_king_condition(game=self)
            if not winner_found:
                clear_terminal()
            if self.exists_command:
                command = get_special_command(game=self)
                if command == 'PAUSE':
                    break
                if command == 'EXIT':
                    self.reset()
                    break
                if command == 'FORFEIT':
                    self.winner = self.p2 if self.turn == 'WHITE' else self.p1
                    break
                if command == 'RESELECT':
                    continue

        if self.winner != None:
            print(str(self.board)) # for kill king to win gameplay
            print(str(self.winner.color)+' has won the game!')


    def make_turn(self) -> bool:
        '''
        Returns True if turn executes successful move, otherwise returns False.
        '''
        pos_example = 'E2 or e2' if self.turn == 'WHITE' else 'E7 or e7'
        dest_example = 'E4 or e4' if self.turn == 'WHITE' else 'E5 or e5'
        pos = input('['+str(self.turn)+"\'S TURN] Select piece\'s position (e.g. "+str(pos_example)+"): ")
        if pos.upper() in special_command_set:
            set_special_command(game=self, command=pos.upper())
            return False
        if not pos_checker(game=self, pos=pos): return False
        pos = pos[0].upper()+pos[1] # to support lowercase
        dest = input('['+str(self.turn)+"\'S TURN] Select the destination for "+
                     str(self.board.get_piece(pos=algebraic_uniconverter(pos)).rank)
                     +" at "+str(pos)+" (e.g. "+str(dest_example)+"): ")
        if dest.upper() in special_command_set:
            set_special_command(game=self, command=dest.upper())
            return False
        if not dest_checker(game=self, pos=pos, dest=dest): return False
        dest = dest[0].upper()+dest[1] # to support lowercase
        # Move of pos -> dest is legal, now make the move
        cur_player = convert_color_to_player(game=self, color=self.turn)
        cur_player.make_move(pos=algebraic_uniconverter(pos[0].upper()+pos[1]), dest=algebraic_uniconverter(dest[0].upper()+dest[1]))
        return True





        
    




