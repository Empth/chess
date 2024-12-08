import os
from misc.constants import *
from .general_helpers import algebraic_uniconverter

'''Helper functions specialized for game logic. The variable game refers to Game type.'''

def clear_terminal():
    '''
    Clears the terminal.
    '''
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    
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

def get_opponent(game, player):
    '''
    Given player in game, get its opponent.
    '''
    assert(player.color in BWSET)
    opponent = game.p1 if game.p1.color != player.color else game.p2
    return opponent

    