import asyncio
import random
import sys
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
_IS_WEB = sys.platform == "emscripten"
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

BACK_RECT    = (20, 110, 120, 40)
QUIT_RECT    = (10, 380, 180, 36)
RESTART_RECT = (10, 426, 180, 36)


def draw_bg(surface):
    surface.fill(DARK)
    for sx, sy, alpha in STARS:
        b = int(alpha * 220)
        pygame.draw.circle(surface, (b, b, b), (sx, sy), 1)
    pygame.draw.line(surface, GOLD, (60, 106), (WIDTH - 60, 106), 1)
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
    mx, my = pygame.mouse.get_pos()
    if x <= mx <= x + w and y <= my <= y + h:
        bg = tuple(min(255, c + 25) for c in bg)
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


def show_home_screen():
    try:
        import platform
        platform.window.eval(
            "var o=document.getElementById('loading-overlay'),"
            "b=document.getElementById('lo-start-btn'),"
            "s=document.getElementById('lo-spinner'),"
            "n=document.getElementById('lo-note');"
            "if(o)o.style.display='flex';"
            "if(b)b.style.display='block';"
            "if(s)s.style.display='none';"
            "if(n)n.style.display='none';"
        )
    except Exception:
        pass


def _ni_show(val=""):
    try:
        import platform
        platform.window.pyNiShow(val)
    except Exception:
        pygame.key.start_text_input()


def _ni_hide():
    try:
        import platform
        platform.window.pyNiHide()
    except Exception:
        pygame.key.stop_text_input()


def _ni_read():
    try:
        import platform
        raw = platform.window._pyNiVal
        val = str(raw)[:14] if raw else ""
        enter = bool(platform.window._pyNiEnter)
        if enter:
            platform.window.pyNiClearEnter()
        return val, enter
    except Exception:
        return None, False


async def main():
    run = True
    clock = pygame.time.Clock()

    phase       = "MODE"
    game_mode   = None
    difficulty  = None
    game        = None
    p_house     = None
    o_house     = None
    p_name      = ""
    o_name      = ""
    name_input  = ""
    naming_step = 1

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and phase == "NAME" and not _IS_WEB:
                if event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    confirmed = name_input.strip() or ("Player 1" if naming_step == 1 else "Player 2")
                    if naming_step == 1:
                        p_name = confirmed
                        if game_mode == "PVP":
                            name_input = ""
                            naming_step = 2
                        else:
                            o_name = "AI"
                            _ni_hide()
                            game = Game(WIN, p_house, o_house, p_name, o_name)
                            phase = "PLAY"
                    else:
                        o_name = confirmed
                        _ni_hide()
                        game = Game(WIN, p_house, o_house, p_name, o_name)
                        phase = "PLAY"

            if event.type == pygame.TEXTINPUT and phase == "NAME" and not _IS_WEB:
                if len(name_input) < 14:
                    name_input += event.text

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
                        show_home_screen()
                        game_mode = None
                        phase = "MODE"
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
                        if game_mode == "PVC":
                            phase = "DIFFICULTY"
                        else:
                            show_home_screen()
                            game_mode = None
                            phase = "MODE"
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
                            if game_mode == "PVP":
                                phase = "HOUSE2"
                            else:
                                o_house = SLYTHERIN_GREEN if p_h != SLYTHERIN_GREEN else GRYFFINDOR_RED
                                name_input = ""
                                naming_step = 1
                                _ni_show("")
                                phase = "NAME"

                elif phase == "NAME":
                    if bx0 <= mx <= bx0 + bw0 and by0 <= my <= by0 + bh0:
                        if naming_step == 2:
                            naming_step = 1
                            name_input = p_name
                            _ni_show(p_name)
                        else:
                            _ni_hide()
                            phase = "HOUSE"
                            name_input = ""
                    elif BX <= mx <= BX + BW and 290 <= my <= 290 + BH:
                        _ni_show(name_input)
                    elif BX <= mx <= BX + BW and 400 <= my <= 400 + BH:
                        confirmed = name_input.strip() or ("Player 1" if naming_step == 1 else "Player 2")
                        if naming_step == 1:
                            p_name = confirmed
                            if game_mode == "PVP":
                                name_input = ""
                                naming_step = 2
                                _ni_show("")
                            else:
                                o_name = "AI"
                                _ni_hide()
                                game = Game(WIN, p_house, o_house, p_name, o_name)
                                phase = "PLAY"
                        else:
                            o_name = confirmed
                            _ni_hide()
                            game = Game(WIN, p_house, o_house, p_name, o_name)
                            phase = "PLAY"

                elif phase == "HOUSE2":
                    if bx0 <= mx <= bx0 + bw0 and by0 <= my <= by0 + bh0:
                        phase = "HOUSE"
                    elif BX <= mx <= BX + BW:
                        all_h = [GRYFFINDOR_RED, SLYTHERIN_GREEN, HUFFLEPUFF_YELLOW, RAVENCLAW_BLUE]
                        avail = [c for c in all_h if c != p_house]
                        for i, color in enumerate(avail):
                            if 200 + i * 110 <= my <= 200 + i * 110 + BH:
                                o_house = color
                                name_input = ""
                                naming_step = 1
                                _ni_show("")
                                phase = "NAME"
                                break

                elif phase == "PLAY" and game is not None:
                    qx, qy, qw, qh = QUIT_RECT
                    rx, ry, rw, rh = RESTART_RECT
                    if qx <= mx <= qx + qw and qy <= my <= qy + qh:
                        show_home_screen()
                        game_mode = None
                        difficulty = None
                        game = None
                        phase = "MODE"
                    elif rx <= mx <= rx + rw and ry <= my <= ry + rh:
                        game = Game(WIN, p_house, o_house, p_name, o_name)
                    else:
                        col = (mx - SIDEBAR_WIDTH) // SQUARE_SIZE
                        row = my // SQUARE_SIZE
                        if 0 <= row < 8 and 0 <= col < 8:
                            await game.select(row, col)

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
            draw_label(WIN, "Player 1 — Choose Your House" if game_mode == "PVP" else "Choose Your House", 140)
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

        elif phase == "HOUSE2":
            draw_bg(WIN)
            draw_title(WIN)
            draw_label(WIN, "Player 2 — Choose Your House", 140)
            all_houses = [
                ("Gryffindor", GRYFFINDOR_RED,    BLACK),
                ("Slytherin",  SLYTHERIN_GREEN,   WHITE),
                ("Hufflepuff", HUFFLEPUFF_YELLOW, BLACK),
                ("Ravenclaw",  RAVENCLAW_BLUE,    WHITE),
            ]
            avail = [(n, c, t) for n, c, t in all_houses if c != p_house]
            for i, (name, color, txt_c) in enumerate(avail):
                draw_button(WIN, name, BX, 200 + i * 110, BW, BH,
                            bg=color, text_color=txt_c, img=COLOR_IMAGE.get(color))
            draw_button(WIN, "Back", *BACK_RECT)

        elif phase == "NAME":
            draw_bg(WIN)
            draw_title(WIN)
            if game_mode == "PVP" and naming_step == 2:
                draw_label(WIN, "Player 2 — Enter Your Name", 200)
            elif game_mode == "PVP":
                draw_label(WIN, "Player 1 — Enter Your Name", 200)
            else:
                draw_label(WIN, "Enter Your Name", 200)
            box_bg = WHITE if name_input else BTN_BG
            pygame.draw.rect(WIN, box_bg, (BX, 290, BW, BH))
            pygame.draw.rect(WIN, GOLD, (BX, 290, BW, BH), 2)
            for cx2, cy2, dx, dy in [(BX, 290, 1, 1), (BX+BW, 290, -1, 1),
                                      (BX, 290+BH, 1, -1), (BX+BW, 290+BH, -1, -1)]:
                pygame.draw.line(WIN, GOLD, (cx2, cy2), (cx2 + dx * 14, cy2), 3)
                pygame.draw.line(WIN, GOLD, (cx2, cy2), (cx2, cy2 + dy * 14), 3)
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            if name_input:
                display_text = name_input + cursor
                text_color   = BLACK
            else:
                display_text = "Type your name..."
                text_color   = WHITE
            name_surf = FONT_BTN.render(display_text, True, text_color)
            WIN.blit(name_surf, (BX + BW // 2 - name_surf.get_width() // 2,
                                  290 + BH // 2 - name_surf.get_height() // 2))
            btn_label = "Next" if game_mode == "PVP" and naming_step == 1 else "Play"
            draw_button(WIN, btn_label, BX, 400, BW, BH)
            draw_button(WIN, "Back", *BACK_RECT)

            if _IS_WEB:
                web_val, web_enter = _ni_read()
                if web_val is not None:
                    name_input = web_val
                if web_enter and phase == "NAME":
                    confirmed = name_input.strip() or ("Player 1" if naming_step == 1 else "Player 2")
                    if naming_step == 1:
                        p_name = confirmed
                        if game_mode == "PVP":
                            name_input = ""
                            naming_step = 2
                            _ni_show("")
                        else:
                            o_name = "AI"
                            _ni_hide()
                            game = Game(WIN, p_house, o_house, p_name, o_name)
                            phase = "PLAY"
                    else:
                        o_name = confirmed
                        _ni_hide()
                        game = Game(WIN, p_house, o_house, p_name, o_name)
                        phase = "PLAY"

        elif phase == "PLAY" and game is not None:
            ai_thinking = game_mode == "PVC" and game.turn == game.o_h
            if ai_thinking:
                game.update(ai_thinking=True)
                draw_button(WIN, "Quit",    *QUIT_RECT)
                draw_button(WIN, "Restart", *RESTART_RECT)
                pygame.display.update()
                await asyncio.sleep(0.25)
                result = minimax(game.board, difficulty, True)
                if result is not None:
                    value, new_board = result
                    if new_board is not None:
                        await game.ai_move(new_board)

            game.update(ai_thinking=False)
            draw_button(WIN, "Quit",    *QUIT_RECT)
            draw_button(WIN, "Restart", *RESTART_RECT)

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
                text = f"{p_name} Wins!" if winner == game.p_h else f"{o_name} Wins!"
                glow = FONT_TITLE.render(text, True, GOLD_DIM)
                msg  = FONT_TITLE.render(text, True, GOLD)
                WIN.blit(glow, (CX - glow.get_width() // 2 + 1, 386))
                WIN.blit(msg,  (CX - msg.get_width()  // 2,     385))
                pygame.display.update()
                await asyncio.sleep(2.5)
                show_home_screen()
                game_mode = None
                difficulty = None
                game = None
                phase = "MODE"

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
