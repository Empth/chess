import random
from player import Player
from board import Board
from debug import Debug
from helpers.general_helpers import algebraic_uniconverter, swap_colors
from helpers.game_helpers import (clear_terminal, get_error_message, get_special_command, set_error_message, set_special_command, 
                          get_color_in_check, pos_checker, dest_checker, convert_color_to_player)
from helpers.state_helpers import update_players_check, move_puts_player_in_check, move_locks_opponent
from movement_zone import get_movement_zone
from misc.constants import *

'''File contains The Game logic.'''

special_command_set = set(['PAUSE', 'EXIT', 'RESELECT', 'FORFEIT', 'RANDOM', 'R', 'KC', 'QC'])
mate_special_command_set = set(['checkmate', 'stalemate'])

class Game:
    def __init__(self, debug=None):

        '''
        debug: is Debug object for testing. None by default.
        '''

        self.board = Board()
        self.p1 = Player(color=WHITE, board=self.board, game=self, debug=debug)
        self.p2 = Player(color=BLACK, board=self.board, game=self, debug=debug)
        self.turn = self.p1.color  # 'WHITE' or 'BLACK'
        self.winner = None # Should be either 'WHITE', 'BLACK', or 'DRAW'
        self.error_message = ''
        self.show_error = False
        self.special_command = ''
        self.exists_command = False
        self.game_clone = None


    def reset(self):
        '''
        Resets game state to a blank slate.
        '''
        self.__init__()


    def render(self, render_below_board=True):
        '''
        Renders the game visuals, minus input text which must be handled outside.
        All previous rendered visuals in the terminal are erased.
        In order: Special Command shortcut list, error message slot, board, 
        (and optionally) in_check message slot, based off if render below_board is True
        render_below_board: If we render in_check below board.
        '''
        clear_terminal()
        print('Special commands: PAUSE, EXIT, FORFEIT, RESELECT, RANDOM (or R), QC or KC (to castle)')
        if self.show_error: 
            get_error_message(game=self)
        else:
            print('\n')
        print(str(self.board))
        if render_below_board:
            color_in_check = get_color_in_check(self)
            if color_in_check in BWSET: # some player is in check
                print(str(color_in_check)+' is in check!\n')
            else:
                print('No player is in check.\n')


    def start(self):
        '''
        Starts a new game, or continues an existing game if it was paused. TODO I didn't implement pause
        '''

        while self.winner == None:
            self.render()
            if not self.exists_command: # FIXME Big antipattern adding this on, it exists to pivot to checkmate branch from random() checkmate, but it sucks...
                # FIXME Everything in game.py needs refactoring!
                turn_success = self.make_turn()

            if self.exists_command:
                command = get_special_command(game=self)
                if command == 'checkmate':
                    self.winner = swap_colors(self.turn) 
                    # ^ Need this because color swapping is default handled by player move functions
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
                if command == 'RANDOM' or command == 'R':
                    self.make_random_move()
                    continue
                if command == 'KC' or command == 'QC':
                    side = 'KING' if command[0] == 'K' else 'QUEEN'
                    self.make_castle_move(side=side)


        if self.winner != None:
            self.render(render_below_board=False)
            if self.winner == 'DRAW':
                print('Game has ended in a draw through '+str(get_special_command(game=self))+'.\n') 
                # assumes get special command was set above as stalemate.
            elif get_special_command(self) == 'forfeited':
                forfeiter = swap_colors(self.winner)
                print(str(forfeiter) +' forfeits. '+ str(self.winner)+' wins!\n')
            else:
                print('Checkmate! '+str(self.winner)+' wins!\n')


    def make_turn(self, executing_move=None) -> bool:
        '''
        Method executes the move if its fully legal (in movement zone, and not leaving the movementer in check)
        and after move executation, will update the check status. Also, deals with checkmate/stalemate conditions, and 
        deals with complaining after an illegal move.
        Returns True if turn executes successful move (move legal and not moving into check), otherwise returns False.
        executing_move: [[x_0, y_0], [x_1, y_1]] which tells make_turn to execute x_0, y_0 -> x_1, y_1 
        as a move. Said move MUST be movement zone legal (ie found in movement zones, check notwithstanding).
        Is None otherwise if player move is derived from user input.
        '''
        pos, dest = [], [] # temp
        if executing_move == None:
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

            # Now, we update pos, dest into [x, y] form instead of string.
            pos, dest = algebraic_uniconverter(pos[0].upper()+pos[1]), algebraic_uniconverter(dest[0].upper()+dest[1])
        else:
            pos, dest = executing_move[0], executing_move[1] # ie move is given by some nonuser agent.

        # So we see pos -> dest is in the movement zone.
        cur_player_color = self.turn
        cur_player = convert_color_to_player(game=self, color=cur_player_color)
        opponent_color = swap_colors(self.turn)
        opponent = convert_color_to_player(game=self, color=opponent_color)

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

        locks_opponent = move_locks_opponent(game=self, pos=pos, dest=dest) # TODO make into its own method
        if locks_opponent: 
            # now need to check if this lock leads to checkmate or stalemate.
            # its okay to make pos->dest move now since the game is basically over.
            cur_player.make_move(pos, dest)
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
        return True
    
    def make_castle_move(self, side) -> bool:
        '''
        Like make_turn, but for castling on 'side' and doesn't ask for user input. 
        Will return True and execute if the 'side' castle is legal for the current player's turn,
        otherwise will return False and throw the appropriate error message.
        side: 'KING' or 'QUEEN'
        '''
        cur_player_color = self.turn
        cur_player = convert_color_to_player(game=self, color=cur_player_color)
        opponent_color = swap_colors(self.turn)
        opponent = convert_color_to_player(game=self, color=opponent_color)
        castle_legal, error_message = cur_player.castle_legal(side, opponent)
        if not castle_legal:
            set_error_message(game=self, message=error_message)
            return False
        # castle on this side is legal. Perform the castle.
        # Case to check if this leads to checkmate or stalemate # TODO make into its own method
        locks_opponent = move_locks_opponent(game=self, castle_side_color = [side, cur_player.color])
        if locks_opponent:
            # now need to check if this lock leads to checkmate or stalemate.
            # its okay to make pos->dest move now since the game is basically over.
            cur_player.castle(side, opponent)
            if opponent.in_check:
                # setting nonuppercased special commands is a hack to overload the win/draw conditions
                # into these existing special command methods.
                set_special_command(game=self, command='checkmate')
                return True
            else:
                set_special_command(game=self, command='stalemate')
                return True
        cur_player.castle(side, opponent)
        return True
    

    def clone_game(self):
        '''
        Creates an seperate deep copy of this game instance, and has game_clone param point to
        the deep copy. In the game clone, any modification of player, board, piece state 
        should not effect the state of this current game.

        Returns: The cloned game in game_clone param

        This method should not be used outside of internal logic, ie 
        only should be used for in_check or similar methods and tree search.
        '''
        clone = Game()
        clone.board = Board()
        clone.p1 = None # this just in case ensures that there are no shenanigans with clone_player() 
        clone.p2 = None
        clone.p1 = self.p1.clone_player(board=clone.board, clone_game=clone) # note, this will also update clone.board's state to have this
                                                            # player's pieces, not just return a player 1 deep clone.
                                                            # Blame the Player <-> Piece <-> Board spaghetti.
        clone.p2 = self.p2.clone_player(board=clone.board, clone_game=clone) # ^ same for p2
        clone.turn = self.turn
        clone.winner = self.winner # now its okay since field is not a player
        # We don't store any other information about error message state, or special command state.
        self.game_clone = clone
        return self.game_clone


    def make_random_move(self):
        '''
        Given a game state where it is PLAYER's turn, makes a 
        randomized move for PLAYER, where moves are drawn
        from set of all movement zone tiles of PLAYER's pieces. 
        The move distribution is uniform. 
        This method will take up PLAYER's turn.
        '''
        all_player_moves = set()
        cur_player = convert_color_to_player(game=self, color=self.turn)
        all_player_moves = cur_player.get_all_player_move_options()
        n = len(all_player_moves)
        indices = list(range(n)) # indices to be shuffled
        random.shuffle(indices)
        for idx in indices:
            executing_move = all_player_moves[idx]
            move_taken = self.make_turn(executing_move) # may or may not be valid (based on check conditions)
            if self.special_command != '':
                # Then its checkmate or stalemate.
                return
            if move_taken:
                set_error_message(game=self, message='')
                get_error_message(self) # hopefully this resets error messaging popping up due to using make_turn
                return
            

        assert(False) # we shouldn't be able to reach here, as this implies cur_player has no possible moves left that
                    # takes it out of check, but this means cur_player should be in stalemate or checkmate.

        # TODO Also try castling as an option.

