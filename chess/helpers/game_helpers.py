import os
from misc.constants import *
from .general_helpers import algebraic_uniconverter

'''Helper functions specialized for game logic. The variable game refers to Game type.'''

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

def pos_checker(game, pos) -> bool:
    '''
    Helper for turn in picking the right position.
    Also handles the error messages.
    '''
    pos_check, pos_message = well_formed(pos)
    if not pos_check:
        set_error_message(game, pos_message)
        return False
    pos = pos[0].upper()+pos[1]
    if not game.board.piece_exists(algebraic_uniconverter(pos)):
        set_error_message(game, 'Piece needs to exist at position '+str(pos)+'!')
        return False
    elif game.board.get_piece(algebraic_uniconverter(pos)).color != game.turn:
        set_error_message(game, ('The ' +str(game.board.get_piece(algebraic_uniconverter(pos)).rank) 
                          +' at position '+str(pos)+' is not your own color of '+str(game.turn)+'!'))
        return False
    
    return True


def dest_checker(game, pos, dest) -> bool:
    '''
    Helper for turn in picking the right destination, given pos.
    Checks legality of move from pos -> dest via move_legal.
    Also handles the error messages.
    '''
    dest_check, dest_message = well_formed(dest)
    if not dest_check:
        set_error_message(game, dest_message)
        return False
    dest = dest[0].upper()+dest[1]
    cur_player = convert_color_to_player(game=game, color=game.turn)
    move_legal, move_legal_message = cur_player.non_bool_move_legal(pos=algebraic_uniconverter(pos), 
                                                            dest=algebraic_uniconverter(dest))
    if not move_legal:
        set_error_message(game, move_legal_message)
        return False
    return True
    
def convert_color_to_player(game, color):
    '''
    Helper returns player with WHITE color if color is WHITE, otherwise it
    returns player with BLACK color if color is BLACK.
    '''
    assert(color in BWSET)
    assert(game.p1.color in BWSET and game.p2.color in BWSET)
    assert(game.p1.color != game.p2.color)

    if color == game.p1.color:
        return game.p1
    else:
        return game.p2
    
def set_error_message(game, message):
    '''
    Sets error message from error_message, and set show_error on.
    '''
    game.error_message = message
    game.show_error = True

def get_error_message(game):
    '''
    Prints error message from error_message, resets error message, and set show_error off.
    '''
    print(str(game.error_message)+'\n')
    game.error_message = ''
    game.show_error = False

def set_special_command(game, command):
    '''
    Sets special command from special_command, and set special command detection on.
    A hacky rule of thumb is command is all caps for actions (pause, forfeit, etc)
    and is lowercase for engine decisions (ie checkmate).
    '''
    game.special_command = command
    game.exists_command = True

def get_special_command(game) -> str:
    '''
    Returns special command from special_command, and resets special command field for game
    and set special command detection off.
    '''
    command = game.special_command
    game.special_command = ''
    game.exists_command = False
    return command

def get_color_in_check(game) -> str:
    '''
    If one of the players is in check, returns the color of player
    that is in check. If no player is in check, return ''.
    It should not be possible for both players to be in check.
    (as this means prev player did not leave check)
    '''
    p1_check = game.p1.in_check
    p2_check = game.p2.in_check
    assert(not (p1_check and p2_check))
    if p1_check:
        return game.p1.color
    if p2_check:
        return game.p2.color
    return ''

def get_opponent(game, player):
    '''
    Given player in game, get its opponent.
    '''
    assert(player.color in BWSET)
    opponent = game.p1 if game.p1.color != player.color else game.p2
    return opponent

    