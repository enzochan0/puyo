import pygame
import sys
from game_v1 import run_game as run_v1
from game_v2 import run_game as run_v2
from game_v3 import run_game as run_v3

pygame.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("My Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
HOVER = (160, 160, 160)
DIM = (80, 80, 80)

font_title = pygame.font.SysFont("Consolas", 64, bold=True)
font_button = pygame.font.SysFont("Consolas", 28)
font_label = pygame.font.SysFont("Consolas", 14)
font_sub = pygame.font.SysFont("Consolas", 18)


def draw_button(text, rect, hovered, subtitle=None):
    color = HOVER if hovered else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font_button.render(text, True, BLACK)
    if subtitle:
        label_rect = label.get_rect(centerx=rect.centerx, centery=rect.centery - 10)
        sub = font_label.render(subtitle, True, (80, 80, 80))
        sub_rect = sub.get_rect(centerx=rect.centerx, centery=rect.centery + 12)
        screen.blit(label, label_rect)
        screen.blit(sub, sub_rect)
    else:
        screen.blit(label, label.get_rect(center=rect.center))


def main_menu():
    play_rect = pygame.Rect(300, 300, 200, 65)
    archive_rect = pygame.Rect(300, 385, 200, 65)
    quit_rect = pygame.Rect(300, 470, 200, 65)

    while True:
        screen.fill(BLACK)
        title = font_title.render("My Game", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 160)))

        mx, my = pygame.mouse.get_pos()
        draw_button("Play", play_rect, play_rect.collidepoint(mx, my))
        draw_button("Archive", archive_rect, archive_rect.collidepoint(mx, my))
        draw_button("Quit", quit_rect, quit_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    run_v3(screen)
                if archive_rect.collidepoint(event.pos):
                    archive_menu()
                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()


def archive_menu():
    v1_rect = pygame.Rect(250, 280, 300, 75)
    v2_rect = pygame.Rect(250, 375, 300, 75)
    back_rect = pygame.Rect(250, 470, 300, 65)

    while True:
        screen.fill(BLACK)

        title = font_sub.render("ARCHIVE", True, DIM)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 160)))
        header = font_title.render("Old Versions", True, WHITE)
        screen.blit(header, header.get_rect(center=(SCREEN_W // 2, 210)))

        mx, my = pygame.mouse.get_pos()
        draw_button(
            "Version 1",
            v1_rect,
            v1_rect.collidepoint(mx, my),
            subtitle="basic bouncing ball",
        )
        draw_button(
            "Version 2",
            v2_rect,
            v2_rect.collidepoint(mx, my),
            subtitle="lifecycle + red ball",
        )
        draw_button("← Back", back_rect, back_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if v1_rect.collidepoint(event.pos):
                    run_v1(screen)
                if v2_rect.collidepoint(event.pos):
                    run_v2(screen)
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        pygame.display.flip()


main_menu()
