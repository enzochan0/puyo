import pygame
import sys
from game_v1 import run_game as run_v1
from game_v2 import run_game as run_v2
from game_v3 import run_game as run_v3

pygame.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("My Game")

BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GRAY  = (200, 200, 200)
HOVER = (160, 160, 160)

font_title  = pygame.font.SysFont("Arial", 64, bold=True)
font_button = pygame.font.SysFont("Arial", 32)

def draw_button(text, rect, hovered):
    color = HOVER if hovered else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font_button.render(text, True, BLACK)
    screen.blit(label, label.get_rect(center=rect.center))

def main_menu():
    v1_rect   = pygame.Rect(300, 280, 200, 60)
    v2_rect   = pygame.Rect(300, 360, 200, 60)
    v3_rect   = pygame.Rect(300, 440, 200, 60)
    quit_rect = pygame.Rect(300, 520, 200, 60)

    while True:
        screen.fill(BLACK)
        title = font_title.render("My Game", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 160)))

        mx, my = pygame.mouse.get_pos()
        draw_button("Play v1", v1_rect,   v1_rect.collidepoint(mx, my))
        draw_button("Play v2", v2_rect,   v2_rect.collidepoint(mx, my))
        draw_button("Play v3", v3_rect,   v3_rect.collidepoint(mx, my))
        draw_button("Quit",    quit_rect, quit_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if v1_rect.collidepoint(event.pos):
                    run_v1(screen)
                if v2_rect.collidepoint(event.pos):
                    run_v2(screen)
                if v3_rect.collidepoint(event.pos):
                    run_v3(screen)
                if quit_rect.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

        pygame.display.flip()

main_menu()
