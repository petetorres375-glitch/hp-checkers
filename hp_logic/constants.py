import pygame
import os

WIDTH, HEIGHT = 1200, 800
BOARD_WIDTH = 800
SIDEBAR_WIDTH = 200
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_WIDTH // COLS

GRYFFINDOR_RED = (122, 0, 0)
SLYTHERIN_GREEN = (26, 71, 42)
HUFFLEPUFF_YELLOW = (236, 185, 57)
RAVENCLAW_BLUE = (34, 47, 91)
PATRONUS_BLUE = (165, 242, 243)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def load_image(path, size):
    if os.path.exists(path):
        try:
            return pygame.transform.scale(pygame.image.load(path), size)
        except Exception:
            return None
    return None


GRYFF_IMG = load_image("assets/gryffindor.png", (45, 45))
SLYTH_IMG = load_image("assets/slytherin.png", (45, 45))
HUFF_IMG = load_image("assets/hufflepuff.png", (45, 45))
RAVE_IMG = load_image("assets/ravenclaw.png", (45, 45))

COLOR_IMAGE = {
    GRYFFINDOR_RED: GRYFF_IMG,
    SLYTHERIN_GREEN: SLYTH_IMG,
    HUFFLEPUFF_YELLOW: HUFF_IMG,
    RAVENCLAW_BLUE: RAVE_IMG,
}

HOUSE_NAMES = {
    GRYFFINDOR_RED: "Gryffindor",
    SLYTHERIN_GREEN: "Slytherin",
    HUFFLEPUFF_YELLOW: "Hufflepuff",
    RAVENCLAW_BLUE: "Ravenclaw",
}
