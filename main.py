import asyncio
import random
import pygame
from hp_logic.constants import (
    WIDTH, HEIGHT, SQUARE_SIZE, SIDEBAR_WIDTH, BLACK, WHITE,
    GRYFFINDOR_RED, SLYTHERIN_GREEN, HUFFLEPUFF_YELLOW, RAVENCLAW_BLUE,
    COLOR_IMAGE,
)
from hp_logic.game import Game
from ai.minimax import minimax

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Harry Potter House Cup Checkers")

GOLD     = (200, 168, 75)
GOLD_DIM = (70,  52,  18)
DARK     = (8,   8,   20)
BTN_BG   = (15,  15,  35)

try:
    FONT_TITLE = pygame.font.Font("assets/Cinzel-Bold.ttf", 46)
    FONT_BTN   = pygame.font.Font("assets/Cinzel-Bold.ttf", 26)
    FONT_SUB   = pygame.font.Font("assets/Cinzel-Regular.ttf", 18)
except Exception:
    FONT_TITLE = pygame.font.SysFont("serif", 46, bold=True)
    FONT_BTN   = pygame.font.SysFont("serif", 26, bold=True)
    FONT_SUB   = pygame.font.SysFont("serif", 18)

_rng  = random.Random(42)
STARS = [(_rng.randint(0, WIDTH), _rng.randint(0, HEIGHT), _rng.uniform(0.15, 1.0))
         for _ in range(160)]

BW, BH = 370, 68
CX = WIDTH // 2
BX = CX - BW // 2

BACK_RECT = (50, HEIGHT - 110, 140, 46)


def draw_bg(surface):
    surface.fill(DARK)
    for sx, sy, alpha in STARS:
        b = int(alpha * 220)
        pygame.draw.circle(surface, (b, b, b), (sx, sy), 1)
    pygame.draw.line(surface, GOLD, (60, 75), (WIDTH - 60, 75), 1)
    pygame.draw.line(surface, GOLD, (60, HEIGHT - 75), (WIDTH - 60, HEIGHT - 75), 1)


def draw_title(surface):
    glow  = FONT_TITLE.render("House Cup Checkers", True, GOLD_DIM)
    title = FONT_TITLE.render("House Cup Checkers", True, GOLD)
    surface.blit(glow,  (CX - glow.get_width()  // 2 + 1, 16))
    surface.blit(title, (CX - title.get_width() // 2,     15))
    sub = FONT_SUB.render("A Wizarding Strategy Game", True, (140, 110, 45))
    surface.blit(sub, (CX - sub.get_width() // 2, 68))


def draw_button(surface, text, x, y, w, h, bg=None, text_color=GOLD, img=None):
    bg = bg or BTN_BG
    pygame.draw.rect(surface, bg, (x, y, w, h))
    pygame.draw.rect(surface, GOLD, (x, y, w, h), 2)
    for cx2, cy2, dx, dy in [(x, y, 1, 1), (x+w, y, -1, 1), (x, y+h, 1, -1), (x+w, y+h, -1, -1)]:
        pygame.draw.line(surface, GOLD, (cx2, cy2), (cx2 + dx * 14, cy2), 3)
        pygame.draw.line(surface, GOLD, (cx2, cy2), (cx2, cy2 + dy * 14), 3)
    txt = FONT_BTN.render(text, True, text_color)
    if img:
        surface.blit(img, (x + 12, y + h // 2 - 22))
        tx = x + 60 + (w - 60) // 2 - txt.get_width() // 2
    else:
        tx = x + w // 2 - txt.get_width() // 2
    surface.blit(txt, (tx, y + h // 2 - txt.get_height() // 2))


def draw_label(surface, text, y):
    surf = FONT_SUB.render(text, True, (160, 128, 52))
    surface.blit(surf, (CX - surf.get_width() // 2, y))


async def main():
    run = True
    clock = pygame.time.Clock()

    phase       = "MODE"
    game_mode   = None
    difficulty  = None
    game        = None

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                bx0, by0, bw0, bh0 = BACK_RECT

                if phase == "MODE":
                    if BX <= mx <= BX + BW:
                        if 310 <= my <= 310 + BH:
                            game_mode = "PVC"
                            phase = "DIFFICULTY"
                        elif 420 <= my <= 420 + BH:
                            game_mode = "PVP"
                            difficulty = 0
                            phase = "HOUSE"

                elif phase == "DIFFICULTY":
                    if bx0 <= mx <= bx0 + bw0 and by0 <= my <= by0 + bh0:
                        phase = "MODE"
                        game_mode = None
                    elif BX <= mx <= BX + BW:
                        if 250 <= my <= 250 + BH:
                            difficulty = 1
                            phase = "HOUSE"
                        elif 345 <= my <= 345 + BH:
                            difficulty = 3
                            phase = "HOUSE"
                        elif 440 <= my <= 440 + BH:
                            difficulty = 4
                            phase = "HOUSE"

                elif phase == "HOUSE":
                    if bx0 <= mx <= bx0 + bw0 and by0 <= my <= by0 + bh0:
                        phase = "DIFFICULTY" if game_mode == "PVC" else "MODE"
                    elif BX <= mx <= BX + BW:
                        p_h = None
                        if 185 <= my <= 185 + BH:
                            p_h = GRYFFINDOR_RED
                        elif 275 <= my <= 275 + BH:
                            p_h = SLYTHERIN_GREEN
                        elif 365 <= my <= 365 + BH:
                            p_h = HUFFLEPUFF_YELLOW
                        elif 455 <= my <= 455 + BH:
                            p_h = RAVENCLAW_BLUE
                        if p_h is not None:
                            p_house = p_h
                            o_house = SLYTHERIN_GREEN if p_h != SLYTHERIN_GREEN else GRYFFINDOR_RED
                            game = Game(WIN, p_house, o_house)
                            phase = "PLAY"

                elif phase == "PLAY" and game is not None:
                    if bx0 <= mx <= bx0 + bw0 and by0 <= my <= by0 + bh0:
                        phase = "MODE"
                        game_mode = None
                        difficulty = None
                        game = None
                    else:
                        mx2, my2 = pygame.mouse.get_pos()
                        col = (mx2 - SIDEBAR_WIDTH) // SQUARE_SIZE
                        row = my2 // SQUARE_SIZE
                        if 0 <= row < 8 and 0 <= col < 8:
                            game.select(row, col)

        if phase == "MODE":
            draw_bg(WIN)
            draw_title(WIN)
            draw_label(WIN, "Select Game Mode", 255)
            draw_button(WIN, "VS Computer", BX, 310, BW, BH)
            draw_button(WIN, "VS Player",   BX, 420, BW, BH)

        elif phase == "DIFFICULTY":
            draw_bg(WIN)
            draw_title(WIN)
            draw_label(WIN, "Select Difficulty", 200)
            draw_button(WIN, "Easy",   BX, 250, BW, BH, bg=(10, 45, 10))
            draw_button(WIN, "Medium", BX, 345, BW, BH, bg=(45, 38, 5))
            draw_button(WIN, "Hard",   BX, 440, BW, BH, bg=(50, 5,  5))
            draw_button(WIN, "Back", *BACK_RECT)

        elif phase == "HOUSE":
            draw_bg(WIN)
            draw_title(WIN)
            draw_label(WIN, "Choose Your House", 140)
            houses = [
                ("Gryffindor", GRYFFINDOR_RED,    BLACK, 185),
                ("Slytherin",  SLYTHERIN_GREEN,   WHITE, 275),
                ("Hufflepuff", HUFFLEPUFF_YELLOW, BLACK, 365),
                ("Ravenclaw",  RAVENCLAW_BLUE,    WHITE, 455),
            ]
            for name, color, txt_c, hy in houses:
                draw_button(WIN, name, BX, hy, BW, BH,
                            bg=color, text_color=txt_c, img=COLOR_IMAGE.get(color))
            draw_button(WIN, "Back", *BACK_RECT)

        elif phase == "PLAY" and game is not None:
            if game_mode == "PVC" and game.turn == game.o_h:
                pygame.time.delay(250)
                result = minimax(game.board, difficulty, True)
                if result is not None:
                    value, new_board = result
                    if new_board is not None:
                        game.ai_move(new_board)

            game.update()
            draw_button(WIN, "Quit", *BACK_RECT)

            winner = game.board.winner()
            if winner is not None:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                WIN.blit(overlay, (0, 0))
                pygame.draw.rect(WIN, DARK, (335, 325, 530, 150))
                pygame.draw.rect(WIN, GOLD, (335, 325, 530, 150), 2)
                for cx2, cy2, dx, dy in [(335, 325, 1, 1), (865, 325, -1, 1),
                                          (335, 475, 1, -1), (865, 475, -1, -1)]:
                    pygame.draw.line(WIN, GOLD, (cx2, cy2), (cx2 + dx * 18, cy2), 3)
                    pygame.draw.line(WIN, GOLD, (cx2, cy2), (cx2, cy2 + dy * 18), 3)
                if winner == game.p_h:
                    text = "Player 1 Wins!"
                else:
                    text = "AI Wins!" if game_mode == "PVC" else "Player 2 Wins!"
                glow = FONT_TITLE.render(text, True, GOLD_DIM)
                msg  = FONT_TITLE.render(text, True, GOLD)
                WIN.blit(glow, (CX - glow.get_width() // 2 + 1, 386))
                WIN.blit(msg,  (CX - msg.get_width()  // 2,     385))
                pygame.display.update()
                pygame.time.delay(2500)
                phase = "MODE"
                game_mode = None
                difficulty = None
                game = None

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
