import unittest
import unittest.mock
from unittest.mock import patch

from game import Game
from debug import Debug
from piece import Piece
import random
import os
from tests import set_up_debug
from helpers.state_helpers import (update_players_check, move_puts_player_in_check, move_locks_opponent, 
                                   clone_game_and_get_game_state_based_on_move)
from helpers.game_helpers import clear_terminal
from movement_zone import mass_movement_zone, get_movement_zone

if __name__ == "__main__":

    game = Game()
    input_commands = ['r']*20 + ['b']*6 + ['PAUSE']
    with patch('builtins.input', side_effect=input_commands):
        game.start()