import pygame
import os
from settings import *

# ===== HÀM LOAD ẢNH AN TOÀN =====
BASE_DIR = os.path.dirname(__file__)

def load_img(*path):
    return pygame.image.load(os.path.join(BASE_DIR, *path)).convert_alpha()


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)
        self.score = 0

        # ===== BACKGROUND MENU =====
        original_bg = load_img('anhgd2', 'background_menu.png')

        scale_factor = 1.5
        new_width = int(original_bg.get_width() * scale_factor)
        new_height = int(original_bg.get_height() * scale_factor)
        self.bg_image = pygame.transform.scale(original_bg, (new_width, new_height))
        self.bg_rect = self.bg_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # ===== INSTRUCTIONS =====
        original_instr = load_img('anhgd2', 'howto.png')
        self.instructions_img = pygame.transform.scale(original_instr, (WIDTH, HEIGHT))
        self.instructions_rect = self.instructions_img.get_rect(topleft=(0, 0))

        # ===== MENU BUTTONS =====
        button_width = 300
        button_height = 100

        self.restart_img = pygame.transform.scale(
            load_img('anhgd2', 'play.png'),
            (button_width, button_height)
        )

        self.quit_img = pygame.transform.scale(
            load_img('anhgd2', 'quit.png'),
            (button_width, button_height)
        )

        self.howto_img = pygame.transform.scale(
            load_img('anhgd2', 'instructions.png'),
            (button_width, button_height)
        )

        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 145))

        # ===== IN-GAME BUTTONS =====
        button_size = 80

        self.backhome_img = pygame.transform.scale(
            load_img('anhgd2', 'backhome.png'),
            (button_size, button_size)
        )
        self.backhome_rect = self.backhome_img.get_rect(topright=(WIDTH - 20, 20))

        self.pause_img = pygame.transform.scale(
            load_img('anhgd2', 'pause.png'),
            (button_size, button_size)
        )
        self.pause_rect = self.pause_img.get_rect(topright=(WIDTH - 20, 110))

        self.mute_img = pygame.transform.scale(
            load_img('anhgd2', 'mutesound.png'),
            (button_size, button_size)
        )
        self.mute_rect = self.mute_img.get_rect(topright=(WIDTH - 20, 200))

        self.is_muted = False
        self.is_paused = False

    # ================= DRAW =================

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        darkened = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        darkened.fill((0, 0, 0, 180))
        self.screen.blit(darkened, (0, 0))
        self.draw_menu()

    def draw_instructions(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.instructions_img, self.instructions_rect)

    def draw_ingame_buttons(self):
        self.screen.blit(self.backhome_img, self.backhome_rect)
        self.screen.blit(self.pause_img, self.pause_rect)
        self.screen.blit(self.mute_img, self.mute_rect)

    # ================= UTILS =================

    def get_button_rects(self):
        return {
            'restart': self.restart_rect,
            'quit': self.quit_rect,
            'howto': self.howto_rect
        }

    def get_ingame_button_rects(self):
        return {
            'backhome': self.backhome_rect,
            'pause': self.pause_rect,
            'mute': self.mute_rect
        }

    def draw_hud(self, health):
        hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))

        score_text = self.small_font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (WIDTH - 200, 10))
