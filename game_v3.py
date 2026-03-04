import pygame
import sys
import random
import math


def run_game(screen):
    SCREEN_W, SCREEN_H = screen.get_size()
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (120, 120, 120)
    RED = (220, 50, 50)
    YELLOW = (255, 230, 50)
    GREEN = (50, 220, 100)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)
    font_card = pygame.font.SysFont("Consolas", 14, bold=True)
    radius = 12
    LIFESPAN = 20000

    # --- ball types registry, add new entries here later ---
    BALL_TYPES = [
        {"kind": "white", "color": WHITE, "label": "WHITE"},
        {"kind": "red", "color": RED, "label": "RED"},
        {"kind": "green", "color": GREEN, "label": "GREEN"},
    ]
    selected_index = 0

    # --- UI constants ---
    BAR_H = 110  # height of bottom HUD bar
    CARD_W = 80
    CARD_H = 80
    CARD_PAD = 16  # gap between cards
    GAME_H = SCREEN_H - BAR_H  # playable area height

    def make_ball(balls, x=None, y=None, kind="white"):
        attempts = 0
        while True:
            bx = float(
                x if x is not None else random.randint(radius, SCREEN_W - radius)
            )
            by = float(y if y is not None else random.randint(radius, GAME_H - radius))
            dx = float(random.choice([-2, -1.5, 1.5, 2]))
            dy = float(random.choice([-2, -1.5, 1.5, 2]))
            if attempts > 50 or all(
                math.hypot(bx - b["x"], by - b["y"]) > radius * 2 for b in balls
            ):
                return {
                    "x": bx,
                    "y": by,
                    "dx": dx,
                    "dy": dy,
                    "born": pygame.time.get_ticks(),
                    "grey": False,
                    "kind": kind,
                    "last_spawn": 0,
                }
            attempts += 1

    def draw_bottom_bar():
        # dark bar background
        bar_rect = pygame.Rect(0, GAME_H, SCREEN_W, BAR_H)
        pygame.draw.rect(screen, (15, 15, 15), bar_rect)
        pygame.draw.line(screen, (50, 50, 50), (0, GAME_H), (SCREEN_W, GAME_H), 1)

        # center the row of cards
        total_cards_w = len(BALL_TYPES) * CARD_W + (len(BALL_TYPES) - 1) * CARD_PAD
        start_x = (SCREEN_W - total_cards_w) // 2
        card_y = GAME_H + 8

        for idx, bt in enumerate(BALL_TYPES):
            cx = start_x + idx * (CARD_W + CARD_PAD)
            is_selected = idx == selected_index

            # card surface with alpha for transparency effect
            card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((40, 40, 40, 240))
            else:
                card_surf.fill((20, 20, 20, 120))

            # ball circle on card
            ball_cx = CARD_W // 2
            ball_cy = CARD_H // 2 - 8
            ball_color = bt["color"]
            if not is_selected:
                # dim the color for unselected
                ball_color = tuple(max(0, c // 3) for c in bt["color"])
            pygame.draw.circle(card_surf, ball_color, (ball_cx, ball_cy), radius)

            # label under the ball
            label_color = WHITE if is_selected else (70, 70, 70)
            label = font_card.render(bt["label"], True, label_color)
            label_rect = label.get_rect(centerx=CARD_W // 2, top=ball_cy + radius + 6)
            card_surf.blit(label, label_rect)

            screen.blit(card_surf, (cx, card_y))

            # highlight border for selected
            if is_selected:
                pygame.draw.rect(
                    screen,
                    bt["color"],
                    (cx, card_y, CARD_W, CARD_H),
                    2,
                    border_radius=4,
                )
            else:
                pygame.draw.rect(
                    screen,
                    (40, 40, 40),
                    (cx, card_y, CARD_W, CARD_H),
                    1,
                    border_radius=4,
                )

        # hint text at very bottom
        hint = font.render(
            "SPACE → spawn       TAB → switch       ESC → menu", True, YELLOW
        )
        screen.blit(hint, hint.get_rect(centerx=SCREEN_W // 2, bottom=SCREEN_H - 1))

    balls = [make_ball([], kind="white")]
    to_add = []
    active = True

    while True:
        now = pygame.time.get_ticks()
        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.WINDOWMINIMIZED:
                active = False
            if event.type == pygame.WINDOWRESTORED:
                active = True
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    balls.append(
                        make_ball(balls, kind=BALL_TYPES[selected_index]["kind"])
                    )
                if event.key == pygame.K_TAB:
                    selected_index = (selected_index + 1) % len(BALL_TYPES)
        if active:
            # --- age check ---
            for b in balls:
                if (
                    b["kind"] == "white"
                    and not b["grey"]
                    and now - b["born"] >= LIFESPAN
                ):
                    b["grey"] = True

            # --- move (clamp to GAME_H not SCREEN_H) ---
            for b in balls:
                b["x"] += b["dx"]
                b["y"] += b["dy"]
                if b["x"] - radius <= 0:
                    b["x"] = radius
                    b["dx"] = abs(b["dx"])
                if b["x"] + radius >= SCREEN_W:
                    b["x"] = SCREEN_W - radius
                    b["dx"] = -abs(b["dx"])
                if b["y"] - radius <= 0:
                    b["y"] = radius
                    b["dy"] = abs(b["dy"])
                if b["y"] + radius >= GAME_H:
                    b["y"] = GAME_H - radius
                    b["dy"] = -abs(b["dy"])

            # --- collisions ---
            to_remove = set()
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    a, b = balls[i], balls[j]
                    nx = b["x"] - a["x"]
                    ny = b["y"] - a["y"]
                    dist = math.hypot(nx, ny)

                    if dist < radius * 2 and dist > 0:
                        nx /= dist
                        ny /= dist

                        if a["kind"] == "red" and b["kind"] == "white":
                            to_remove.add(j)
                            continue
                        if b["kind"] == "red" and a["kind"] == "white":
                            to_remove.add(i)
                            continue

                        overlap = radius * 2 - dist
                        a["x"] -= nx * overlap / 2
                        a["y"] -= ny * overlap / 2
                        b["x"] += nx * overlap / 2
                        b["y"] += ny * overlap / 2

                        dvx = a["dx"] - b["dx"]
                        dvy = a["dy"] - b["dy"]
                        dot = dvx * nx + dvy * ny
                        if dot > 0:
                            a["dx"] -= dot * nx
                            a["dy"] -= dot * ny
                            b["dx"] += dot * nx
                            b["dy"] += dot * ny

                        if a["kind"] == "red" and b["kind"] == "red":
                            if (
                                len(balls) + len(to_add) < 50
                                and now - a["last_spawn"] > 2000
                                and now - b["last_spawn"] > 2000
                            ):
                                to_add.append(
                                    (
                                        (a["x"] + b["x"]) / 2,
                                        (a["y"] + b["y"]) / 2,
                                        "red",
                                    )
                                )
                                a["last_spawn"] = b["last_spawn"] = now

                        if a["kind"] == "white" and b["kind"] == "white":
                            if not a["grey"] and not b["grey"]:
                                if (
                                    len(balls) + len(to_add) < 50
                                    and now - a["last_spawn"] > 2000
                                    and now - b["last_spawn"] > 2000
                                ):
                                    to_add.append(
                                        (
                                            (a["x"] + b["x"]) / 2,
                                            (a["y"] + b["y"]) / 2,
                                            "white",
                                        )
                                    )
                                    a["last_spawn"] = b["last_spawn"] = now
                            if a["grey"]:
                                to_remove.add(i)
                            if b["grey"]:
                                to_remove.add(j)

                        # --- green vs red: both destroyed ---
                        if (a["kind"] == "green" and b["kind"] == "red") or (
                            a["kind"] == "red" and b["kind"] == "green"
                        ):
                            to_remove.add(i)
                            to_remove.add(j)
                            continue

                        # --- green vs white: reset white's timer, both bounce ---
                        if a["kind"] == "green" and b["kind"] == "white":
                            b["born"] = now
                            b["grey"] = False
                        if b["kind"] == "green" and a["kind"] == "white":
                            a["born"] = now
                            a["grey"] = False

                        # --- green vs green: spawn new green ---
                        if a["kind"] == "green" and b["kind"] == "green":
                            if (
                                len(balls) + len(to_add) < 50
                                and now - a["last_spawn"] > 2000
                                and now - b["last_spawn"] > 2000
                            ):
                                to_add.append(
                                    (
                                        (a["x"] + b["x"]) / 2,
                                        (a["y"] + b["y"]) / 2,
                                        "green",
                                    )
                                )
                                a["last_spawn"] = b["last_spawn"] = now

            for i in sorted(to_remove, reverse=True):
                balls.pop(i)
            for sx, sy, kind in to_add:
                balls.append(make_ball(balls, x=sx, y=sy, kind=kind))
            to_add.clear()

            # --- draw ---
            screen.fill(BLACK)
            for b in balls:
                if b["kind"] == "red":
                    color = RED
                elif b["kind"] == "green":
                    color = GREEN
                elif b["grey"]:
                    color = GREY
                else:
                    color = WHITE
                pygame.draw.circle(screen, color, (int(b["x"]), int(b["y"])), radius)

            # population status top left
            white_count = sum(
                1 for b in balls if b["kind"] == "white" and not b["grey"]
            )
            grey_count = sum(1 for b in balls if b["kind"] == "white" and b["grey"])
            red_count = sum(1 for b in balls if b["kind"] == "red")
            green_count = sum(1 for b in balls if b["kind"] == "green")
            total = len(balls)

            if total < 5:
                status, sc = "population too low...", (100, 180, 255)
            elif total <= 20:
                status, sc = "population healthy", (100, 255, 100)
            elif total <= 35:
                status, sc = "getting crowded...", (255, 200, 50)
            else:
                status, sc = "overpopulated!", (255, 80, 80)

            screen.blit(font.render(status, True, sc), (10, 10))
            screen.blit(
                font.render(
                    f"W {white_count + grey_count}  R {red_count}  Gr {green_count}",
                    True,
                    (60, 60, 60),
                ),
                (10, 30),
            )

            draw_bottom_bar()
            pygame.display.flip()
        clock.tick(60)
