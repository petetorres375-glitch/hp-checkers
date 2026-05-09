import asyncio
import pygame
from hp_logic.constants import (
    WIDTH, HEIGHT, SQUARE_SIZE, SIDEBAR_WIDTH, BLACK, WHITE,
    GRYFFINDOR_RED, SLYTHERIN_GREEN, HUFFLEPUFF_YELLOW, RAVENCLAW_BLUE
)
from hp_logic.game import Game
from ai.minimax import minimax

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Harry Potter House Cup Checkers")
FONT = pygame.font.SysFont("comicsans", 30)


async def main():
    run = True
    clock = pygame.time.Clock()

    phase = "MODE"
    game_mode = None
    difficulty = None
    game = None
    player_house = None
    ai_house = None

    while run:
        clock.tick(60)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if phase == "MODE":
                    if 450 <= pos[0] <= 750:
                        if 300 <= pos[1] <= 360:
                            game_mode = "PVC"
                            phase = "DIFFICULTY"
                        elif 400 <= pos[1] <= 460:
                            game_mode = "PVP"
                            difficulty = 0
                            phase = "HOUSE"

                elif phase == "DIFFICULTY":
                    if 450 <= pos[0] <= 750:
                        if 250 <= pos[1] <= 310:
                            difficulty = 1
                            phase = "HOUSE"
                        elif 350 <= pos[1] <= 410:
                            difficulty = 3
                            phase = "HOUSE"
                        elif 450 <= pos[1] <= 510:
                            difficulty = 4
                            phase = "HOUSE"

                elif phase == "HOUSE":
                    if 450 <= pos[0] <= 750:
                        p_h = None
                        if 200 <= pos[1] <= 260:
                            p_h = GRYFFINDOR_RED
                        elif 300 <= pos[1] <= 360:
                            p_h = SLYTHERIN_GREEN
                        elif 400 <= pos[1] <= 460:
                            p_h = HUFFLEPUFF_YELLOW
                        elif 500 <= pos[1] <= 560:
                            p_h = RAVENCLAW_BLUE

                        if p_h is not None:
                            player_house = p_h
                            ai_house = SLYTHERIN_GREEN if p_h != SLYTHERIN_GREEN else GRYFFINDOR_RED
                            game = Game(WIN, player_house, ai_house)
                            phase = "PLAY"

                elif phase == "PLAY" and game is not None:
                    col = (pos[0] - SIDEBAR_WIDTH) // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        game.select(row, col)

        WIN.fill(BLACK)

        if phase == "MODE":
            WIN.blit(FONT.render("Select Game Mode", True, WHITE), (500, 200))
            pygame.draw.rect(WIN, (50, 50, 50), (450, 300, 300, 60))
            WIN.blit(FONT.render("VS Computer", True, WHITE), (510, 310))
            pygame.draw.rect(WIN, (50, 50, 50), (450, 400, 300, 60))
            WIN.blit(FONT.render("VS Player", True, WHITE), (530, 410))

        elif phase == "DIFFICULTY":
            WIN.blit(FONT.render("Select AI Difficulty", True, WHITE), (490, 150))
            pygame.draw.rect(WIN, (0, 80, 0), (450, 250, 300, 60))
            WIN.blit(FONT.render("Easy", True, WHITE), (550, 260))
            pygame.draw.rect(WIN, (80, 80, 0), (450, 350, 300, 60))
            WIN.blit(FONT.render("Medium", True, WHITE), (540, 360))
            pygame.draw.rect(WIN, (80, 0, 0), (450, 450, 300, 60))
            WIN.blit(FONT.render("Hard", True, WHITE), (555, 460))

        elif phase == "HOUSE":
            WIN.blit(FONT.render("Choose Your House", True, WHITE), (480, 100))
            y_coords = [200, 300, 400, 500]
            houses = [
                ("Gryffindor", GRYFFINDOR_RED),
                ("Slytherin", SLYTHERIN_GREEN),
                ("Hufflepuff", HUFFLEPUFF_YELLOW),
                ("Ravenclaw", RAVENCLAW_BLUE),
            ]
            for i, h in enumerate(houses):
                pygame.draw.rect(WIN, h[1], (450, y_coords[i], 300, 60))
                txt_c = BLACK if h[0] == "Hufflepuff" else WHITE
                WIN.blit(FONT.render(h[0], True, txt_c), (520, y_coords[i] + 15))

        elif phase == "PLAY" and game is not None:
            if game_mode == "PVC" and game.turn == game.o_h:
                pygame.time.delay(250)
                result = minimax(game.board, difficulty, True)
                if result is not None:
                    value, new_board = result
                    if new_board is not None:
                        game.ai_move(new_board)

            game.update()

            winner = game.board.winner()
            if winner is not None:
                pygame.draw.rect(WIN, BLACK, (420, 360, 360, 80))
                if winner == game.p_h:
                    text = "Player 1 Wins!"
                else:
                    text = "AI Wins!" if game_mode == "PVC" else "Player 2 Wins!"
                WIN.blit(FONT.render(text, True, WHITE), (500, 385))
                pygame.display.update()
                pygame.time.delay(2000)
                phase = "MODE"
                game_mode = None
                difficulty = None
                game = None

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
