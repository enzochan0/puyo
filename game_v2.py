import pygame
import sys
import random
import math

def run_game(screen):
    SCREEN_W, SCREEN_H = screen.get_size()
    BLACK  = (0,   0,   0)
    WHITE  = (255, 255, 255)
    GREY   = (120, 120, 120)
    YELLOW = (255, 230,  50)

    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("Arial", 20)
    radius = 12
    LIFESPAN = 10000  # 10 seconds in milliseconds

    def make_ball(balls, x=None, y=None):
        attempts = 0
        while True:
            bx = float(x if x is not None else random.randint(radius, SCREEN_W - radius))
            by = float(y if y is not None else random.randint(radius, SCREEN_H - radius))
            dx = float(random.choice([-4, -3, 3, 4]))
            dy = float(random.choice([-4, -3, 3, 4]))
            if attempts > 50 or all(math.hypot(bx - b["x"], by - b["y"]) > radius * 2 for b in balls):
                return {
                    "x": bx, "y": by,
                    "dx": dx, "dy": dy,
                    "born": pygame.time.get_ticks(),
                    "grey": False,
                    "last_spawn": 0 
                }
            attempts += 1

    balls = [make_ball([])]
    to_add = []

    while True:

        now = pygame.time.get_ticks()

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    balls.append(make_ball(balls))

        # --- age check: white → grey after 10s ---
        for b in balls:
            if not b["grey"] and now - b["born"] >= LIFESPAN:
                b["grey"] = True

        # --- move ---
        for b in balls:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            if b["x"] - radius <= 0:
                b["x"] = radius;             b["dx"] = abs(b["dx"])
            if b["x"] + radius >= SCREEN_W:
                b["x"] = SCREEN_W - radius;  b["dx"] = -abs(b["dx"])
            if b["y"] - radius <= 0:
                b["y"] = radius;             b["dy"] = abs(b["dy"])
            if b["y"] + radius >= SCREEN_H:
                b["y"] = SCREEN_H - radius;  b["dy"] = -abs(b["dy"])

        # --- ball vs ball collision ---
        to_remove = set()
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                a, b = balls[i], balls[j]
                nx = b["x"] - a["x"]
                ny = b["y"] - a["y"]
                dist = math.hypot(nx, ny)

                if dist < radius * 2 and dist > 0:
                    # push apart
                    overlap = radius * 2 - dist
                    nx /= dist;  ny /= dist
                    a["x"] -= nx * overlap / 2
                    a["y"] -= ny * overlap / 2
                    b["x"] += nx * overlap / 2
                    b["y"] += ny * overlap / 2

                    # velocity swap
                    dvx = a["dx"] - b["dx"]
                    dvy = a["dy"] - b["dy"]
                    dot = dvx * nx + dvy * ny
                    if dot > 0:
                        a["dx"] -= dot * nx;  a["dy"] -= dot * ny
                        b["dx"] += dot * nx;  b["dy"] += dot * ny

                    # lifecycle rules
                    if a["grey"]:
                        to_remove.add(i)
                    if b["grey"]:
                        to_remove.add(j)

                    # two white balls collide → spawn a new one between them
                    if not a["grey"] and not b["grey"]:
                            if (now - a["last_spawn"] > 1000 and
                                now - b["last_spawn"] > 1000):
                                spawn_x = (a["x"] + b["x"]) / 2
                                spawn_y = (a["y"] + b["y"]) / 2
                                to_add.append((spawn_x, spawn_y))
                                a["last_spawn"] = now
                                b["last_spawn"] = now

        # remove grey balls that collided (reverse order to keep indices valid)
        for i in sorted(to_remove, reverse=True):
            balls.pop(i)

        # spawn new balls from white collisions
        for (sx, sy) in to_add:
            balls.append(make_ball(balls, x=sx, y=sy))
        to_add.clear()

        # --- draw ---
        screen.fill(BLACK)
        for b in balls:
            color = GREY if b["grey"] else WHITE
            pygame.draw.circle(screen, color, (int(b["x"]), int(b["y"])), radius)

        white_count = sum(1 for b in balls if not b["grey"])
        grey_count  = sum(1 for b in balls if b["grey"])
        hint = font.render(
            f"SPACE → add ball   white: {white_count}  grey: {grey_count}   ESC → menu",
            True, YELLOW
        )
        screen.blit(hint, (10, 10))

        pygame.display.flip()
        clock.tick(60)