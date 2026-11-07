import pygame
import sys
import random
import threading
import time

BG = (30, 30, 30)

board_y = 40
board_x = 60
board = []
for y in range(board_y):
    board.append([0] * board_x)

length = 12
gap = 2

tab_y = board_y * (length + gap) + gap
tab_x = board_x * (length + gap) + gap

lock = threading.Lock()

def check_flr(y, x):
    return y + 1 < board_y

def spawn():
    for x in range(board_x):
        if random.random() > 0.2: board[board_y - 1][x] = 36
        else: 0

def fall():
    while True:
        time.sleep(0.04)
        with lock:
            for x in range(board_x):
                if random.random() > 0.3: board[board_y - 1][x] = 36
                else: 0
            for x in range(board_x):
                for y in range(1, board_y):
                    below = board[y][x]
                    decay = random.randint(0, 3)
                    wind = random.randint(-1, 1)
                    target_x = x + wind

                    if 0 <= target_x < board_x:
                        board[y - 1][target_x] = max(0, below - decay)

def get_color(intensity):
    if intensity == 0:
        return (30, 30, 30)
    elif intensity < 12:
        return (intensity * 20, 0, 0)
    elif intensity < 24:
        return (255, (intensity - 12) * 20, 0)
    else:
        return (255, 255, min(255, (intensity - 24) * 20))

def draw(screen):
    for y in range(board_y):
        for x in range(board_x):
            X = x * (length + gap) + gap
            Y = y * (length + gap) + gap
            intensity = board[y][x]
            color = get_color(intensity)

            pygame.draw.rect(screen, color, [X, Y, length, length], border_radius = 2)

def main():
    pygame.init()
    pygame.display.set_caption("Fire")
    screen = pygame.display.set_mode((tab_x, tab_y))
    clock = pygame.time.Clock()

    spawn()
    bg_thread = threading.Thread(target=fall, daemon=True)
    bg_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill((10, 10, 10))
        
        with lock:
            draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()