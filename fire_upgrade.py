import pygame, sys, random, threading, time

width = 60
height = 40
size = 12
gap = 2
board = [[0] * width for _ in range(height)]
lock = threading.Lock()

pallette = [
    ((20, 0, 0), (255, 100, 0), (255, 255, 200)),
    ((0, 40, 100), (0, 120, 220), (150, 220, 255)),
    ((60, 0, 80), (160, 30, 200), (230, 150, 255)),
    ((0, 60, 20), (30, 200, 60), (180, 255, 180)),
    ((80, 60, 0), (220, 180, 20), (255, 255, 150)),
    ((0, 60, 80), (0, 200, 220), (180, 255, 255))
]

state = 0
timer = 0
p_idx = 0
next_p_idx = 1
p_trans = 0.0

def update():
    global state, timer, p_idx, next_p_idx, p_trans
    while True:
        time.sleep(0.04)
        with lock:
            timer += 1
            for x in range(width):
                if state == 0: spark_prob = 0.95 - (timer / 120.0) * 0.65
                else: spark_prob = 0.3
                if random.random() > spark_prob: board[-1][x] = 36
                else: board[-1][x] = 0
            for x in range(width):
                for y in range(1, height):
                    target_x = max(0, min(width - 1, x + random.randint(-1, 1)))
                    board[y - 1][target_x] = max(0, board[y][x] - random.randint(0, 3))
            if state == 0 and timer > 110:
                timer, state = 0, 1
            elif state == 1 and timer > 140:
                timer, state, p_trans = 0, 2, 0.0
            elif state == 2:
                p_trans += 0.015
                if p_trans >= 1.0:
                    timer, p_idx, state = 0, 1, 3
            elif state == 3 and timer > 140:
                timer, state, p_trans = 0, 4, 0.0
            elif state == 4:
                p_trans += 0.015
                if p_trans >= 1.0:
                    timer, p_idx, state = 0, 2, 5
            elif state == 5:
                p_trans += 0.008
                if p_trans >= 1.0:
                    p_trans, p_idx = 0.0, next_p_idx
                    next_p_idx = (next_p_idx + 1) % len(pallette)

def get_color(val):
    if val == 0:
        return (30, 30, 30)
    if state == 0:
        factor = min(1.0, timer / 110.0)
        p1 = p2 = pallette[0]
        blend = 0.0
    else:
        factor = 1.0
        p1 = pallette[p_idx]
        p2, blend = {
            2: (pallette[1], p_trans),
            4: (pallette[2], p_trans),
            5: (pallette[next_p_idx], p_trans)
        }.get(state, (p1, 0.0))

    def blend_rgb(c1, c2, f):
        return tuple(int((c1[i] * (1 - f) + c2[i] * f) * factor) for i in range(3))
    
    if val < 12:
        f = val / 12.0
        return blend_rgb([c * f for c in p1[0]], [c * f for c in p2[0]], blend)
    elif val < 24:
        f = (val - 12) / 12.0
        return blend_rgb([p1[0][1] * (1 - f) + p1[1][i] * f for i in range(3)], [p2[0][i] * (1 - f) + p2[1][i] * f for i in range(3)], blend)
    else:
        f = min(1.0, (val - 24) / 12.0)
        return blend_rgb([p1[1][i] * (1 - f) + p1[2][i] * f for i in range(3)], [p2[1][i] * (1 - f) + p2[2][i] * f for i in range(3)], blend)

def main():
    pygame.init()
    w, h = width * (size + gap) + gap, height * (size + gap) + gap
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Fire 002")
    clock = pygame.time.Clock()

    threading.Thread(target=update, daemon=True).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((10, 10, 10))
        with lock:
            for y in range(height):
                for x in range(width):
                    rect = [x * (size + gap) + gap, y * (size + gap) + gap, size, size]
                    pygame.draw.rect(screen, get_color(board[y][x]), rect, border_radius = 2)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()