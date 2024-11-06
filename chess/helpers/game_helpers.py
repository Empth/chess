import os
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
        game.set_error_message(pos_message)
        return False
    pos = pos[0].upper()+pos[1]
    if not game.board.piece_exists(algebraic_uniconverter(pos)):
        game.set_error_message('Piece needs to exist at position '+str(pos)+'!')
        return False
    elif game.board.get_piece(algebraic_uniconverter(pos)).color != game.turn:
        game.set_error_message('The ' +str(game.board.get_piece(algebraic_uniconverter(pos)).rank) +' at position '+str(pos)+' is not your own color of '+str(game.turn)+'!')
        return False
    
    return True


def dest_checker(game, pos, dest) -> bool:
    '''
    Helper for turn in picking the right destination, given pos.
    Also handles the error messages.
    '''
    dest_check, dest_message = well_formed(dest)
    if not dest_check:
        game.set_error_message(dest_message)
        return False
    dest = dest[0].upper()+dest[1]
    cur_player = convert_color_to_player(game=game, color=game.turn)
    move_legal, move_legal_message = cur_player.move_legal(pos=algebraic_uniconverter(pos), 
                                                            dest=algebraic_uniconverter(dest))
    if not move_legal:
        game.set_error_message(move_legal_message)
        return False
    return True
    
def convert_color_to_player(game, color):
    '''
    Helper returns player 1 if color is WHITE, otherwise player 2
    if color is BLACK.
    '''
    assert(color in ['BLACK', 'WHITE'])
    if color == 'WHITE':
        return game.p1
    else:
        return game.p2
    
def set_error_message(game, message):
    '''
    Sets error message from error_message, and set error_message on
    '''
    game.error_message = message
    game.show_error = True

def get_error_message(game):
    '''
    Shows error message from error_message, resets error message, and set error_message off
    '''
    print(game.error_message)
    game.error_message = ''
    game.show_error = False

def set_special_command(game, command):
    '''
    Sets special command from special_command, and set special command detection on
    '''
    game.special_command = command
    game.exists_command = True

def get_special_command(game) -> str:
    '''
    Returns special command from special_command, and resets special command field for game
    and set special command detection off
    '''
    command = game.special_command
    game.special_command = ''
    game.show_error = False
    return command


def check_winner_king_condition(game) -> bool:
    '''
    Checks if a player is missing their king. If so, then the other player is
    declared the winner of the match, by updating winner. At least one player should have their king.
    Boolean is if winner was found (True) or not.
    '''
    p1_has_king = False
    p2_has_king = False
    p1_collection = game.p1.pieces
    p2_collection = game.p2.pieces
    for key in p1_collection:
        if p1_collection[key].rank == 'KING':
            p1_has_king = True
    for key in p2_collection:
        if p2_collection[key].rank == 'KING':
            p2_has_king = True
    assert(p1_has_king or p2_has_king)
    if not p1_has_king:
        game.winner = game.p2
        return True
    if not p2_has_king:
        game.winner = game.p1
        return True
    return False