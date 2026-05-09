import os
import pygame
from .constants import (
    PATRONUS_BLUE, SQUARE_SIZE, SIDEBAR_WIDTH, BOARD_WIDTH, WHITE, BLACK,
    ROWS, COLS, HOUSE_NAMES, COLOR_IMAGE, HUFFLEPUFF_YELLOW,
)
from .board import Board


class Game:
    def __init__(self, win, p_h, o_h):
        self.win = win
        self.p_h = p_h
        self.o_h = o_h
        self._snd_move = self._load_sound("assets/wand_flick.wav")
        self._snd_capture = self._load_sound("assets/expelliarmus.wav")
        self._font_name = pygame.font.SysFont("comicsans", 22, bold=True)
        self._font_score = pygame.font.SysFont("comicsans", 18)
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

    def _init(self):
        self.selected = None
        self.board = Board(self.p_h, self.o_h)
        self.turn = self.p_h
        self.valid_moves = {}
        self.captured_by_p = []
        self.captured_by_o = []

    def update(self):
        self.win.fill(BLACK)
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        self.draw_captured_sidebar()
        pygame.display.update()

    def _animate_piece(self, piece, end_row, end_col):
        start_x, start_y = piece.x, piece.y
        end_x = SQUARE_SIZE * end_col + SQUARE_SIZE // 2 + SIDEBAR_WIDTH
        end_y = SQUARE_SIZE * end_row + SQUARE_SIZE // 2
        steps = 18
        for i in range(1, steps + 1):
            t = i / steps
            piece.x = int(start_x + (end_x - start_x) * t)
            piece.y = int(start_y + (end_y - start_y) * t)
            self.win.fill(BLACK)
            self.board.draw(self.win)
            self.draw_captured_sidebar()
            pygame.display.update()
            pygame.time.delay(18)

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)

        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            was_king = self.selected.king
            self._animate_piece(self.selected, row, col)
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]

            if skipped:
                for caught in skipped:
                    if self.turn == self.p_h:
                        self.captured_by_p.append(caught.color)
                    else:
                        self.captured_by_o.append(caught.color)

                self.board.remove(skipped)
                if self._snd_capture:
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
                if self._snd_move:
                    self._snd_move.play()

            self.change_turn()
            return True

        return False

    def draw_captured_sidebar(self):
        def draw_side(house, captured, x_off):
            txt_color = BLACK if house == HUFFLEPUFF_YELLOW else WHITE
            pygame.draw.rect(self.win, house, (x_off, 0, SIDEBAR_WIDTH, 38))
            name_surf = self._font_name.render(HOUSE_NAMES.get(house, ""), True, txt_color)
            self.win.blit(name_surf, (x_off + SIDEBAR_WIDTH // 2 - name_surf.get_width() // 2, 8))

            img = COLOR_IMAGE.get(house)
            if img:
                self.win.blit(img, (x_off + SIDEBAR_WIDTH // 2 - 22, 48))

            score_surf = self._font_score.render(f"Taken: {len(captured)}", True, WHITE)
            self.win.blit(score_surf, (x_off + SIDEBAR_WIDTH // 2 - score_surf.get_width() // 2, 102))

            for i, color in enumerate(captured):
                r, c = i // 2, i % 2
                cx = x_off + 55 + c * 80
                cy = r * 38 + 132
                pygame.draw.circle(self.win, color, (cx, cy), 16)
                small = self._sidebar_imgs.get(color)
                if small:
                    self.win.blit(small, (cx - 13, cy - 13))

        draw_side(self.p_h, self.captured_by_p, 0)
        draw_side(self.o_h, self.captured_by_o, BOARD_WIDTH + SIDEBAR_WIDTH)

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

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

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

    def ai_move(self, board):
        moved_from = None
        moved_to = None
        for row in range(ROWS):
            for col in range(COLS):
                old = self.board.board[row][col]
                new = board.board[row][col]
                if old != 0 and new == 0 and old.color == self.o_h:
                    moved_from = (row, col)
                elif old == 0 and new != 0 and new.color == self.o_h:
                    moved_to = (row, col)

        if moved_from and moved_to:
            piece = self.board.board[moved_from[0]][moved_from[1]]
            if piece != 0:
                self._animate_piece(piece, moved_to[0], moved_to[1])

        self.board = board
        self.change_turn()
