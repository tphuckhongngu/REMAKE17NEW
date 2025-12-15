import pygame
from settings import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)

    def draw_menu(self):
        self.screen.fill((20, 20, 20))
        title = self.font.render("SUPER SHOOTER TEAM 5", True, WHITE)
        play_text = self.small_font.render("Press SPACE to PLAY", True, YELLOW)
        self.screen.blit(title, (WIDTH//2 - 200, HEIGHT//3))
        self.screen.blit(play_text, (WIDTH//2 - 150, HEIGHT//2))
    #ssssssss
    def draw_game_over(self):
        self.screen.fill(BLACK)
        text = self.font.render("GAME OVER", True, RED)
        retry = self.small_font.render("Press SPACE to RESTART", True, WHITE)
        self.screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 20))
        self.screen.blit(retry, (WIDTH//2 - 160, HEIGHT//2 + 40))

    def draw_hud(self, health):
        hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))