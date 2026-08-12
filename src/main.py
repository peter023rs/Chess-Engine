import pygame
import sys
from const import *
from game import Game
from square import Square
from move import Move
from piece import Pawn

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    def apply_move(self, piece, initial, final):
        '''run an already validated move and hand the turn over'''
        game = self.game
        board = game.board
        screen = self.screen

        captured = board.squares[final.row][final.col].has_piece()
        #an en passant target square is empty but still a capture
        if isinstance(piece, Pawn) and final.col != initial.col:
            captured = True
        promoting = isinstance(piece, Pawn) and final.row in (0, 7)

        board.move(piece, Move(initial, final))
        game.selected = None

        #sounds
        game.play_sound(captured)
        #show methods
        game.show_bg(screen)
        game.show_last_move(screen)
        game.show_pieces(screen)

        if promoting:
            #hand over to the picker, the turn ends once it is answered
            game.promotion = (final.row, final.col, piece.color)
        else:
            #next turn
            game.next_turn()
            game.check_game_over()

    def mainloop(self):
        

        game = self.game
        screen = self.screen
        board = self.game.board
        dragger = self.game.dragger

        while True:
            #show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)

            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            game.show_promotion(screen)
            game.show_game_over(screen)

            for event in pygame.event.get():

                #click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSize
                    clicked_col = dragger.mouseX // SQSize

                    #the picker owns the board until a piece is chosen
                    if game.promotion:
                        choice = game.promotion_choice(clicked_row, clicked_col)
                        if choice:
                            row, col, _ = game.promotion
                            board.promote(row, col, choice)
                            game.promotion = None
                            game.next_turn()
                            game.check_game_over()
                        continue

                    #no picking pieces up once the game is decided
                    if game.game_over:
                        continue

                    #something is already selected, so this click is either its
                    #destination, a different piece to pick up, or a cancel
                    if game.selected:
                        selected_piece, selected_row, selected_col = game.selected

                        #clicking it again puts it back down
                        if (clicked_row, clicked_col) == (selected_row, selected_col):
                            game.selected = None
                            continue

                        initial = Square(selected_row, selected_col)
                        final = Square(clicked_row, clicked_col)
                        if board.valid_move(selected_piece, Move(initial, final)):
                            self.apply_move(selected_piece, initial, final)
                            continue

                        #not a legal destination - drop the selection and fall
                        #through, in case they clicked another of their pieces
                        game.selected = None

                    #if clicked square has a piece?
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        #valid piece (color)?
                        if piece.color == game.next_player:

                            board.calc_moves(piece, clicked_row, clicked_col, bool = True)
                            game.selected = (piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            #show methods
                            game.show_bg(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                #mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1]//SQSize
                    motion_col = event.pos[0]//SQSize
                    game.set_hover(motion_row,motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        #show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)
                        

                #click release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSize
                        released_col = dragger.mouseX // SQSize

                        #let go on the square it started on, so that was a click and
                        #not a drag - leave it selected and wait for a destination
                        if (released_row, released_col) != (dragger.initial_row, dragger.initial_col):
                            # create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            #valid move?
                            if board.valid_move(dragger.piece, move):
                                self.apply_move(dragger.piece, initial, final)

                    dragger.undrag_piece()

                #key press
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_t:

                        #changing themes
                        game.change_theme()

                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
            
                #auit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

main = Main()   
main.mainloop()
