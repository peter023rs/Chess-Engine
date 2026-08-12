import pygame
from const import *
from board import Board
from dragger import Dragger
from config import Config
from piece import Queen, Rook, Bishop, Knight


class Game():

    #order the promotion picker is drawn in
    PROMOTIONS = ['queen', 'rook', 'bishop', 'knight']

    def __init__(self):
        self.board = Board()
        self.hovered_sqr = None
        self.dragger = Dragger()
        self.next_player = 'white'
        self.config = Config()
        #(piece, row, col) of a piece clicked but not yet given a destination
        self.selected = None
        #(row, col, color) while the player is choosing a promotion piece
        self.promotion = None
        #'checkmate', 'stalemate' or None
        self.game_over = None

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

        #a piece being dragged and a piece sitting selected both show their moves
        if self.dragger.dragging:
            piece = self.dragger.piece
        elif self.selected:
            piece = self.selected[0]
        else:
            return

        #mark the square the selected piece is waiting on
        if self.selected:
            row, col = self.selected[1], self.selected[2]
            color = theme.trace.light if (row+col) %2 == 0 else theme.trace.dark
            pygame.draw.rect(surface, color, (col*SQSize, row*SQSize, SQSize, SQSize))

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
                
    def show_promotion(self, surface):
        if not self.promotion:
            return

        color = self.promotion[2]
        classes = [Queen, Rook, Bishop, Knight]

        for i, (row, col) in enumerate(self.promotion_squares()):
            rect = (col*SQSize, row*SQSize, SQSize, SQSize)
            pygame.draw.rect(surface, (245,245,245), rect)
            pygame.draw.rect(surface, (40,40,40), rect, width=2)

            piece = classes[i](color)
            piece.set_texture(size=80)
            img = pygame.image.load(piece.texture)
            center = col*SQSize + SQSize//2, row*SQSize + SQSize//2
            surface.blit(img, img.get_rect(center=center))

    def show_game_over(self, surface):
        if not self.game_over:
            return

        if self.game_over == 'checkmate':
            #next_player is the side that has been mated
            winner = 'Black' if self.next_player == 'white' else 'White'
            text = f'Checkmate - {winner} wins'
        else:
            text = 'Stalemate - draw'

        label = self.config.font.render(text, True, (255,255,255))
        hint = self.config.small_font.render('press r to play again', True, (200,200,200))
        label_rect = label.get_rect(center=(WIDTH//2, HEIGHT//2 - 14))
        hint_rect = hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 26))

        box = label_rect.union(hint_rect).inflate(60, 44)
        overlay = pygame.Surface(box.size, pygame.SRCALPHA)
        overlay.fill((0,0,0,210))
        surface.blit(overlay, box.topleft)
        surface.blit(label, label_rect)
        surface.blit(hint, hint_rect)

    #other methods

    def promotion_squares(self):
        '''the four squares the picker covers, first option on the promotion square'''
        row, col, color = self.promotion
        step = 1 if color == 'white' else -1
        return [(row + step*i, col) for i in range(4)]

    def promotion_choice(self, row, col):
        '''which piece a click landed on, or None if it missed the picker'''
        for i, square in enumerate(self.promotion_squares()):
            if square == (row, col):
                return self.PROMOTIONS[i]
        return None

    def check_game_over(self):
        self.game_over = self.board.game_over(self.next_player)

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

