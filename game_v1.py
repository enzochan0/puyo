import pygame
import sys
import random
import math

def run_game(screen):
    SCREEN_W, SCREEN_H = screen.get_size()
    BLACK  = (0,   0,   0)
    WHITE  = (255, 255, 255)
    YELLOW = (255, 230,  50)

    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("Arial", 20)
    radius = 12

    def make_ball():
        while True:
            x  = random.randint(radius, SCREEN_W - radius)
            y  = random.randint(radius, SCREEN_H - radius)
            dx = random.choice([-4, -3, 3, 4])
            dy = random.choice([-4, -3, 3, 4])
            # make sure new ball doesn't spawn inside an existing one
            if all(math.hypot(x - b["x"], y - b["y"]) > radius * 2 for b in balls):
                return {"x": float(x), "y": float(y), "dx": float(dx), "dy": float(dy)}

    balls = [{"x": float(SCREEN_W // 2), "y": float(SCREEN_H // 2),
              "dx": 3.0, "dy": -3.0}]

    while True:

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    balls.append(make_ball())

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
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                a, b = balls[i], balls[j]
                nx = b["x"] - a["x"]
                ny = b["y"] - a["y"]
                dist = math.hypot(nx, ny)
                if dist < radius * 2 and dist > 0:
                    # push apart so they don't stick
                    overlap = radius * 2 - dist
                    nx /= dist;  ny /= dist
                    a["x"] -= nx * overlap / 2
                    a["y"] -= ny * overlap / 2
                    b["x"] += nx * overlap / 2
                    b["y"] += ny * overlap / 2
                    # swap velocity along collision axis
                    dvx = a["dx"] - b["dx"]
                    dvy = a["dy"] - b["dy"]
                    dot = dvx * nx + dvy * ny
                    if dot > 0:   # only resolve if moving toward each other
                        a["dx"] -= dot * nx;  a["dy"] -= dot * ny
                        b["dx"] += dot * nx;  b["dy"] += dot * ny

        # --- draw ---
        screen.fill(BLACK)
        for b in balls:
            pygame.draw.circle(screen, WHITE, (int(b["x"]), int(b["y"])), radius)

        hint = font.render(f"SPACE → add ball ({len(balls)})   ESC → menu", True, YELLOW)
        screen.blit(hint, (10, 10))

        pygame.display.flip()
        clock.tick(60)