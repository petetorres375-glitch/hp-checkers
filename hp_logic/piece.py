import pygame
from .constants import SQUARE_SIZE, SIDEBAR_WIDTH, WHITE, PATRONUS_BLUE, COLOR_IMAGE


class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2 + SIDEBAR_WIDTH
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING

        pygame.draw.circle(win, WHITE, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)

        image = COLOR_IMAGE.get(self.color)
        if image:
            win.blit(image, image.get_rect(center=(self.x, self.y)))

        if self.king:
            pygame.draw.circle(win, (255, 215, 0), (self.x, self.y), radius + 10, 4)
            pygame.draw.circle(win, PATRONUS_BLUE, (self.x, self.y), radius + 5, 3)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)
