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
        # recent scores (most recent first)
        self.recent_scores = []
        self.all_scores = []

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
        # 1.5 LOAD PROFILE / TRAINING BUTTONS (menu corner)
        # ==========================================
        ICON_SIZE = 128
        def load_icon(name, fallback_color):
            try:
                img = load_img('anhgd2', name)
                img = img.convert_alpha()
                w, h = img.get_size()
                # if image is smaller than target, don't upscale to avoid blur: center it
                if w < ICON_SIZE or h < ICON_SIZE:
                    surf = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
                    surf.fill((0,0,0,0))
                    # center original image
                    rect = img.get_rect(center=(ICON_SIZE//2, ICON_SIZE//2))
                    surf.blit(img, rect)
                    return surf
                # otherwise scale smoothly to ICON_SIZE
                return pygame.transform.smoothscale(img, (ICON_SIZE, ICON_SIZE))
            except Exception:
                s = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
                s.fill(fallback_color)
                return s

        self.profile_img = load_icon('profile.png', (80, 80, 80))
        self.training_img = load_icon('training.png', (100, 100, 100))

        # position: top-right corner, with small margin
        margin = 12
        self.profile_rect = self.profile_img.get_rect(topright=(WIDTH - margin, margin))
        # place training to the left of profile with spacing (bigger icons -> bigger spacing)
        spacing = 16
        self.training_rect = self.training_img.get_rect(topright=(self.profile_rect.left - spacing, margin))

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
        # draw profile and training buttons at top-right with subtle shadow/outline
        try:
            for img, rect in ((self.training_img, self.training_rect), (self.profile_img, self.profile_rect)):
                # shadow
                shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                shadow.fill((0,0,0,100))
                shadow_rect = shadow.get_rect(topleft=(rect.x+3, rect.y+3))
                self.screen.blit(shadow, shadow_rect)
                # border
                try:
                    pygame.draw.rect(self.screen, (30,30,30), rect, 2)
                except Exception:
                    pass
                self.screen.blit(img, rect)
        except Exception:
            pass

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
        # Draw recent scores and top score in a panel on the left to avoid overlapping rank image
        try:
            panel_w = 380
            panel_h = 260
            panel_x = 40
            panel_y = 80
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((10, 10, 10, 200))
            pygame.draw.rect(panel, (200, 200, 200), (0, 0, panel_w, panel_h), 2)

            # Title: top score
            title_surf = self.font.render("HIGH SCORE", True, (240, 220, 60))
            panel.blit(title_surf, (12, 8))
            hs_text = self.small_font.render(str(self.high_score), True, (255, 255, 255))
            panel.blit(hs_text, (12, 8 + title_surf.get_height() + 6))

            # Recent scores list
            recent_title = self.small_font.render("Recent Scores:", True, (200, 200, 200))
            panel.blit(recent_title, (12, 8 + title_surf.get_height() + 6 + hs_text.get_height() + 8))
            ry = 8 + title_surf.get_height() + 6 + hs_text.get_height() + 8 + recent_title.get_height() + 6
            for i, sc in enumerate(self.recent_scores[:5]):
                try:
                    line = self.small_font.render(f"{i+1}. {sc}", True, (220, 220, 220))
                    panel.blit(line, (12, ry + i * (line.get_height() + 6)))
                except Exception:
                    pass

            # blit panel to screen
            self.screen.blit(panel, (panel_x, panel_y))
        except Exception:
            pass

    def draw_ingame_buttons(self):
        self.screen.blit(self.backhome_img, self.backhome_rect)
        self.screen.blit(self.pause_img, self.pause_rect)
        self.screen.blit(self.mute_img, self.mute_rect)

    def draw_hud(self, health, ammo=None, max_ammo=None):
        """Draw health bar, score, and optionally ammo count/bar.
        Place HP and ammo next to each other at top-left to avoid overlapping top-right buttons.
        """
        # left padding; nudge vertical down slightly to avoid cutting off text
        base_x = 12
        base_y = 28

        # HP bar (left)
        hp_bar_w = 180
        hp_bar_h = 18
        try:
            hp = max(0, min(health, 100)) if isinstance(health, (int, float)) else 0
            pygame.draw.rect(self.screen, (60, 60, 60), (base_x, base_y, hp_bar_w, hp_bar_h))
            fill_w = int(hp_bar_w * (hp / 100.0))
            pygame.draw.rect(self.screen, (200, 50, 50), (base_x, base_y, fill_w, hp_bar_h))
            pygame.draw.rect(self.screen, (220, 220, 220), (base_x, base_y, hp_bar_w, hp_bar_h), 2)
            hp_text = self.small_font.render(f"HP: {int(hp)}", True, WHITE)
            # place numeric just above the HP bar
            self.screen.blit(hp_text, (base_x + 6, base_y - hp_text.get_height() - 2))
        except Exception:
            try:
                hp_text = self.small_font.render(f"HP: {health}", True, WHITE)
                self.screen.blit(hp_text, (base_x, base_y))
            except Exception:
                pass

        # Ammo bar (to the right of HP)
        if ammo is not None and max_ammo is not None:
            try:
                gap = 12
                am_x = base_x + hp_bar_w + gap
                am_y = base_y
                am_text = self.small_font.render(f"Ammo: {int(ammo)}/{int(max_ammo)}", True, (255, 255, 255))
                # text above ammo bar
                self.screen.blit(am_text, (am_x, am_y - am_text.get_height() - 2))
                am_bar_w = 140
                am_bar_h = 12
                pygame.draw.rect(self.screen, (60, 60, 60), (am_x, am_y, am_bar_w, am_bar_h))
                fill_aw = int(am_bar_w * (max(0, ammo) / max(1, max_ammo)))
                pygame.draw.rect(self.screen, (80, 200, 120), (am_x, am_y, fill_aw, am_bar_h))
                pygame.draw.rect(self.screen, (200, 200, 200), (am_x, am_y, am_bar_w, am_bar_h), 2)
            except Exception:
                pass

        # score center-top
        try:
            score_text = self.small_font.render(f"SCORE: {self.score}", True, YELLOW)
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, base_y))
        except Exception:
            pass

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
            'training': self.training_rect,
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
        # Load recent scores from 'scores.txt' if present (most recent first), fallback to legacy highscore.txt
        try:
            scores = []
            if os.path.exists('scores.txt'):
                with open('scores.txt', 'r') as f:
                    for line in f:
                        try:
                            scores.append(int(line.strip()))
                        except Exception:
                            continue
            elif os.path.exists('highscore.txt'):
                # legacy single-value file
                try:
                    with open('highscore.txt', 'r') as f:
                        v = int(f.read().strip())
                        scores = [v]
                except Exception:
                    scores = []

            self.all_scores = scores
            self.recent_scores = list(self.all_scores)[:5]
            self.high_score = max(self.all_scores) if self.all_scores else 0
        except Exception:
            self.high_score = 0
            self.recent_scores = []
            self.all_scores = []

    def save_high_score(self):
        try:
            # also keep a legacy single-value file for compatibility
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def record_score(self, score):
        """Record a recently played score (most recent first) and persist to `scores.txt`.
        Also update `recent_scores` and `high_score`.
        """
        try:
            try:
                current = []
                if os.path.exists('scores.txt'):
                    with open('scores.txt', 'r') as f:
                        for line in f:
                            try:
                                current.append(int(line.strip()))
                            except Exception:
                                continue
            except Exception:
                current = []

            # insert newest at front
            current.insert(0, int(score))
            # keep a reasonable history
            current = current[:50]
            with open('scores.txt', 'w') as f:
                for s in current:
                    f.write(str(s) + '\n')

            self.all_scores = current
            self.recent_scores = list(self.all_scores)[:5]
            self.high_score = max(self.all_scores) if self.all_scores else 0
            # also update legacy highscore file
            try:
                with open('highscore.txt', 'w') as f:
                    f.write(str(self.high_score))
            except Exception:
                pass
        except Exception:
            pass
        # End of UI module. No top-level pygame.font or draw calls here.
