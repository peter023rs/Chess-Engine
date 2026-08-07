import pygame
from const import *
from board import Board
from dragger import Dragger
from config import Config


class Game():

    def __init__(self):
        self.board = Board()
        self.hovered_sqr = None
        self.dragger = Dragger()
        self.next_player = 'white'
        self.config = Config()

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                #color
                color = theme.bg.light if (row+col)%2 == 0 else theme.bg.dark
                #rect
                rect = (col*SQSize, row*SQSize, SQSize,SQSize)
                #blit
                pygame.draw.rect(surface,color,rect)


    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                #piece?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    #all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSize + SQSize//2, row *SQSize + SQSize//2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme= self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            #loop all valid moves
            for move in piece.moves:
                #color
                color = theme.move.light if (move.final.row + move.final.col) %2 == 0 else theme.move.dark
                #rect
                rect = (move.final.col*SQSize, move.final.row*SQSize, SQSize, SQSize)
                #blit
                pygame.draw.rect(surface, color, rect)


    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                #color
                color = theme.trace.light if (pos.row+pos.col)%2 == 0 else theme.trace.dark
                #rect
                rect = (pos.col*SQSize, pos.row*SQSize, SQSize,SQSize)
                #blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            color = (180,180,180)
            #rect
            rect = (self.hovered_sqr.col*SQSize, self.hovered_sqr.row * SQSize, SQSize, SQSize)
            #blit
            pygame.draw.rect(surface, color, rect,width=3)
                
    #other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured = False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

