import pygame
import sys
import random
import math

def run_game(screen):
    SCREEN_W, SCREEN_H = screen.get_size()
    BLACK  = (0,   0,   0)
    WHITE  = (255, 255, 255)
    GREY   = (120, 120, 120)
    RED    = (220,  50,  50)
    YELLOW = (255, 230,  50)

    clock    = pygame.time.Clock()
    font     = pygame.font.SysFont("Arial", 20)
    font_big = pygame.font.SysFont("Arial", 28, bold=True)
    radius   = 12
    LIFESPAN = 20000

    selected = "white"  # currently selected ball type to spawn

    def make_ball(balls, x=None, y=None, kind="white"):
        attempts = 0
        while True:
            bx = float(x if x is not None else random.randint(radius, SCREEN_W - radius))
            by = float(y if y is not None else random.randint(radius, SCREEN_H - radius))
            dx = float(random.choice([-2, -1.5, 1.5, 2]))
            dy = float(random.choice([-2, -1.5, 1.5, 2]))
            if attempts > 50 or all(math.hypot(bx - b["x"], by - b["y"]) > radius * 2 for b in balls):
                return {
                    "x": bx, "y": by,
                    "dx": dx, "dy": dy,
                    "born": pygame.time.get_ticks(),
                    "grey": False,
                    "kind": kind,
                    "last_spawn": 0
                }
            attempts += 1

    balls  = [make_ball([], kind="white")]
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
                    balls.append(make_ball(balls, kind=selected))
                if event.key == pygame.K_TAB:
                    selected = "red" if selected == "white" else "white"

        # --- age check: white → grey after 20s (red balls don't age) ---
        for b in balls:
            if b["kind"] == "white" and not b["grey"] and now - b["born"] >= LIFESPAN:
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

        # --- collisions ---
        to_remove = set()
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                a, b = balls[i], balls[j]
                nx   = b["x"] - a["x"]
                ny   = b["y"] - a["y"]
                dist = math.hypot(nx, ny)

                if dist < radius * 2 and dist > 0:
                    nx /= dist;  ny /= dist

                    # --- red vs white: white despawns, red passes through ---
                    if a["kind"] == "red" and b["kind"] != "red":
                        to_remove.add(j)
                        continue
                    if b["kind"] == "red" and a["kind"] != "red":
                        to_remove.add(i)
                        continue

                    # --- everything else: push apart + velocity swap ---
                    overlap = radius * 2 - dist
                    a["x"] -= nx * overlap / 2;  a["y"] -= ny * overlap / 2
                    b["x"] += nx * overlap / 2;  b["y"] += ny * overlap / 2

                    dvx = a["dx"] - b["dx"]
                    dvy = a["dy"] - b["dy"]
                    dot = dvx * nx + dvy * ny
                    if dot > 0:
                        a["dx"] -= dot * nx;  a["dy"] -= dot * ny
                        b["dx"] += dot * nx;  b["dy"] += dot * ny

                    # --- red vs red: spawn new red ---
                    if a["kind"] == "red" and b["kind"] == "red":
                        if (len(balls) + len(to_add) < 50 and
                            now - a["last_spawn"] > 2000 and
                            now - b["last_spawn"] > 2000):
                                sx = (a["x"] + b["x"]) / 2
                                sy = (a["y"] + b["y"]) / 2
                                to_add.append((sx, sy, "red"))
                                a["last_spawn"] = now
                                b["last_spawn"] = now

                    # --- white vs white: spawn new white ---
                    if a["kind"] == "white" and b["kind"] == "white":
                        if not a["grey"] and not b["grey"]:
                            if (len(balls) + len(to_add) < 50 and
                                now - a["last_spawn"] > 2000 and
                                now - b["last_spawn"] > 2000):
                                    sx = (a["x"] + b["x"]) / 2
                                    sy = (a["y"] + b["y"]) / 2
                                    to_add.append((sx, sy, "white"))
                                    a["last_spawn"] = now
                                    b["last_spawn"] = now

                        # grey white destroyed on collision
                        if a["grey"]: to_remove.add(i)
                        if b["grey"]: to_remove.add(j)

        for i in sorted(to_remove, reverse=True):
            balls.pop(i)
        for (sx, sy, kind) in to_add:
            balls.append(make_ball(balls, x=sx, y=sy, kind=kind))
        to_add.clear()

        # --- draw ---
        screen.fill(BLACK)
        for b in balls:
            if b["kind"] == "red":
                color = RED
            elif b["grey"]:
                color = GREY
            else:
                color = WHITE
            pygame.draw.circle(screen, color, (int(b["x"]), int(b["y"])), radius)

        # population status
        white_count = sum(1 for b in balls if b["kind"] == "white" and not b["grey"])
        grey_count  = sum(1 for b in balls if b["kind"] == "white" and b["grey"])
        red_count   = sum(1 for b in balls if b["kind"] == "red")
        total       = len(balls)

        if total < 5:
            status, status_color = "population too low...", (100, 180, 255)
        elif total <= 20:
            status, status_color = "population healthy",   (100, 255, 100)
        elif total <= 35:
            status, status_color = "getting crowded...",   (255, 200,  50)
        else:
            status, status_color = "overpopulated!",       (255,  80,  80)

        sel_color = RED if selected == "red" else WHITE
        sel_label = font_big.render(f"[ {selected} ]", True, sel_color)

        hint   = font.render(f"SPACE → spawn   TAB → switch   white: {white_count}  grey: {grey_count}  red: {red_count}   ESC → menu", True, YELLOW)
        pop    = font.render(status, True, status_color)
        screen.blit(hint,      (10, 10))
        screen.blit(pop,       (10, 35))
        screen.blit(sel_label, (10, 60))

        pygame.display.flip()
        clock.tick(60)