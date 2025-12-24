import pygame
import os
from settings import *

# ===== HÀM LOAD ẢNH AN TOÀN (Giúp chạy tốt trên cả Windows/Mac) =====
BASE_DIR = os.path.dirname(__file__)

def load_img(*path):
    # *path giúp nối chuỗi linh hoạt, ví dụ: load_img('anhgd2', 'play.png')
    return pygame.image.load(os.path.join(BASE_DIR, *path)).convert_alpha()

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)
        self.score = 0

        # ==========================================
        # 1. LOAD ẢNH MENU CHÍNH
        # ==========================================
        # Background
        original_bg = load_img('anhgd2', 'background_menu.png')
        scale_factor = 1.5
        new_width = int(original_bg.get_width() * scale_factor)
        new_height = int(original_bg.get_height() * scale_factor)
        self.bg_image = pygame.transform.scale(original_bg, (new_width, new_height))
        self.bg_rect = self.bg_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Instructions
        original_instr = load_img('anhgd2', 'howto.png')
        self.instructions_img = pygame.transform.scale(original_instr, (WIDTH, HEIGHT))
        self.instructions_rect = self.instructions_img.get_rect(topleft=(0, 0))

        # Buttons (Play, Quit, HowTo)
        button_width = 300
        button_height = 100

        self.restart_img = pygame.transform.scale(load_img('anhgd2', 'play.png'), (button_width, button_height))
        self.quit_img = pygame.transform.scale(load_img('anhgd2', 'quit.png'), (button_width, button_height))
        self.howto_img = pygame.transform.scale(load_img('anhgd2', 'instructions.png'), (button_width, button_height))

        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 145))

        # ==========================================
        # 2. LOAD ẢNH IN-GAME (Nút nhỏ góc phải)
        # ==========================================
        button_size = 80
        
        self.backhome_img = pygame.transform.scale(load_img('anhgd2', 'backhome.png'), (button_size, button_size))
        self.backhome_rect = self.backhome_img.get_rect(topright=(WIDTH - 20, 20))

        self.pause_img = pygame.transform.scale(load_img('anhgd2', 'pause.png'), (button_size, button_size))
        self.pause_rect = self.pause_img.get_rect(topright=(WIDTH - 20, 110))

        self.mute_img = pygame.transform.scale(load_img('anhgd2', 'mutesound.png'), (button_size, button_size))
        self.mute_rect = self.mute_img.get_rect(topright=(WIDTH - 20, 200))

        self.is_muted = False
        self.is_paused = False

        # ==========================================
        # 3. LOAD ẢNH GAME OVER (DEFEAT)
        # ==========================================
        try:
            # Ảnh nền Defeat (Sử dụng load_img cho đồng bộ)
            img_defeat_bg = load_img('anhgd2', 'defeat_bg.png')
            self.defeat_bg = pygame.transform.scale(img_defeat_bg, (WIDTH, HEIGHT))
            
            # Nút Quit (X) - Đặt ở góc trái dưới
            img_quit = load_img('anhgd2', 'btn_quit.png')
            self.btn_quit_over = pygame.transform.scale(img_quit, (100, 100)) 
            self.rect_quit_over = self.btn_quit_over.get_rect(bottomleft=(50, HEIGHT - 50))

            # Nút Play Again (Mũi tên) - Đặt ở góc phải dưới
            img_restart = load_img('anhgd2', 'btn_restart.png')
            self.btn_restart_over = pygame.transform.scale(img_restart, (100, 100)) 
            self.rect_restart_over = self.btn_restart_over.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
            # Nút Home (Trở về menu chính)
            img_home = load_img('anhgd2', 'mainmenu.png') # Tái sử dụng ảnh backhome hoặc dùng ảnh mới
            self.btn_home_over = pygame.transform.scale(img_home, (200, 200))
            self.rect_home_over = self.btn_home_over.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        except Exception as e:
            print(f"Lỗi tải ảnh Game Over: {e}")
            # Tạo màn hình đen dự phòng nếu lỗi ảnh
            self.defeat_bg = pygame.Surface((WIDTH, HEIGHT))
            self.defeat_bg.fill((50, 0, 0))

    # ================= DRAW FUNCTIONS =================

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.howto_img, self.howto_rect)

    def draw_instructions(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.instructions_img, self.instructions_rect)

    def draw_ingame_buttons(self):
        self.screen.blit(self.backhome_img, self.backhome_rect)
        self.screen.blit(self.pause_img, self.pause_rect)
        self.screen.blit(self.mute_img, self.mute_rect)

    def draw_hud(self, health):
        # Vẽ HP góc trái
        hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))

        # Vẽ Score ở giữa (để tránh đè lên nút Pause bên phải)
        score_text = self.small_font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (WIDTH // 2 - 50, 10))

    def draw_game_over(self):
        self.screen.blit(self.defeat_bg, (0, 0))
    
        # Vẽ 3 nút: Quit (Trái), Home (Giữa), Restart (Phải)
        self.screen.blit(self.btn_quit_over, self.rect_quit_over)
        self.screen.blit(self.btn_home_over, self.rect_home_over)
        self.screen.blit(self.btn_restart_over, self.rect_restart_over)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(score_text, score_rect)

    # ================= UTILS (GET RECTS) =================

    def get_button_rects(self): # Cho Menu chính
        return {
            'restart': self.restart_rect,
            'quit': self.quit_rect,
            'howto': self.howto_rect
        }

    def get_ingame_button_rects(self): # Cho màn hình Playing
        return {
            'backhome': self.backhome_rect,
            'pause': self.pause_rect,
            'mute': self.mute_rect
        }

    def get_game_over_buttons(self):
        return {
            'quit': self.rect_quit_over,
            'home': self.rect_home_over,   # Thêm nút home vào đây
            'restart': self.rect_restart_over
        }