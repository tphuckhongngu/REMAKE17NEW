import pygame
import os
from settings import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)

        base_path = os.path.dirname(__file__)
        img_path = os.path.join(base_path, 'anhgd2')

        # Load hình nền menu
        original_bg = pygame.image.load(
            os.path.join(img_path, 'background_menu.png')
        ).convert_alpha()

        scale_factor = 1.5
        new_width = int(original_bg.get_width() * scale_factor)
        new_height = int(original_bg.get_height() * scale_factor)
        self.bg_image = pygame.transform.scale(original_bg, (new_width, new_height))
        self.bg_rect = self.bg_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Load ảnh hướng dẫn FULL màn hình
        original_instr = pygame.image.load(
            os.path.join(img_path, 'howto.png')
        ).convert_alpha()
        self.instructions_img = pygame.transform.scale(original_instr, (WIDTH, HEIGHT))
        self.instructions_rect = self.instructions_img.get_rect(topleft=(0, 0))

        # Kích thước nút
        button_width = 300
        button_height = 100

        self.restart_img = pygame.transform.scale(
            pygame.image.load(os.path.join(img_path, 'play.png')).convert_alpha(),
            (button_width, button_height)
        )

        self.quit_img = pygame.transform.scale(
            pygame.image.load(os.path.join(img_path, 'quit.png')).convert_alpha(),
            (button_width, button_height)
        )

        self.howto_img = pygame.transform.scale(
            pygame.image.load(os.path.join(img_path, 'instructions.png')).convert_alpha(),
            (button_width, button_height)
        )

        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 145))

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        darkened = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darkened.fill((0, 0, 0, 180))
        self.screen.blit(darkened, (0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)

    def draw_instructions(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.instructions_img, self.instructions_rect)

    def draw_hud(self, health):
        hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))

    def get_button_rects(self):
        return {
            'restart': self.restart_rect,
            'quit': self.quit_rect,
            'howto': self.howto_rect
        }
