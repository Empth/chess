from player import Player
from board import Board
from debug import Debug
from helpers.general_helpers import algebraic_uniconverter, swap_colors
from helpers.game_helpers import (clear_terminal, get_error_message, get_special_command, set_error_message, set_special_command, 
                          get_color_in_check, pos_checker, dest_checker, convert_color_to_player)
from helpers.state_helpers import update_players_check, move_puts_player_in_check, move_locks_opponent
from misc.constants import *

'''File contains The Game logic.'''

special_command_set = set(['PAUSE', 'EXIT', 'RESELECT', 'FORFEIT'])
mate_special_command_set = set(['checkmate', 'stalemate'])

class Game:
    def __init__(self, debug=None):

        '''
        debug: is Debug object for testing. None by default.
        '''

        self.board = Board()
        self.p1 = Player(color=WHITE, board=self.board, debug=debug)
        self.p2 = Player(color=BLACK, board=self.board, debug=debug)
        self.turn = self.p1.color  # 'WHITE' or 'BLACK'
        self.winner = None # Should be either 'WHITE', 'BLACK', or 'DRAW'
        self.error_message = ''
        self.show_error = False
        self.special_command = ''
        self.exists_command = False
        self.game_clone = None


    def reset(self):
        self.__init__()


    def start(self):
        '''
        Starts a new game, or continues an existing game if it was paused.
        '''

        clear_terminal()
        while self.winner == None:
            print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT')
            if self.show_error: 
                get_error_message(game=self)
            else:
                print('\n')
            color_in_check = get_color_in_check(self)
            print(str(self.board))
            if color_in_check in BWSET: # some player is in check
                print(str(color_in_check)+' is in check!\n')
            else:
                print('No player is in check.\n')
            turn_success = self.make_turn()
            win_con = (self.special_command in mate_special_command_set) 
            # ^ probably bad to not use the getter... but I don't want special_cmd reset
            if turn_success and not win_con:
                # ie mate_special... means not checkmate or stalemate.
                self.turn = swap_colors(self.turn) # swaps turn to the next color.

            '''
            # comment this out for now in favor of checkmate win condition
            winner_found = check_winner_king_condition(game=self)
            if not winner_found:
                clear_terminal()
            '''
            if self.exists_command:
                command = get_special_command(game=self)
                if command == 'checkmate':
                    self.winner = self.turn
                    break
                if command == 'stalemate':
                    set_special_command(self, "stalemate")
                    self.winner = 'DRAW'
                    break
                if command == 'PAUSE':
                    break # TODO not implemented
                if command == 'EXIT':
                    self.reset()
                    clear_terminal()
                    return
                if command == 'FORFEIT':
                    self.winner = swap_colors(self.turn) # as opposing player color wins
                    set_special_command(self, "forfeited") # hack for forfeit win message
                    break
                if command == 'RESELECT':
                    clear_terminal()
                    continue

            clear_terminal()
            # and loop repeats


        clear_terminal() # clear terminal at end

        print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT') # boilerplate again
        print('\n')
        if self.winner != None:
            print(str(self.board)) # Present the final board
            if self.winner == 'DRAW':
                print('Game has ended in a draw through '+str(get_special_command(game=self))) 
                # assumes get special command was set above as stalemate.
            elif get_special_command(self) == 'forfeited':
                forfeiter = swap_colors(self.winner)
                print(str(forfeiter) +' forfeits. '+ str(self.winner)+' wins!')
            else:
                print('Checkmate! '+str(self.winner)+' wins!')


    def make_turn(self) -> bool:
        '''
        Method executes the move if its fully legal (in movement zone, and not leaving the movementer in check)
        and after move executation, will update the check status. Also, deals with checkmate/stalemate conditions, and 
        deals with complaining after an illegal move.
        Returns True if turn executes successful move (move legal and not moving into check), otherwise returns False.
        '''
        pos_example = 'E2 or e2' if self.turn == WHITE else 'E7 or e7'
        dest_example = 'E4 or e4' if self.turn == WHITE else 'E5 or e5'
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
        # So we see pos -> dest is in the movement zone.
        cur_player_color = self.turn
        cur_player = convert_color_to_player(game=self, color=cur_player_color)
        opponent_color = swap_colors(self.turn)
        opponent = convert_color_to_player(game=self, color=opponent_color)

        # Now, we update pos, dest into [x, y] form instead of string.
        pos, dest = algebraic_uniconverter(pos[0].upper()+pos[1]), algebraic_uniconverter(dest[0].upper()+dest[1])

        cur_piece = self.board.get_piece(pos)
        assert(cur_piece != None)

        # Now checking if pos -> dest places said movementer's king in check
        # (and thus would be invalid). Perfect time to use __clone_game!
        puts_cur_player_in_check = move_puts_player_in_check(game=self, 
                                                             pos=pos, 
                                                             dest=dest) # only modifies self's game_clone param.
        if puts_cur_player_in_check:
            if cur_player.in_check:
                if cur_piece.rank == 'KING': # our move into check move is moving king, while king is already in check
                    set_error_message(game=self, message='This move is not legal as your KING would still be in check!')
                else:
                    set_error_message(game=self, message='This move is not legal as it leaves your KING in check!')
            else:
                set_error_message(game=self, message='This move is not legal as it puts your KING into check!')
            return False
        
        # Now we check to see if this pos->dest move places the opponent into checkmate or stalemate,
        # in that all of the opponent's subsequent possible moves leads to their king's capture.

        locks_opponent = move_locks_opponent(game=self, pos=pos, dest=dest)
        if locks_opponent:
            # now need to check if this lock leads to checkmate or stalemate.
            # its okay to make pos->dest move now since the game is basically over.
            cur_player.make_move(pos, dest)
            update_players_check(game=self)
            if opponent.in_check:
                # setting nonuppercased special commands is a hack to overload the win/draw conditions
                # into these existing special command methods.
                set_special_command(game=self, command='checkmate')
                return True
            else:
                set_special_command(game=self, command='stalemate')
                return True
        
        # Move of pos -> dest is fully legal (albeit doesn't terminate the game), now make the move
        cur_player.make_move(pos, dest)
        update_players_check(game=self)
        return True
    

    def clone_game(self):
        '''
        Creates an seperate deep copy of this game instance, and has game_clone param point to
        the deep copy. In the game clone, any modification of player, board, piece state 
        should not effect the state of this current game.
        This method should not be used outside of internal logic, ie in_check methods and tree search. 
        '''
        clone = Game()
        clone.board = Board()
        clone.p1 = self.p1.clone_player(board=clone.board) # note, this will also update clone.board's state to have this
                                                            # player's pieces, not just return a player 1 deep clone.
                                                            # Blame the Player <-> Piece <-> Board spaghetti.
        clone.p2 = self.p2.clone_player(board=clone.board) # ^ same for p2
        clone.turn = self.turn
        clone.winner = self.winner # now its okay sine its not a player
        # We don't store any other information about error message state, or special command state.
        self.game_clone = clone





        
    




