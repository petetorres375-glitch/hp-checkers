import asyncio
import copy
import os
import pygame
from .constants import (
    PATRONUS_BLUE, SQUARE_SIZE, SIDEBAR_WIDTH, BOARD_WIDTH, WHITE, BLACK,
    ROWS, COLS, HEIGHT, HOUSE_NAMES, COLOR_IMAGE, HUFFLEPUFF_YELLOW,
)
from .board import Board


class Game:
    def __init__(self, win, p_h, o_h, p_name="", o_name="", p_wins=0, o_wins=0):
        self.win = win
        self.p_h = p_h
        self.o_h = o_h
        self.p_name = p_name or "Player"
        self.o_name = o_name or "Opponent"
        self.p_wins = p_wins
        self.o_wins = o_wins
        self._snd_move = self._load_sound("assets/wand_flick.wav")
        self._snd_capture = self._load_sound("assets/expelliarmus.wav")
        try:
            self._font_name  = pygame.font.Font("assets/Cinzel-Bold.ttf", 20)
            self._font_score = pygame.font.Font("assets/Cinzel-Regular.ttf", 16)
        except Exception:
            self._font_name  = pygame.font.SysFont("serif", 20, bold=True)
            self._font_score = pygame.font.SysFont("serif", 16)
        self._sidebar_imgs = {
            color: pygame.transform.scale(img, (26, 26))
            for color, img in COLOR_IMAGE.items()
            if img is not None
        }
        self._init()

    @staticmethod
    def _load_sound(path):
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def _snapshot(self):
        return (copy.deepcopy(self.board), self.captured_by_p[:], self.captured_by_o[:])

    def undo(self):
        if not self._history:
            return False
        self.board, self.captured_by_p, self.captured_by_o = self._history.pop()
        self.selected = None
        self.valid_moves = {}
        self.turn = self.p_h
        self._turn_saved = False
        return True

    def _init(self):
        self.selected = None
        self.board = Board(self.p_h, self.o_h)
        self.turn = self.p_h
        self.valid_moves = {}
        self.captured_by_p = []
        self.captured_by_o = []
        self.last_move = None
        self.muted = False
        self._king_flash = None
        self._history = []
        self._turn_saved = False

    def update(self, ai_thinking=False):
        self.win.fill(BLACK)
        self.board.draw(self.win, self.last_move)
        self.draw_movable_pieces()
        self.draw_valid_moves(self.valid_moves)
        self._draw_king_flash()
        self.draw_captured_sidebar(ai_thinking)
        pygame.display.update()

    async def _animate_piece(self, piece, end_row, end_col):
        start_x, start_y = piece.x, piece.y
        end_x = SQUARE_SIZE * end_col + SQUARE_SIZE // 2 + SIDEBAR_WIDTH
        end_y = SQUARE_SIZE * end_row + SQUARE_SIZE // 2
        steps = 12
        for i in range(1, steps + 1):
            t = i / steps
            piece.x = int(start_x + (end_x - start_x) * t)
            piece.y = int(start_y + (end_y - start_y) * t)
            self.win.fill(BLACK)
            self.board.draw(self.win, self.last_move)
            self.draw_captured_sidebar()
            pygame.display.update()
            await asyncio.sleep(0.012)

    async def _move(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            if not self._turn_saved:
                self._history = [self._snapshot()]
                self._turn_saved = True
            was_king = self.selected.king
            await self._animate_piece(self.selected, row, col)
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]

            self.last_move = (row, col)
            if not was_king and self.selected.king:
                self._king_flash = (row, col, pygame.time.get_ticks())

            if skipped:
                for caught in skipped:
                    if self.turn == self.p_h:
                        self.captured_by_p.append(caught.color)
                    else:
                        self.captured_by_o.append(caught.color)

                self.board.remove(skipped)
                if self._snd_capture and not self.muted:
                    self._snd_capture.play()

                if not was_king and self.selected.king:
                    self.change_turn()
                    return True

                new_moves = self.board.get_valid_moves(self.selected)
                further_jumps = {m: s for m, s in new_moves.items() if s}
                if further_jumps:
                    self.valid_moves = further_jumps
                    return True
            else:
                if self._snd_move and not self.muted:
                    self._snd_move.play()

            self.change_turn()
            return True

        return False

    def draw_captured_sidebar(self, ai_thinking=False):
        def draw_side(house, captured, x_off, player_name, is_active, thinking, wins):
            txt_color = BLACK if house == HUFFLEPUFF_YELLOW else WHITE
            pygame.draw.rect(self.win, house, (x_off, 0, SIDEBAR_WIDTH, 38))
            display = player_name[:12] if player_name else HOUSE_NAMES.get(house, "")
            name_surf = self._font_name.render(display, True, txt_color)
            self.win.blit(name_surf, (x_off + SIDEBAR_WIDTH // 2 - name_surf.get_width() // 2, 8))

            if is_active:
                pygame.draw.rect(self.win, (220, 188, 80), (x_off, 0, SIDEBAR_WIDTH, HEIGHT), 2)

            img = COLOR_IMAGE.get(house)
            if img:
                self.win.blit(img, (x_off + SIDEBAR_WIDTH // 2 - 22, 48))

            taken_surf = self._font_score.render(f"Taken: {len(captured)}", True, WHITE)
            left_surf  = self._font_score.render(f"Left:  {12 - len(captured)}", True, WHITE)
            self.win.blit(taken_surf, (x_off + SIDEBAR_WIDTH // 2 - taken_surf.get_width() // 2, 102))
            self.win.blit(left_surf,  (x_off + SIDEBAR_WIDTH // 2 - left_surf.get_width()  // 2, 120))
            wins_surf = self._font_score.render(f"Wins: {wins}", True, (200, 168, 75))
            self.win.blit(wins_surf, (x_off + SIDEBAR_WIDTH // 2 - wins_surf.get_width() // 2, 580))

            for i, color in enumerate(captured):
                r, c = i // 2, i % 2
                cx = x_off + 55 + c * 80
                cy = r * 38 + 148
                pygame.draw.circle(self.win, color, (cx, cy), 16)
                small = self._sidebar_imgs.get(color)
                if small:
                    self.win.blit(small, (cx - 13, cy - 13))

            if thinking:
                ind = self._font_score.render("Thinking...", True, (160, 130, 50))
            elif is_active:
                ind = self._font_score.render("Your Turn", True, (220, 188, 80))
            else:
                ind = None
            if ind:
                self.win.blit(ind, (x_off + SIDEBAR_WIDTH // 2 - ind.get_width() // 2, 560))

        draw_side(self.p_h, self.captured_by_p, 0,                          self.p_name, self.turn == self.p_h, False,       self.p_wins)
        draw_side(self.o_h, self.captured_by_o, BOARD_WIDTH + SIDEBAR_WIDTH, self.o_name, self.turn == self.o_h, ai_thinking, self.o_wins)

    def draw_movable_pieces(self):
        if self.selected:
            return
        max_cap = self.board.get_max_capture_count(self.turn)
        for piece in self.board.get_all_pieces(self.turn):
            moves = self.board.get_valid_moves(piece)
            if not moves:
                continue
            if max_cap > 0 and not any(len(s) == max_cap for s in moves.values()):
                continue
            x = piece.col * SQUARE_SIZE + SIDEBAR_WIDTH
            y = piece.row * SQUARE_SIZE
            pygame.draw.rect(self.win, (200, 168, 75), (x + 3, y + 3, SQUARE_SIZE - 6, SQUARE_SIZE - 6), 2)

    def _draw_king_flash(self):
        if not self._king_flash:
            return
        fr, fc, ft = self._king_flash
        elapsed = pygame.time.get_ticks() - ft
        if elapsed >= 900:
            self._king_flash = None
            return
        alpha = int(220 * (1 - elapsed / 900))
        hl = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        hl.fill((255, 215, 0, alpha))
        self.win.blit(hl, (fc * SQUARE_SIZE + SIDEBAR_WIDTH, fr * SQUARE_SIZE))

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(
                self.win,
                PATRONUS_BLUE,
                (
                    col * SQUARE_SIZE + SQUARE_SIZE // 2 + SIDEBAR_WIDTH,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2,
                ),
                15,
            )

    def change_turn(self):
        self.valid_moves = {}
        self.turn = self.o_h if self.turn == self.p_h else self.p_h
        self._turn_saved = False

    async def select(self, row, col):
        if self.selected:
            result = await self._move(row, col)
            if not result:
                self.selected = None
                await self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            moves = self.board.get_valid_moves(piece)
            max_captures = self.board.get_max_capture_count(self.turn)
            if max_captures > 0:
                moves = {m: s for m, s in moves.items() if len(s) == max_captures}
            if not moves and max_captures > 0:
                return False
            self.selected = piece
            self.valid_moves = moves
            return True

        return False

    async def ai_move(self, board):
        moved_from = None
        moved_to = None
        captures = 0
        for row in range(ROWS):
            for col in range(COLS):
                old = self.board.board[row][col]
                new = board.board[row][col]
                if old != 0 and new == 0 and old.color == self.o_h:
                    moved_from = (row, col)
                elif old == 0 and new != 0 and new.color == self.o_h:
                    moved_to = (row, col)
                elif old != 0 and new == 0 and old.color == self.p_h:
                    self.captured_by_o.append(old.color)
                    captures += 1

        if moved_from and moved_to:
            piece = self.board.board[moved_from[0]][moved_from[1]]
            if piece != 0:
                await self._animate_piece(piece, moved_to[0], moved_to[1])

        self.board = board
        if moved_to:
            self.last_move = moved_to
        if captures > 0:
            if self._snd_capture and not self.muted:
                self._snd_capture.play()
        else:
            if self._snd_move and not self.muted:
                self._snd_move.play()
        self.change_turn()
