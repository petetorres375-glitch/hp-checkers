import pygame
from .constants import ROWS, COLS, SQUARE_SIZE, SIDEBAR_WIDTH


class Board:
    def __init__(self, p_color, o_color):
        self.board = []
        self.p_color = p_color
        self.o_color = o_color
        self.create_board()

    def create_board(self):
        from .piece import Piece

        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, self.o_color))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, self.p_color))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                x = col * SQUARE_SIZE + SIDEBAR_WIDTH
                y = row * SQUARE_SIZE
                color = (60, 0, 0) if (row + col) % 2 == 1 else (30, 30, 30)
                pygame.draw.rect(win, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col] = 0
        self.board[row][col] = piece
        piece.move(row, col)

        if not piece.king:
            if piece.color == self.p_color and row == 0:
                piece.make_king()
            elif piece.color == self.o_color and row == ROWS - 1:
                piece.make_king()

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def evaluate(self):
        p_score = 0
        o_score = 0

        for row in self.board:
            for piece in row:
                if piece != 0:
                    value = 3 if piece.king else 1
                    if piece.color == self.o_color:
                        o_score += value
                    else:
                        p_score += value

        return o_score - p_score

    def winner(self):
        p_pieces = self.get_all_pieces(self.p_color)
        o_pieces = self.get_all_pieces(self.o_color)

        if len(p_pieces) == 0:
            return self.o_color
        if len(o_pieces) == 0:
            return self.p_color

        if not self.has_any_moves(self.p_color):
            return self.o_color
        if not self.has_any_moves(self.o_color):
            return self.p_color

        return None

    def has_any_moves(self, color):
        for piece in self.get_all_pieces(color):
            if self.get_valid_moves(piece):
                return True
        return False

    def get_max_capture_count(self, color):
        max_count = 0
        for piece in self.get_all_pieces(color):
            for skipped in self.get_valid_moves(piece).values():
                if len(skipped) > max_count:
                    max_count = len(skipped)
        return max_count

    def get_valid_moves(self, piece):
        if piece.king:
            return self._get_flying_king_moves(piece)
        return self._get_man_moves(piece)

    def _get_man_moves(self, piece):
        moves = {}
        directions = []

        if piece.color == self.p_color:
            directions.extend([(-1, -1), (-1, 1)])
        if piece.color == self.o_color:
            directions.extend([(1, -1), (1, 1)])

        for dr, dc in directions:
            r = piece.row + dr
            c = piece.col + dc
            if self._in_bounds(r, c) and self.board[r][c] == 0:
                moves[(r, c)] = []

        capture_moves = self._get_man_captures(piece, piece.row, piece.col, [], set())
        if capture_moves:
            return capture_moves

        return moves

    def _get_man_captures(self, piece, row, col, captured, visited, can_go_back=False):
        moves = {}
        found_capture = False

        if can_go_back:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == self.p_color:
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        for dr, dc in directions:
            mid_r = row + dr
            mid_c = col + dc
            land_r = row + 2 * dr
            land_c = col + 2 * dc

            if not self._in_bounds(mid_r, mid_c) or not self._in_bounds(land_r, land_c):
                continue

            middle = self.board[mid_r][mid_c]
            landing = self.board[land_r][land_c]

            if (
                middle != 0
                and middle.color != piece.color
                and landing == 0
                and (mid_r, mid_c) not in visited
            ):
                found_capture = True
                new_captured = captured + [middle]
                new_visited = visited | {(mid_r, mid_c)}

                temp_piece = self.board[row][col]
                self.board[row][col] = 0
                self.board[land_r][land_c] = temp_piece

                deeper = self._get_man_captures(piece, land_r, land_c, new_captured, new_visited, can_go_back=True)

                self.board[row][col] = temp_piece
                self.board[land_r][land_c] = 0

                if deeper:
                    moves.update(deeper)
                else:
                    moves[(land_r, land_c)] = new_captured

        if found_capture:
            return moves
        return {}

    def _get_flying_king_moves(self, piece):
        capture_moves = self._get_flying_king_captures(piece, piece.row, piece.col, [], set())
        if capture_moves:
            return capture_moves

        moves = {}
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = piece.row + dr
            c = piece.col + dc
            while self._in_bounds(r, c) and self.board[r][c] == 0:
                moves[(r, c)] = []
                r += dr
                c += dc

        return moves

    def _get_flying_king_captures(self, piece, row, col, captured, visited):
        moves = {}
        found_capture = False
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = row + dr
            c = col + dc
            enemy = None
            enemy_pos = None

            while self._in_bounds(r, c):
                current = self.board[r][c]

                if current == 0:
                    if enemy is not None:
                        found_capture = True
                        new_captured = captured + [enemy]
                        new_visited = visited | {enemy_pos}

                        temp_piece = self.board[row][col]
                        self.board[row][col] = 0
                        self.board[r][c] = temp_piece

                        deeper = self._get_flying_king_captures(
                            piece, r, c, new_captured, new_visited
                        )

                        self.board[row][col] = temp_piece
                        self.board[r][c] = 0

                        if deeper:
                            moves.update(deeper)
                        else:
                            moves[(r, c)] = new_captured
                    r += dr
                    c += dc
                    continue

                if current.color == piece.color:
                    break

                if enemy is not None:
                    break

                if (r, c) in visited:
                    break

                enemy = current
                enemy_pos = (r, c)
                r += dr
                c += dc

        if found_capture:
            return moves
        return {}

    def _in_bounds(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS
