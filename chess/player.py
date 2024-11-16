from piece import Piece
from board import Board
from misc.constants import *
from move_legal import pawn_move_legal, rook_move_legal, bishop_move_legal, knight_move_legal, queen_move_legal, king_move_legal
from helpers.state_helpers import pawn_promotion, update_moved_piece
from helpers.general_helpers import check_in_bounds, algebraic_uniconverter, convert_letter_to_rank

'''
Player who gets to make chess moves.
'''

class Player:
    def __init__(self, color: str, board: Board, debug=None, is_clone=False):
        '''
        debug: debugging config, for setting initial config of pieces
        is_clone: Whether created player is a clone, if so, forgos collecting of pieces
        and setting them on board, to delegate them to client.
        '''
        self.color = color
        self.pieces = {} # key is Piece name, value is Piece, its a collection of this player's pieces
        self.board = board
        if not is_clone:
            self.collect_pieces(debug=debug) 
            self.set_pieces_on_board()
        self.in_check = False # whether Player's king is in check or not. 

        
    def collect_pieces(self, debug=None):
        '''
        Builds piece collection and their positions for this player.
        '''
        
        if debug == None:
            assert(self.color in BWSET)
            main_row = ['ROOK', 'KNIGHT', 'BISHOP', 'QUEEN', 'KING', 'BISHOP', 'KNIGHT', 'ROOK']
            main_row_pos = 1 if self.color == WHITE else 8
            pawn_row_pos = 2 if self.color == WHITE else 7
            for i in range(8):
                pawn_piece = Piece(color=self.color, rank='PAWN', pos=[i+1, pawn_row_pos], player=self)
                self.pieces[pawn_piece.name] = pawn_piece
                main_piece = Piece(color=self.color, rank=main_row[i], pos=[i+1, main_row_pos], player=self)
                self.pieces[main_piece.name] = main_piece
        elif self.color in debug.board_state:
            player_board_state = debug.board_state[self.color]
            for code in player_board_state:
                piece = Piece(color=self.color, rank=convert_letter_to_rank(code[0]), 
                              pos=algebraic_uniconverter(code[2:]), player=self)
                assert(piece.name == code) # sanity check, helped catch a knight is N bug once
                self.pieces[piece.name] = piece 


    def set_pieces_on_board(self):
        '''
        Sets this player's pieces on the board, for the start of the game.
        '''
        for piece in self.pieces.values():
            self.board.add_or_replace_piece(pos=piece.pos, piece=piece)


    def make_move(self, pos, dest):
        '''
        This moves a piece at pos to dest if said move is legal.
        Note, pos, dest are [8]^2 coordinates.
        Function will handle pawn promotion, and update the 'moved' parameter of
        the moved piece, if it has moved.
        '''
        legality, message = self.move_legal(pos=pos, dest=dest)
        if legality:
            moving_piece = self.board.get_piece(pos)
            self.board.move_piece(pos=dest, piece=moving_piece)
            pawn_promotion(player=self, dest=dest, piece=moving_piece)
            assert(moving_piece.pos == dest)
            update_moved_piece(piece=moving_piece)
        else:
            print(message)
            return

    def move_legal(self, pos, dest) -> tuple[bool, str]:
        '''
        This checks to see if moving a piece from pos to dest is legal.
        Some examples of illegal moves include out-of-bounds, out of movement zone, and other misc stuff.
        Note, moving into check is illegal but is not handled by this method.
        Note, pos, dest are [8]^2 coordinates.
        Returns True, '' or False, error message string.
        '''

        misc_check = self.misc_checks(pos=pos, dest=dest) # helper
        if not misc_check[0]:
            return misc_check
        
        cur_piece = self.board.get_piece(pos=pos)
        assert(cur_piece.pos == pos)
        rank = cur_piece.rank

        if rank == None:
            raise Exception("Piece needs to have rank")
        
        # Note no teamkill is delegated by X_move_legal functions, to have error messages make sense
        
        if rank == 'PAWN':
            return pawn_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'ROOK':
            return rook_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'BISHOP':
            return bishop_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KNIGHT':
            return knight_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'QUEEN':
            return queen_move_legal(player=self, pos=pos, dest=dest)
        elif rank == 'KING':
            return king_move_legal(player=self, pos=pos, dest=dest)
        else:
            return False, 'Rank of piece at position ' +str(algebraic_uniconverter(pos))+ ' does not match any of the 6 classes.'
    

    def misc_checks(self, pos, dest) -> tuple[bool, str]:
        '''
        Helper for move_legal.
        '''

        if not check_in_bounds(pos) or not check_in_bounds(dest):
            return False, 'Given coordinates '+str(pos)+' is out of bounds' # unreachable?
        cur_piece = self.board.get_piece(pos=pos)
        if cur_piece == None:
            return False, 'No piece at position '+str(algebraic_uniconverter(pos))+' exists'
        if type(cur_piece) != Piece:
            return False, 'Object at '+str(algebraic_uniconverter(pos))+' needs to be a piece!' # probably unreachable
        if cur_piece.color != self.color:
            return False, 'Color of selected piece doesnt match players color of '+str(self.color)+'!'
        if dest == pos:
            return False, 'Piece cannot stall as a move!'
            
        return True, 'Cannot detect any issues with prelim checks'
    

    def bool_move_legal(self, pos, dest) -> bool:
        '''
        Returns boolean value of move_legal's tuple output.
        Mainly for use when testing truth values of move legality.
        '''
        return self.move_legal(pos=pos, dest=dest)[0]
    
    def clone_player(self, board: Board):
        '''
        Returns a deep copy clone of this player, including its pieces and board state.
        '''
        clone = Player(color=self.color, board=board, is_clone=True)
        clone.pieces = self.clone_player_pieces(clone_player=clone)
        clone.set_pieces_on_board() # updates board param for clone, which is also board param for higher up Game.
        clone.in_check = self.in_check
        return clone
    
    def clone_player_pieces(self, clone_player):
        '''
        Returns a deep copy clone of the collection of pieces for this (non-clone) player.
        Each cloned piece is a deep copy of the original piece.
        '''
        cloned_collection = {}
        for piece in self.pieces.values():
            clone_piece = piece.clone_piece(player=clone_player)
            cloned_collection[clone_piece.name] = clone_piece
        return cloned_collection
