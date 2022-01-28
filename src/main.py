from chess import *
import chess.svg
import sfengine
# import myengine
import sys
import random
import time
import pygame

from pygame.locals import (
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SQUARE_HEIGHT = 100
BOARD_POS = (0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
surfaces = []
board = Board()
pieceString = {"r": "br", "n": "bn", "b": "bb", "q": "bq", "k": "bk", "p": "bp",
               "R": "wr", "N": "wn", "B": "wb", "Q": "wq", "K": "wk", "P": "wp"}
locations = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
key_list = pygame.sprite.LayeredUpdates()
promo_list = pygame.sprite.LayeredUpdates()


class Piece(pygame.sprite.Sprite):
    layer = 1

    def __init__(self, xpos, ypos, image, id, piecetype, group, layer):
        super(Piece, self).__init__()
        self.image = image
        self.clicked = False
        self.rect = self.image.get_rect()
        self.rect.y = ypos
        self.rect.x = xpos
        self.id = id
        self.piecetype = piecetype
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, group)
        group.add(self, layer=self._layer)


def draw_piece(position, piece, init, promo, promo_pos):
    location = r'C:\Users\Crgla\Desktop\Personal Coding Projects\chess-engine\assets\{piece}.png'.format(piece=piece)
    image = pygame.image.load(location)
    newimage = pygame.transform.smoothscale(image, (100, 100))
    img_rect = newimage.get_rect(center=(position[0] + 50, position[1] + 50))

    if init:
        if promo:
            Piece(promo_pos[0], promo_pos[1], image=newimage, id=len(promo_list) + 1, piecetype=piece, group=promo_list, layer=0)
        else:
            Piece(position[0], position[1], image=newimage, id=len(key_list) + 1, piecetype=piece, group=key_list, layer=0)

    screen.blit(newimage, img_rect)
    pygame.display.flip()


def draw_pieces(FEN, init, promo, promo_pos):
    index = 0
    row = 0
    for char in FEN:
        if char == " ":
            break
        else:
            if char.isdigit():
                index += int(char)
            elif char == "/":
                index = 0
                row += 1
            elif char.isalpha():
                position = (index * 100, row * 100)
                draw_piece(position, pieceString[char], init, False, None)
                index += 1
    if promo:
        # if white is promoting
        if promo_pos[1] == 0:
            draw_piece(promo_pos, "wq", init, True, promo_pos)
            newpos = (promo_pos[0], promo_pos[1] + 100)
            draw_piece(newpos, "wn", init, True, newpos)
            newpos = (newpos[0], newpos[1] + 100)
            draw_piece(newpos, "wr", init, True, newpos)
            newpos = (newpos[0], newpos[1] + 100)
            draw_piece(newpos, "wb", init, True, newpos)
        # if black if promoting
        elif promo_pos[1] == 700:
            draw_piece(promo_pos, "bq", init, True, promo_pos)  # change here
            newpos = (promo_pos[0], promo_pos[1] - 100)
            draw_piece(newpos, "bn", init, True, newpos)
            newpos = (newpos[0], newpos[1] - 100)
            draw_piece(newpos, "br", init, True, newpos)
            newpos = (newpos[0], newpos[1] - 100)
            draw_piece(newpos, "bb", init, True, newpos)
        else:
            print(promo_pos)
            print("you shouldn't see this (in draw_pieces())")
            exit(1)


def get_square_under_mouse():
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - BOARD_POS
    x, y = [int(v // SQUARE_HEIGHT) for v in mouse_pos]
    try:
        if x >= 0 and y >= 0: return (x, y)
    except IndexError: pass
    return None, None, None


def draw_board(init, promo, promo_pos):
    board_surf = pygame.Surface((SQUARE_HEIGHT * 8, SQUARE_HEIGHT * 8))
    for file in range(8):
        for rank in range(8):
            isLightSqare = (file + rank) % 2 == 0
            if isLightSqare:
                squareColor = (240, 217, 181)
            else:
                squareColor = (181, 136, 99)
            rect = pygame.Rect(rank * SQUARE_HEIGHT, file * SQUARE_HEIGHT, SQUARE_HEIGHT, SQUARE_HEIGHT)
            pygame.draw.rect(board_surf, squareColor, rect)
    draw_pieces(board.fen(), init, promo, promo_pos)
    return board_surf


def draw_move_marker(original_location, target_location, fixed_original_location):
    transparency = 170
    if original_location:
        origin = pygame.Surface((SQUARE_HEIGHT, SQUARE_HEIGHT))
        origin.set_alpha(transparency)
        origin.fill((248, 236, 91))
        screen.blit(origin, (original_location[0] * SQUARE_HEIGHT, original_location[1] * SQUARE_HEIGHT))
    if target_location:
        origin = pygame.Surface((SQUARE_HEIGHT, SQUARE_HEIGHT))
        origin.set_alpha(transparency)
        origin.fill((248, 236, 91))
        screen.blit(origin, (target_location[0] * SQUARE_HEIGHT, target_location[1] * SQUARE_HEIGHT))
    if fixed_original_location:
        if fixed_original_location == original_location:
            return
        origin = pygame.Surface((SQUARE_HEIGHT, SQUARE_HEIGHT))
        origin.set_alpha(transparency)
        origin.fill((248, 236, 91))
        screen.blit(origin, (fixed_original_location[0] * SQUARE_HEIGHT, fixed_original_location[1] * SQUARE_HEIGHT))


def animate_linear(origin, target, step, board_surf, sprite, is_x, blitinfo):
    for val in range(origin, target + step, step):
        screen.blit(board_surf, BOARD_POS)
        draw_move_marker(blitinfo[0], blitinfo[1], blitinfo[2])
        if is_x:
            sprite.rect.x = val
        else:
            sprite.rect.y = val
        key_list.update()
        key_list.draw(screen)
        pygame.display.flip()
        time.sleep(0.01)


def animate_slope(origin, target, step, board_surf, sprite, is_x, blitinfo, slope, origin2):
    altorigin = 0
    altorigin += origin2
    for val in range(origin, target + step, step):
        screen.blit(board_surf, BOARD_POS)
        draw_move_marker(blitinfo[0], blitinfo[1], blitinfo[2])

        if is_x:
            sprite.rect.x = val
            sprite.rect.y = altorigin
        else:
            sprite.rect.y = val
            sprite.rect.x = altorigin

        key_list.update()
        key_list.draw(screen)
        pygame.display.flip()
        altorigin += slope * step
        time.sleep(0.01)


def animate_all(target_location, fixed_original_location, board_surf, blitinfo):
    # remove piece to be animated from screen
    spritelist = pygame.sprite.LayeredUpdates.get_sprites_at(self=key_list,
                                                             pos=(
                                                                 fixed_original_location[0] * 100, fixed_original_location[1] * 100))
    if len(spritelist) == 1:
        spritelist[0].rect.y = fixed_original_location[1] * 100
        spritelist[0].rect.x = fixed_original_location[0] * 100
        key_list.update()
        key_list.draw(screen)
        pygame.display.flip()
        while True:
            if not (target_location[1] * 100 == fixed_original_location[1] * 100 or target_location[0] * 100 ==
                    fixed_original_location[0] * 100):
                slope = (target_location[1] * 100 - fixed_original_location[1] * 100) / (
                            target_location[0] * 100 - fixed_original_location[0] * 100)
                # diagonal movement here
                if target_location[0] * 100 > fixed_original_location[0] * 100:
                    animate_slope(fixed_original_location[0] * 100, target_location[0] * 100, 10,
                                  board_surf, spritelist[0], True, blitinfo, slope, fixed_original_location[1] * 100)
                else:
                    animate_slope(fixed_original_location[0] * 100, target_location[0] * 100, -10,
                                  board_surf, spritelist[0], True, blitinfo, slope, fixed_original_location[1] * 100)
            # vertical/horizontal movement here
            else:
                if target_location[1] * 100 == fixed_original_location[1] * 100:
                    if target_location[0] * 100 > fixed_original_location[0] * 100:
                        animate_linear(fixed_original_location[0] * 100, target_location[0] * 100, 10,
                                       board_surf, spritelist[0], True, blitinfo)
                    else:
                        animate_linear(fixed_original_location[0] * 100, target_location[0] * 100, -10,
                                       board_surf, spritelist[0], True, blitinfo)
                else:
                    if target_location[1] * 100 > fixed_original_location[1] * 100:
                        animate_linear(fixed_original_location[1] * 100, target_location[1] * 100, 10,
                                       board_surf, spritelist[0], False, blitinfo)
                    else:
                        animate_linear(fixed_original_location[1] * 100, target_location[1] * 100, -10,
                                       board_surf, spritelist[0], False, blitinfo)
            break
        spritelist[0].rect.y = target_location[1] * 100
        spritelist[0].rect.x = target_location[0] * 100


def main():
    #board.set_fen("8/3P4/8/5K2/8/8/1kb5/8 w - - 0 1")
    #board.set_fen("6k1/4Q3/6K1/8/8/8/8/8 b - - 0 1")
    #board.set_fen("3r2r1/2Pp1Pp1/3n2p1/2KQ2Q1/3p2p1/8/1k6/8 w - - 0 1")

    #board.set_fen("8/3P4/8/5K2/8/8/1kn5/8 w - - 0 1")
    #board.set_fen("8/4K3/8/8/8/1k6/3p2p1/8 b - - 0 1")

    #board.set_fen("3qkb2/4n3/3p1p2/3Np3/2B5/8/8/6K1 b - - 0 1")

    print(board.fen())
    print(board)
    print()

    player_as_white = True
    ai_vs_ai = False
    engine1 = sfengine.Stockfishclass(board.fen())
    # engine2 = myengine.Omega0(board.fen())
    # engine2.testfun(board)

    # Draw initial screen
    board_surf = draw_board(True, False, None)
    screen.blit(board_surf, BOARD_POS)
    key_list.update()
    key_list.draw(screen)
    pygame.display.flip()

    selecting_promotion = False
    promo_pos = None
    running = True
    selected_key = None
    piece_selected = False
    original_location = None
    original_marker_location = None
    target_location = None
    fixed_original_location = None
    original_square = None
    promotion = False
    clicked = False
    animate = False
    target_square = None
    while running:
        if board.turn == player_as_white and not ai_vs_ai:
            x, y = get_square_under_mouse()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if event.button == 1:
                        for key in key_list:
                            if key.rect.collidepoint(pos):
                                if piece_selected:
                                    continue
                                else:
                                    selected_key = key
                                    key.clicked = True
                                    piece_selected = True
                                    original_location = (x, y)
                                    original_marker_location = (x, y)
                                    original_square = square(x, abs(7-y))
                        if not piece_selected:
                            original_marker_location = None

                if event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    for key in key_list:
                        key.clicked = False
                    piece_selected = False
                    if selected_key:
                        target_square = square(x, abs(7-y))

                        # add promotion conditionals
                        if selected_key.piecetype == 'wp' and y == 0:
                            move_str = Move(original_square, target_square, promotion=QUEEN).uci()
                            promotion = True
                        elif selected_key.piecetype == 'bp' and y == 7:
                            move_str = Move(original_square, target_square, promotion=QUEEN).uci()
                            promotion = True
                        else:
                            move_str = Move(original_square, target_square).uci()

                        # if player puts piece back in its original spot
                        if target_square == original_square:
                            selected_key.rect.y = y * 100
                            selected_key.rect.x = x * 100
                            continue
                        else:
                            move = Move.from_uci(move_str)
                        if move in board.legal_moves:
                            target_location = (x, y)
                            fixed_original_location = original_location
                            selected_key.rect.y = y * 100
                            selected_key.rect.x = x * 100
                            # ASK PLAYER TO DECIDE PROMOTION PIECE HERE
                            if promotion:
                                promoting_piece = None
                                selecting_promotion = True
                                promo_pos = (x * 100, y * 100)

                                # draw promotion graphics on top of board
                                pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=key_list, layer_nr=1)
                                board_surf = draw_board(True, selecting_promotion, promo_pos)

                                # Draw background to piece options (get surface to be above other pieces not being promoted)
                                squarecolor = (255, 255, 255)
                                closesquarecolor = (241, 241, 241)
                                i = 0
                                is_pos = 1
                                closesquare = 0
                                if promo_pos[1] != 0:
                                    is_pos = -1
                                    closesquare = 50

                                while i <= 3:
                                    rect = pygame.Rect(promo_pos[0], promo_pos[1] + (100*i)*is_pos, SQUARE_HEIGHT,
                                                       SQUARE_HEIGHT)
                                    pygame.draw.rect(board_surf, squarecolor, rect)
                                    i += 1
                                rect = pygame.Rect(promo_pos[0], promo_pos[1] + (100 * i)*is_pos+(closesquare), SQUARE_HEIGHT,
                                                   SQUARE_HEIGHT/2)
                                pygame.draw.rect(board_surf, closesquarecolor, rect)

                                # blit screen
                                screen.blit(board_surf, BOARD_POS)

                                # remove the promoting pawn from screen
                                spritelist = pygame.sprite.LayeredUpdates.get_sprites_at(self=key_list,
                                                                                         pos=(original_location[0]*100, original_location[1]*100))
                                if len(spritelist) == 1:
                                    pygame.sprite.LayeredUpdates.change_layer(self=key_list, sprite=spritelist[0],
                                                                              new_layer=2)
                                    pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=key_list, layer_nr=2)

                                for num in range(5):
                                    spritelist = pygame.sprite.LayeredUpdates.get_sprites_at(self=key_list,
                                                                                             pos=(promo_pos[0],
                                                                                                  promo_pos[1] + num*(
                                                                                                          100 * is_pos)))
                                    if len(spritelist) == 1:
                                        pygame.sprite.LayeredUpdates.change_layer(self=key_list, sprite=spritelist[0],
                                                                                  new_layer=2)
                                        pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=key_list, layer_nr=2)

                                key_list.update()
                                key_list.draw(screen)


                                promo_list.update()
                                promo_list.draw(screen)
                                pygame.display.flip()

                                while promotion:
                                    for event in pygame.event.get():
                                        if event.type == MOUSEBUTTONDOWN:
                                            pos = pygame.mouse.get_pos()
                                            selected = False
                                            for key in promo_list:  # selection promotion
                                                if key.rect.collidepoint(pos):
                                                    promoting_piece = key.piecetype
                                                    selected = True
                                            if not selected:
                                                pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=promo_list,
                                                                                                     layer_nr=1)
                                                promotion = False
                                                selecting_promotion = False
                                                break

                                        if promoting_piece == 'wq' or promoting_piece == 'bq':
                                            pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=promo_list,
                                                                                                 layer_nr=1)
                                            move_str = Move(original_square, target_square, promotion=QUEEN).uci()
                                            move = Move.from_uci(move_str)
                                            print("Player plays: ", end='')
                                            print(board.san(move))
                                            board.push(move)
                                            selecting_promotion = False
                                            promotion = False  # debug here
                                            break
                                        elif promoting_piece == 'wn' or promoting_piece == 'bn':
                                            pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=promo_list,
                                                                                                 layer_nr=1)
                                            move_str = Move(original_square, target_square, promotion=KNIGHT).uci()
                                            move = Move.from_uci(move_str)
                                            print("Player plays: ", end='')
                                            print(board.san(move))
                                            board.push(move)
                                            selecting_promotion = False
                                            promotion = False  # debug here
                                            break
                                        elif promoting_piece == 'wr' or promoting_piece == 'br':
                                            pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=promo_list,
                                                                                                 layer_nr=1)
                                            move_str = Move(original_square, target_square, promotion=ROOK).uci()
                                            move = Move.from_uci(move_str)
                                            print("Player plays: ", end='')
                                            print(board.san(move))
                                            board.push(move)
                                            selecting_promotion = False
                                            promotion = False  # debug here
                                            break
                                        elif promoting_piece == 'wb' or promoting_piece == 'bb':
                                            pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=promo_list,
                                                                                                 layer_nr=1)
                                            move_str = Move(original_square, target_square, promotion=BISHOP).uci()
                                            move = Move.from_uci(move_str)
                                            print("Player plays: ", end='')
                                            print(board.san(move))
                                            board.push(move)
                                            selecting_promotion = False
                                            promotion = False  # debug here
                                            break

                                        if event.type == KEYDOWN:
                                            if event.key == K_ESCAPE:
                                                exit(0)
                                        elif event.type == QUIT:
                                            exit(0)
                            else:
                                selecting_promotion = False
                                print("Player plays: ", end='')
                                print(board.san(move))
                                board.push(move)

                            pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=key_list, layer_nr=1)
                            board_surf = draw_board(True, False, promo_pos)

                        else:
                            selected_key.rect.y = original_location[1] * 100
                            selected_key.rect.x = original_location[0] * 100
                    selected_key = None

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        exit(0)

                elif event.type == QUIT:
                    pygame.quit()
                    exit(0)

            for key in key_list:
                if key.clicked:
                    pos = pygame.mouse.get_pos()
                    key.rect.x = pos[0] - (key.rect.width/2)
                    key.rect.y = pos[1] - (key.rect.height/2)
                    clicked = True
                else:
                    clicked = False

            screen.blit(board_surf, BOARD_POS)

            # Draw move markers
            draw_move_marker(original_marker_location, target_location, fixed_original_location)

            if clicked:
                if x != None:
                    rect = (BOARD_POS[0] + x * SQUARE_HEIGHT, BOARD_POS[1] + y * SQUARE_HEIGHT, SQUARE_HEIGHT, SQUARE_HEIGHT)
                    pygame.draw.rect(screen, (235, 235, 235, 50), rect, 3)

            if piece_selected:
                pygame.sprite.LayeredUpdates.move_to_front(self=key_list, sprite=selected_key)

            key_list.update()
            key_list.draw(screen)

            promo_list.update()
            promo_list.draw(screen)

            pygame.display.flip()

            clock.tick(240)

        else:
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        exit(0)
                moves = list(board.legal_moves)
                if len(moves) != 0:
                    move_str = engine1.generate_move(board.fen())
                    move = board.parse_uci(move_str)

                    print("Computer plays: ", end='')
                    print(board.san(move))
                    print()
                    board.push(move)

                    original_marker_location = (locations[move_str[0]], 7 - (int(move_str[1]) - 1))
                    fixed_original_location = (locations[move_str[0]], 7 - (int(move_str[1]) - 1))
                    target_location = (locations[move_str[2]], 7 - (int(move_str[3]) - 1))

                    blitinfo = (original_marker_location, target_location, fixed_original_location)

                    animate_all(target_location, fixed_original_location, board_surf, blitinfo)

                    pygame.sprite.LayeredUpdates.remove_sprites_of_layer(self=key_list, layer_nr=1)
                    board_surf = draw_board(True, False, None)
                    animate = True

                    if not ai_vs_ai:
                        break
                    else:
                        screen.blit(board_surf, BOARD_POS)
                        draw_move_marker(fixed_original_location, target_location, original_marker_location)
                        # display pieces
                        key_list.update()
                        key_list.draw(screen)
                        pygame.display.flip()
                else:
                    print("Game over!")
                    running = False
                    break
    endscreen = True
    while endscreen:
        for event in pygame.event.get():
            if event.type == QUIT:
                endscreen = False
                pygame.quit()
                break


if __name__ == '__main__':
    main()
