import math
import random
import sys
import threading
import time
import pygame

BG = (10, 10, 20)
WIDTH, HEIGHT = 800, 600

lock = threading.Lock()

fireworks = []
particles = []

BASE_COLORS = [
    (255, 50, 50),
    (50, 255, 100),
    (50, 150, 255),
    (255, 100, 255),
    (255, 220, 50),
    (255, 120, 30),
]


def spawn_rocket(start_x=None, target_y=None):
  x = start_x if start_x is not None else random.randint(100, WIDTH - 100)
  y = HEIGHT
  t_y = target_y if target_y is not None else random.randint(50, HEIGHT // 3)

  if target_y is not None:
    distance = HEIGHT - target_y
    vy = -math.sqrt(2 * 0.2 * distance)
  else:
    vy = random.uniform(-14, -10)

  color_idx = random.randint(0, len(BASE_COLORS) - 1)
  exploded = 0

  fireworks.append([x, y, vy, t_y, color_idx, exploded])


def update_simulation():
  global fireworks, particles
  while True:
    time.sleep(0.02)
    with lock:
      if random.random() < 0.04:
        spawn_rocket()

      remaining_fireworks = []
      for f in fireworks:
        if f[5] == 0:
          f[1] += f[2]
          f[2] += 0.2
          if f[1] <= f[3] or f[2] >= 0:
            f[5] = 1
            num_particles = random.randint(120, 180)
            for _ in range(num_particles):
              angle = random.uniform(0, math.pi * 2)
              speed = random.uniform(2, 9)
              vx = math.cos(angle) * speed
              vy = math.sin(angle) * speed
              color_idx = f[4]
              life = 1.0
              decay = random.uniform(0.008, 0.02)
              particles.append([f[0], f[1], vx, vy, color_idx, life, decay])
        if f[5] == 0:
          remaining_fireworks.append(f)
      fireworks = remaining_fireworks

      remaining_particles = []
      for p in particles:
        p[0] += p[2]
        p[1] += p[3]
        p[3] += 0.12
        p[2] *= 0.985
        p[3] *= 0.985
        p[5] -= p[6]
        if p[5] > 0:
          remaining_particles.append(p)
      particles = remaining_particles


def draw(screen):
  for f in fireworks:
    if f[5] == 0:
      color = BASE_COLORS[f[4]]
      pygame.draw.circle(screen, color, (int(f[0]), int(f[1])), 3)

  for p in particles:
    boost = min(1.0, p[5] * 1.4)
    base_color = BASE_COLORS[p[4]]
    c = (
        int(base_color[0] * boost),
        int(base_color[1] * boost),
        int(base_color[2] * boost),
    )
    pygame.draw.circle(screen, c, (int(p[0]), int(p[1])), 2)


def main():
  pygame.init()
  pygame.display.set_caption("Index-Based Procedural Fireworks")
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  clock = pygame.time.Clock()

  sim_thread = threading.Thread(target=update_simulation, daemon=True)
  sim_thread.start()

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      elif event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()
        with lock:
          spawn_rocket(start_x=mx, target_y=my)

    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.set_alpha(45)
    fade_surface.fill(BG)
    screen.blit(fade_surface, (0, 0))

    with lock:
      draw(screen)

    pygame.display.flip()
    clock.tick(60)


if __name__ == "__main__":
  main()