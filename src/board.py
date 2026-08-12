from const import *
from square import Square
from piece import *
from move import Move
import copy


class Board:

    def __init__(self):
        self.squares = [[0,0,0,0,0,0,0,0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        #remember this before the board changes - an empty target means en passant
        en_passant_empty = self.squares[final.row][final.col].isempty()

        #console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            #en passant capture - a pawn only moves diagonally onto an empty
            #square when it is capturing the pawn beside it
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
            else:
                self.check_promotion(piece,final)

        #king castling
        if isinstance(piece, King):
            if self.castling(initial,final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff<0) else piece.right_rook
                if rook:
                    #rook jumps to the square the king crossed
                    rook_initial = Square(initial.row, 0 if diff<0 else 7)
                    rook_final = Square(initial.row, 3 if diff<0 else 5)
                    self.move(rook, Move(rook_initial, rook_final))
        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #en passant is only offered for the single move after a double push
        self.set_true_en_passant(piece, initial, final)

        #set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        #queen by default - main.py opens a picker and calls promote() to change it
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = self._promoted('queen', piece.color)

    def promote(self, row, col, name):
        '''swap an already promoted piece for the one the player picked'''
        color = self.squares[row][col].piece.color
        self.squares[row][col].piece = self._promoted(name, color)

    def _promoted(self, name, color):
        piece = {'queen': Queen, 'rook': Rook, 'bishop': Bishop, 'knight': Knight}[name](color)
        #a promoted piece has already moved - otherwise a rook promoted onto a1
        #or h1 would look like untouched castling material
        piece.moved = True
        return piece

    def set_true_en_passant(self, piece, initial, final):
        #any move at all wipes the previous right - it expires immediately
        for row in range(ROWS):
            for col in range(COLS):
                p = self.squares[row][col].piece
                if isinstance(p, Pawn):
                    p.en_passant = False

        #only a two square push grants it
        if isinstance(piece, Pawn) and abs(final.row - initial.row) == 2:
            piece.en_passant = True

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def king_in_check(self, color):
        '''is this side's king attacked right now?'''
        for row in range(ROWS):
            for col in range(COLS):
                p = self.squares[row][col].piece
                if isinstance(p, King) and p.color == color:
                    #a move onto its own square leaves the position untouched
                    return self.in_check(p, Move(Square(row,col), Square(row,col)))
        return False

    def has_legal_moves(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                p = self.squares[row][col].piece
                if p and p.color == color:
                    self.calc_moves(p, row, col)
                    found = len(p.moves) > 0
                    p.clear_moves()
                    if found:
                        return True
        return False

    def game_over(self, color):
        '''\'checkmate\', \'stalemate\' or None for the side about to move'''
        if self.has_legal_moves(color):
            return None
        return 'checkmate' if self.king_in_check(color) else 'stalemate'

    def in_check(self,piece,move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p,row, col, bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    
    def calc_moves(self, piece, row, col, bool =True):
        '''
            Calculate all the possible (valid) moves of an specific piece on a specific position
        '''

        #start from a clean list, otherwise moves stack up on every click
        piece.clear_moves()

        def knight_moves():
            #8possible moves
            possible_moves = [
                (row-2, col+1),
                (row-2, col-1),
                (row-1, col+2),
                (row-1, col-2),
                (row+2, col -1),
                (row+2, col+1),
                (row+1, col-2),
                (row+1, col+2),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        #create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece) #piece = piece
                        #create new move
                        move = Move(initial,final)

                        #append new valid move
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)

                        else:
                            piece.add_moves(move)

        def pawn_moves():
            #steps
            steps = 1 if piece.moved else 2

            #vertical moves
            start = row + piece.dir
            end = row+(piece.dir * (1+steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        #create initial and finall move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        #create a new move
                        move = Move(initial, final)

                        #check potential chcks
                        if bool:
                            if not self.in_check(piece, move):

                                piece.add_moves(move)

                        else:
                            piece.add_moves(move)
                    #blocked
                    else:
                        break
                #not in range
                else:
                    break

            #diagonal moves
            possible_move_row = row+piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)

                        #check potential chcks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)

                        else:
                            piece.add_moves(move)

            #en passant moves
            #white captures standing on row 3 and lands on row 2, black the mirror
            en_passant_row = 3 if piece.color == 'white' else 4
            final_row = 2 if piece.color == 'white' else 5

            if row == en_passant_row:
                for possible_move_col in [col-1, col+1]:
                    if Square.in_range(possible_move_col):
                        if self.squares[row][possible_move_col].has_rival_piece(piece.color):
                            p = self.squares[row][possible_move_col].piece
                            if isinstance(p, Pawn) and p.en_passant:
                                initial = Square(row, col)
                                #the captured pawn sits beside us, not on the target square
                                final = Square(final_row, possible_move_col, p)
                                move = Move(initial, final)

                                #check potential chcks
                                if bool:
                                    if not self.in_check(piece, move):
                                        piece.add_moves(move)

                                else:
                                    piece.add_moves(move)

        def straightlinemoves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row+row_incr
                possible_move_col = col+col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):

                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        move = Move(initial,final)

                        #empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #check potential chcks
                            if bool:
                                if not self.in_check(piece, move):
    
                                    piece.add_moves(move)
    
                            else:
                                piece.add_moves(move)

                        #has enemy piece
                        elif self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            #check potential chcks
                            if bool:
                                if not self.in_check(piece, move):
    
                                    piece.add_moves(move)
    
                            else:
                                piece.add_moves(move)
                            break

                        #has team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            
                            break

                        #not in range
                    else: break
                        #incrementing incrs
                    possible_move_row,possible_move_col = possible_move_row+row_incr, possible_move_col+col_incr

        def king_move():
            adjs = [
                (row-1, col),(row-1,col+1),(row,col+1),(row+1,col+1),(row+1,col),(row+1,col-1),(row,col-1),(row-1,col-1)
            ]

            #normal moves
            for possible_move in adjs:
                possible_moves_row, possible_moves_col = possible_move

                if Square.in_range(possible_moves_row, possible_moves_col):
                    if self.squares[possible_moves_row][possible_moves_col].isempty_or_rival(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_moves_row][possible_moves_col].piece
                        final = Square(possible_moves_row,possible_moves_col, final_piece)
                        move = Move(initial,final)
                        #check potential chcks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)

                        else:
                            piece.add_moves(move)

            #castling moves
            if not piece.moved:
                
                #queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1,4):
                            if self.squares[row][c].has_piece(): #castling is not possible - pieces in between
                                break

                            if c ==3:
                                #adds left rook to king
                                piece.left_rook = left_rook

                                #rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial,final)
            

                                #king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial,final)
        

                                #check potential chcks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        #append new move to rook
                                        left_rook.add_moves(moveR)
                                        piece.add_moves(moveK)

                                else:
                                    left_rook.add_moves(moveR)
                                    piece.add_moves(moveK)


                #king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5,7):
                            if self.squares[row][c].has_piece(): #castling is not possible - pieces in between
                                break

                            if c ==6:
                                #adds right rook to king
                                piece.right_rook = right_rook

                                #rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial,final)
                                

                                #king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial,final)

                                #check potential chcks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        #append new move to rook
                                        right_rook.add_moves(moveR)
                                        piece.add_moves(moveK)

                                else:
                                    right_rook.add_moves(moveR)
                                    piece.add_moves(moveK)
                                
                                



        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straightlinemoves([
                (-1,1),(-1,-1),(1,-1),(1,1)
            ])

        elif isinstance(piece, Rook):
            straightlinemoves([
                (-1,0),(1,0),(0,1),(0,-1)
            ])

        elif isinstance(piece, Queen):
            straightlinemoves([
                (-1,1),(-1,-1),(1,-1),(1,1),(-1,0),(1,0),(0,1),(0,-1)
            ])

        elif isinstance(piece, King):
            king_move()
        

    def _create(self): 
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

     
    def _add_pieces(self, color):
        row_pawn, row_other = (6,7) if color == 'white' else (1,0)

        #pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        #knights
        self.squares[row_other][1] = Square(row_other, 1,Knight(color))
        self.squares[row_other][6] = Square(row_other, 6,Knight(color))

        #bishops
        self.squares[row_other][2] = Square(row_other, 2,Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5,Bishop(color))

        #rooks
        self.squares[row_other][0] = Square(row_other, 0,Rook(color))
        self.squares[row_other][7] = Square(row_other, 7,Rook(color))

        #queen
        self.squares[row_other][3] = Square(row_other, 3,Queen(color))

        #king
        self.squares[row_other][4] = Square(row_other, 4,King(color))
                