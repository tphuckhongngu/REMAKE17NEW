# ui.py
import pygame
import json
import os
from settings import WIDTH, HEIGHT, FPS, TITLE

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.title_font = pygame.font.SysFont("arial", 72, bold=True)

        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 220, 0)
        self.RED = (200, 0, 0)
        self.GREEN = (0, 200, 0)
        self.BLACK = (0, 0, 0)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (40, 40, 40)

        # Biến trạng thái
        self.score = 0
        self.high_score = 0
        self.recent_scores = []
        self.is_paused = False

        # Load hình nút (nếu có, nếu không thì dùng hình chữ nhật)
        self.home_btn_img = self.load_button_image("home.png")
        self.settings_btn_img = self.load_button_image("lock.png")
        self.sound_btn_img = self.load_button_image("sound.png")
        self.continue_btn_img = self.load_button_image("continue.png")

        # Vị trí nút ingame (góc phải trên)
        btn_size = 60
        padding = 15
        self.home_btn_rect = pygame.Rect(WIDTH - btn_size - padding, padding, btn_size, btn_size)
        self.settings_btn_rect = pygame.Rect(WIDTH - btn_size - padding, padding + btn_size + 10, btn_size, btn_size)
        self.sound_btn_rect = pygame.Rect(WIDTH - btn_size - padding, padding + 2*(btn_size + 10), btn_size, btn_size)

        # Nút continue khi pause
        self.continue_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

        self.load_high_score()

    def load_button_image(self, filename):
        """Load ảnh nút từ thư mục assets/buttons, fallback hình vuông nếu thiếu"""
        try:
            path = os.path.join("assets", "buttons", filename)
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (60, 60))
        except Exception as e:
            # Fallback: hình tròn có chữ
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(surf, (70, 70, 70), (30, 30), 28)
            return surf

    def load_high_score(self):
        """Load high score và recent scores từ file"""
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
                    self.recent_scores = data.get("recent", [])
        except Exception as e:
            self.high_score = 0
            self.recent_scores = []

    def save_high_score(self):
        """Lưu high score và recent scores"""

        data = {
            "high_score": self.high_score,
            "recent": self.recent_scores[-9:]  # giữ 10 điểm gần nhất
        }
        with open("highscore.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def record_score(self, score):
        """Ghi điểm lần chơi này vào danh sách recent"""
        if score > 0:
            self.recent_scores.append(score)
            self.recent_scores.sort(reverse=True)

    def update_rank(self, score):
        """Cập nhật rank (dùng cho profile nếu cần)"""
        pass  # Có thể mở rộng sau

    def draw_hud(self, health, ammo=None, max_ammo=None):
        """Vẽ HUD trong game: HP, Ammo, Score"""
        # HP Bar
        bar_width = 200
        bar_height = 20
        x = 20
        y = 20

        pygame.draw.rect(self.screen, self.DARK_GRAY, (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, self.RED, (x, y, bar_width, bar_height))
        fill = (health / 100) * bar_width
        pygame.draw.rect(self.screen, self.GREEN if health > 30 else self.YELLOW if health > 10 else self.RED,
                         (x, y, fill, bar_height))

        hp_text = self.small_font.render(f"{int(health)}/100", True, self.WHITE)
        self.screen.blit(hp_text, (x + bar_width//2 - hp_text.get_width()//2, y + 2))

        # Ammo Bar (nếu có)
        if ammo is not None and max_ammo is not None:
            ammo_y = y + bar_height + 10
            pygame.draw.rect(self.screen, self.DARK_GRAY, (x - 2, ammo_y - 2, bar_width + 4, bar_height + 4))
            pygame.draw.rect(self.screen, (50, 50, 100), (x, ammo_y, bar_width, bar_height))
            ammo_fill = (ammo / max_ammo) * bar_width
            pygame.draw.rect(self.screen, (100, 180, 255), (x, ammo_y, ammo_fill, bar_height))

            ammo_text = self.small_font.render(f"{ammo}/{max_ammo}", True, self.WHITE)
            self.screen.blit(ammo_text, (x + bar_width//2 - ammo_text.get_width()//2, ammo_y + 2))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, self.YELLOW)
        self.screen.blit(score_text, (20, ammo_y + bar_height + 20 if ammo is not None else y + bar_height + 20))

    def draw_ingame_buttons(self):
        """Vẽ các nút góc phải trên: Home, Settings, Sound"""
        self.screen.blit(self.home_btn_img or pygame.Surface((60,60)), self.home_btn_rect.topleft)
        self.screen.blit(self.settings_btn_img or pygame.Surface((60,60)), self.settings_btn_rect.topleft)
        self.screen.blit(self.sound_btn_img or pygame.Surface((60,60)), self.sound_btn_rect.topleft)

    def draw_menu(self):
        """Menu chính"""
        self.screen.fill((20, 30, 50))

        title = self.title_font.render(TITLE, True, self.YELLOW)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(title, title_rect)

        # Nút Play
        play_text = self.big_font.render("PLAY", True, self.WHITE)
        play_rect = play_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        pygame.draw.rect(self.screen, self.GREEN, play_rect.inflate(40, 20), border_radius=15)
        self.screen.blit(play_text, play_rect)

        # Nút Training
        train_text = self.font.render("Training Mode", True, self.WHITE)
        train_rect = train_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        pygame.draw.rect(self.screen, (0, 120, 200), train_rect.inflate(30, 15), border_radius=10)
        self.screen.blit(train_text, train_rect)

        # High Score
        hs_text = self.small_font.render(f"High Score: {self.high_score}", True, self.YELLOW)
        self.screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, HEIGHT - 100))

    def draw_game_over(self):
        """Màn hình Game Over"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        go_text = self.big_font.render("GAME OVER", True, self.RED)
        go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(go_text, go_rect)

        score_text = self.font.render(f"Final Score: {self.score}", True, self.YELLOW)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(score_text, score_rect)

        if self.score > self.high_score:
            new_hs = self.big_font.render("NEW HIGH SCORE!", True, self.YELLOW)
            self.screen.blit(new_hs, new_hs.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        retry_text = self.font.render("Press ANY KEY to return to MENU", True, self.WHITE)
        retry_rect = retry_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        self.screen.blit(retry_text, retry_rect)

    def draw_pause(self):
        """Vẽ overlay khi pause (gọi từ draw() trong main nếu cần)"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.big_font.render("PAUSED", True, self.WHITE)
        self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))

        # Nút Continue
        if self.continue_btn_img:
            self.screen.blit(self.continue_btn_img, self.continue_btn_rect.topleft)
        else:
            pygame.draw.rect(self.screen, self.GREEN, self.continue_btn_rect, border_radius=15)
            cont_text = self.font.render("CONTINUE", True, self.WHITE)
            cont_rect = cont_text.get_rect(center=self.continue_btn_rect.center)
            self.screen.blit(cont_text, cont_rect)

    def draw_highscore_screen(self):
        """Màn hình bảng điểm (nếu bạn muốn thêm sau)"""
        self.screen.fill((10, 10, 30))
        title = self.big_font.render("HIGH SCORES", True, self.YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 100)))

        for i, score in enumerate(self.recent_scores[:10]):
            text = self.font.render(f"{i+1}. {score}", True, self.WHITE)
            self.screen.blit(text, (WIDTH//2 - 100, 200 + i*50))