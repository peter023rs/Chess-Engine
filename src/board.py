from const import *
from square import Square
from piece import *
from move import Move


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

        #console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def calc_moves(self, piece, row, col):
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
                possible_possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_possible_move_row, possible_move_col):
                    if self.squares[possible_possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        #create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_possible_move_row, possible_move_col) #piece = piece
                        #create new move
                        move = Move(initial,final)
                        #append new valid move
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
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        piece.add_moves(move)

        def straightlinemoves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row+row_incr
                possible_move_col = col+col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):

                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)

                        move = Move(initial,final)

                        #empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #create new move
                            piece.add_moves(move)

                        #has enemy piece
                        if self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            #create new move
                            piece.add_moves(move)
                            break

                        #has team piece
                        if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
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
                        final = Square(possible_moves_row,possible_moves_col)
                        move = Move(initial,final)
                        piece.add_moves(move)

            #castling moves



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
                