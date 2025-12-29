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
        self.high_score = 0

        # ==========================================
        # 1. LOAD ẢNH MENU CHÍNH
        # ==========================================
        original_menu_bg = load_img('anhgd2', 'nentrencung.png')
        self.deep_menu_background = pygame.transform.scale(original_menu_bg, (WIDTH, HEIGHT))


        self.highscore_bg = load_img('anhgd2', 'highscore_background.png')
        self.highscore_bg = pygame.transform.scale(self.highscore_bg, (WIDTH, HEIGHT))

        original_bg = load_img('anhgd2', 'background_menu.png')
        scale_factor = 0.4
        new_width = int(original_bg.get_width() * scale_factor)
        new_height = int(original_bg.get_height() * scale_factor)
        self.bg_image = pygame.transform.scale(original_bg, (new_width, new_height))
        self.bg_rect = self.bg_image.get_rect(midtop=(WIDTH // 2, -150))

        button_width = 300
        button_height = 100

        self.restart_img = pygame.transform.scale(load_img('anhgd2', 'play.png'), (button_width, button_height))
        self.howto_img = pygame.transform.scale(load_img('anhgd2', 'instructions.png'), (button_width, button_height))
        self.quit_img = pygame.transform.scale(load_img('anhgd2', 'quit.png'), (button_width, button_height))
        self.highscore_img = pygame.transform.scale(load_img('anhgd2', 'highscore.png'), (button_width, button_height))

        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        self.highscore_rect = self.highscore_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 230))

        # ==========================================
        # 2. LOAD ẢNH IN-GAME
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
        # 3. LOAD ẢNH GAME OVER
        # ==========================================
        try:
            img_defeat_bg = load_img('anhgd2', 'defeat_bg.png')
            self.defeat_bg = pygame.transform.scale(img_defeat_bg, (WIDTH, HEIGHT))
            
            img_quit = load_img('anhgd2', 'btn_quit.png')
            self.btn_quit_over = pygame.transform.scale(img_quit, (100, 100)) 
            self.rect_quit_over = self.btn_quit_over.get_rect(bottomleft=(50, HEIGHT - 50))

            img_restart = load_img('anhgd2', 'btn_restart.png')
            self.btn_restart_over = pygame.transform.scale(img_restart, (100, 100)) 
            self.rect_restart_over = self.btn_restart_over.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))

            img_home = load_img('anhgd2', 'mainmenu.png')
            self.btn_home_over = pygame.transform.scale(img_home, (200, 200))
            self.rect_home_over = self.btn_home_over.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        except Exception as e:
            print(f"Lỗi tải ảnh Game Over: {e}")
            self.defeat_bg = pygame.Surface((WIDTH, HEIGHT))
            self.defeat_bg.fill((50, 0, 0))

        # ==========================================
        # 4. SLIDESHOW INSTRUCTIONS
        # ==========================================
        self.instruction_slides = []
        self.current_slide = 0
        self.showing_instructions = False

        self.instruction_slides.append(pygame.transform.scale(load_img('anhgd2', 'guide1.png'), (WIDTH, HEIGHT)))
        self.instruction_slides.append(pygame.transform.scale(load_img('anhgd2', 'guide2.png'), (WIDTH, HEIGHT)))
        self.instruction_slides.append(pygame.transform.scale(load_img('anhgd2', 'guide3.png'), (WIDTH, HEIGHT)))
        self.instruction_slides.append(pygame.transform.scale(load_img('anhgd2', 'guide4.png'), (WIDTH, HEIGHT)))

        # ===== RANK HÌNH ẢNH - CHỈ HIỂN THỊ Ở HIGH SCORE =====
        self.rank_images = [None] * 8
        self.current_rank_index = 0
        try:
            rank_dir = os.path.join(BASE_DIR, 'ranks')
            for i in range(1, 9):
                path = os.path.join(rank_dir, f'rank{i}.png')
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.rank_images[i-1] = pygame.transform.scale(img, (1100, 800))
                else:
                    print(f"Thiếu file: ranks/rank{i}.png")
        except Exception as e:
            print(f"Lỗi load rank images: {e}")

    def get_rank_index(self, score):
        if score < 100:
            return 0
        elif score < 300:
            return 1
        elif score < 800:
            return 2
        elif score < 1300:
            return 3
        elif score < 1800:
            return 4
        elif score < 2300:
            return 5
        elif score < 2800:
            return 6
        else:
            return 7

    def update_rank(self, score):
        self.current_rank_index = self.get_rank_index(score)

    # ================= DRAW FUNCTIONS =================

    def draw_menu(self):
        self.screen.blit(self.deep_menu_background, (0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.howto_img, self.howto_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.highscore_img, self.highscore_rect)

    def draw_instructions(self):
        if not self.showing_instructions:
            return
        self.screen.blit(self.instruction_slides[self.current_slide], (0, 0))

    def draw_highscore_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.highscore_bg, (0, 0))

        # Chỉ hiển thị hình rank ở đây
        if self.rank_images[self.current_rank_index] is not None:
            rank_img = self.rank_images[self.current_rank_index]
            rank_rect = rank_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            self.screen.blit(rank_img, rank_rect)

        

    def draw_ingame_buttons(self):
        self.screen.blit(self.backhome_img, self.backhome_rect)
        self.screen.blit(self.pause_img, self.pause_rect)
        self.screen.blit(self.mute_img, self.mute_rect)

    def draw_hud(self, health):
        hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
        self.screen.blit(hp_text, (10, 10))

        score_text = self.small_font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (WIDTH // 2 - 50, 10))

    def draw_game_over(self):
        self.screen.blit(self.defeat_bg, (0, 0))
        
        self.screen.blit(self.btn_quit_over, self.rect_quit_over)
        self.screen.blit(self.btn_home_over, self.rect_home_over)
        self.screen.blit(self.btn_restart_over, self.rect_restart_over)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(score_text, score_rect)

    

    # ================= SLIDESHOW INSTRUCTIONS =================
    def start_instructions(self):
        self.showing_instructions = True
        self.current_slide = 0

    def next_slide(self):
        self.current_slide += 1
        if self.current_slide >= len(self.instruction_slides):
            self.showing_instructions = False
            self.current_slide = 0
            return True
        return False

    # ================= GET BUTTON RECTS =================
    def get_menu_button_rects(self):
        return {
            'highscore': self.highscore_rect,
            'restart': self.restart_rect,
            'howto': self.howto_rect,
            'quit': self.quit_rect
        }

    def get_ingame_button_rects(self):
        return {
            'backhome': self.backhome_rect,
            'pause': self.pause_rect,
            'mute': self.mute_rect
        }

    def get_game_over_buttons(self):
        return {
            'quit': self.rect_quit_over,
            'home': self.rect_home_over,
            'restart': self.rect_restart_over
        }

    # ================= HIGH SCORE SAVE / LOAD =================
    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = int(f.read().strip())
        except:
            self.high_score = 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    font = pygame.font.SysFont(None, 24)
draw_skill_ui(screen, player, font)
player.draw_shield(screen)
