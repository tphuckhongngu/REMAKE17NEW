import pygame
from settings import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)

        # Load hình nền menu/game over và làm NHỎ LẠI
        original_bg = pygame.image.load('anhgd2/background_menu.png').convert_alpha()
        
        # ***** CHỈNH KÍCH THƯỚC Ở ĐÂY *****
        scale_factor = 1.5  # Thử các giá trị: 0.5 (rất nhỏ), 0.6, 0.65, 0.7, 0.8 (lớn hơn)
        new_width = int(original_bg.get_width() * scale_factor)
        new_height = int(original_bg.get_height() * scale_factor)
        self.bg_image = pygame.transform.scale(original_bg, (new_width, new_height))
        
        # Đặt background nằm giữa màn hình
        self.bg_rect = self.bg_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Load ảnh hướng dẫn chơi (màn hình instructions)
        # Load ảnh hướng dẫn chơi (màn hình instructions) - FULL MÀN HÌNH
        original_instr = pygame.image.load('anhgd2/howto.png').convert_alpha()

        # Scale ảnh đúng bằng kích thước màn hình game (WIDTH x HEIGHT)
        self.instructions_img = pygame.transform.scale(original_instr, (WIDTH, HEIGHT))

        # Đặt vị trí top-left là (0, 0) để ảnh phủ kín toàn bộ màn hình
        self.instructions_rect = self.instructions_img.get_rect(topleft=(0, 0))

        # Load và scale các nút về cùng kích thước
        button_width = 300
        button_height = 100

        self.restart_img = pygame.image.load('anhgd2/play.png').convert_alpha()
        self.restart_img = pygame.transform.scale(self.restart_img, (button_width, button_height))

        self.quit_img = pygame.image.load('anhgd2/quit.png').convert_alpha()
        self.quit_img = pygame.transform.scale(self.quit_img, (button_width, button_height))

        # Nút HƯỚNG DẪN (thêm mới)
        self.howto_img = pygame.image.load('anhgd2/instructions.png').convert_alpha()
        self.howto_img = pygame.transform.scale(self.howto_img, (button_width, button_height))

        # Vị trí nút: đặt ở giữa phần bảng gỗ (thử nghiệm để đẹp mắt)
        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 145))  # dưới Quit

    def draw_menu(self):
        self.screen.fill((0, 0, 0))  # Nền đen
        self.screen.blit(self.bg_image, self.bg_rect)  # Background nằm giữa
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)  # hiện nút hướng dẫn

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        
        darkened = pygame.surface.Surface((WIDTH, HEIGHT)).convert_alpha()
        darkened.fill((0, 0, 0, 180))
        self.screen.blit(darkened, (0, 0))
        
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)  # hiện nút hướng dẫn (tùy chọn bỏ nếu không muốn ở Game Over)

    # Hàm mới: hiển thị ảnh hướng dẫn chơi
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
            'howto': self.howto_rect  # thêm howto vào dict
        }