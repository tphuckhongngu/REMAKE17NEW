import pygame
import os
from settings import *

BASE_DIR = os.path.dirname(__file__)

def load_img(*path):
    try:
        return pygame.image.load(os.path.join(BASE_DIR, *path)).convert_alpha()
    except:
        return None

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.is_paused = False
        self.is_muted = False
        self.about_mode = 0
        self.score = 0
        self.high_score = 0
        self.recent_scores = []
        self.recent_limit = 5
        self.all_scores = []
        self.has_played_highscore_sound = False
        self.showing_instructions = False
        self.current_slide = 0
        self.current_rank_index = 0

        # Continue button (pause)
        try:
            img = pygame.image.load(os.path.join("anh", "continue.png")).convert_alpha()
            self.continue_btn_img = pygame.transform.scale(img, (150, 50))
            self.continue_btn_rect = self.continue_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        except:
            self.continue_btn_img = None

        # Fonts (Vietnamese support)
        try:
            bundled = os.path.join(BASE_DIR, 'fonts', 'DejaVuSans.ttf')
            if os.path.exists(bundled):
                self.font = pygame.font.Font(bundled, 48)
                self.small_font = pygame.font.Font(bundled, 32)
            else:
                for name in ("segoeui", "tahoma", "arial", "dejavusans"):
                    path = pygame.font.match_font(name)
                    if path:
                        self.font = pygame.font.Font(path, 48)
                        self.small_font = pygame.font.Font(path, 32)
                        break
                else:
                    self.font = pygame.font.SysFont(None, 48)
                    self.small_font = pygame.font.SysFont(None, 32)
        except:
            self.font = pygame.font.SysFont(None, 48)
            self.small_font = pygame.font.SysFont(None, 32)

        # Menu backgrounds
        self.deep_menu_background = pygame.transform.scale(load_img('anhgd2', 'nentrencung.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))
        self.highscore_bg = pygame.transform.scale(load_img('anhgd2', 'highscore_background.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))

        bg = load_img('anhgd2', 'background_menu.png')
        if bg:
            scale = 0.4
            self.bg_image = pygame.transform.scale(bg, (int(bg.get_width() * scale), int(bg.get_height() * scale)))
        else:
            self.bg_image = pygame.Surface((100, 100))
        self.bg_rect = self.bg_image.get_rect(midtop=(WIDTH // 2, -150))

        # Main menu buttons
        btn_w, btn_h = 300, 100
        self.restart_img = pygame.transform.scale(load_img('anhgd2', 'play.png') or pygame.Surface((btn_w, btn_h)), (btn_w, btn_h))
        self.howto_img = pygame.transform.scale(load_img('anhgd2', 'instructions.png') or pygame.Surface((btn_w, btn_h)), (btn_w, btn_h))
        self.quit_img = pygame.transform.scale(load_img('anhgd2', 'quit.png') or pygame.Surface((btn_w, btn_h)), (btn_w, btn_h))
        self.highscore_img = pygame.transform.scale(load_img('anhgd2', 'highscore.png') or pygame.Surface((btn_w, btn_h)), (btn_w, btn_h))

        self.restart_rect = self.restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        self.howto_rect = self.howto_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.quit_rect = self.quit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        self.highscore_rect = self.highscore_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 230))

        # Corner icons
        ICON_SIZE = 90
        def load_icon(name, fallback):
            img = load_img('anhgd2', name)
            if img:
                w, h = img.get_size()
                if w < ICON_SIZE or h < ICON_SIZE:
                    surf = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
                    rect = img.get_rect(center=(ICON_SIZE//2, ICON_SIZE//2))
                    surf.blit(img, rect)
                    return surf
                return pygame.transform.smoothscale(img, (ICON_SIZE, ICON_SIZE))
            surf = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
            surf.fill(fallback)
            return surf

        self.profile_img = load_icon('profile.png', (80, 80, 80))
        self.training_img = load_icon('training.png', (100, 100, 100))

        margin = 12
        spacing = 16
        self.profile_rect = self.profile_img.get_rect(topright=(WIDTH - margin, margin))
        self.training_rect = self.training_img.get_rect(topright=(self.profile_rect.left - spacing, margin))

        # About Us
        self.about_us_bg = pygame.transform.scale(load_img('anhgd2', 'about.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))
        self.about_slides = []
        for name in ('about.png', 'about2.png', 'about3.png', 'about4.png'):
            img = load_img('anhgd2', name)
            if img:
                self.about_slides.append(pygame.transform.scale(img, (WIDTH, HEIGHT)))
        if not self.about_slides:
            self.about_slides.append(self.about_us_bg)

        self.about_button_img = pygame.transform.scale(load_img('anhgd2', 'aboutshe.png') or pygame.Surface((90, 90)), (90, 90))
        self.about_button_rect = self.about_button_img.get_rect(bottomleft=(40, HEIGHT - 40))

        # In-game buttons
        btn_size = 80
        self.backhome_img = pygame.transform.scale(load_img('anhgd2', 'backhome.png') or pygame.Surface((btn_size, btn_size)), (btn_size, btn_size))
        self.backhome_rect = self.backhome_img.get_rect(topright=(WIDTH - 20, 20))
        self.pause_img = pygame.transform.scale(load_img('anhgd2', 'pause.png') or pygame.Surface((btn_size, btn_size)), (btn_size, btn_size))
        self.pause_rect = self.pause_img.get_rect(topright=(WIDTH - 20, 110))
        self.mute_img = pygame.transform.scale(load_img('anhgd2', 'mutesound.png') or pygame.Surface((btn_size, btn_size)), (btn_size, btn_size))
        self.mute_rect = self.mute_img.get_rect(topright=(WIDTH - 20, 200))

        # Game Over / Victory
        self.defeat_bg = pygame.transform.scale(load_img('anhgd2', 'defeat_bg.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))
        self.victory_bg = pygame.transform.scale(load_img('anh', 'victory.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))

        # Game over buttons
        self.btn_quit_over = pygame.transform.scale(load_img('anhgd2', 'btn_quit.png') or pygame.Surface((100, 100)), (100, 100))
        self.rect_quit_over = self.btn_quit_over.get_rect(bottomleft=(50, HEIGHT - 50))

        self.btn_restart_over = pygame.transform.scale(load_img('anhgd2', 'btn_restart.png') or pygame.Surface((100, 100)), (100, 100))
        self.rect_restart_over = self.btn_restart_over.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))

        home_img = load_img('anhgd2', 'mainmenu.png') or pygame.Surface((200, 200))
        bright = pygame.transform.smoothscale(home_img, (400, 400))
        overlay = pygame.Surface(bright.get_size())
        overlay.fill((60, 60, 60))
        bright.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.btn_home_over = bright
        self.rect_home_over = self.btn_home_over.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))

        # Instructions slides
        self.instruction_slides = [
            pygame.transform.scale(load_img('anhgd2', f'guide{i}.png') or pygame.Surface((WIDTH, HEIGHT)), (WIDTH, HEIGHT))
            for i in range(1, 5)
        ]

        # Rank images
        self.rank_images = [None] * 8
        rank_dir = os.path.join(BASE_DIR, 'ranks')
        for i in range(1, 9):
            path = os.path.join(rank_dir, f'rank{i}.png')
            if os.path.exists(path):
                self.rank_images[i-1] = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (1100, 800))

        # Profiles
        try:
            from profilenpc import PROFILES as _PROFILES
        except:
            _PROFILES = []
        self.profiles = []
        for p in _PROFILES:
            prof = {'name': p.get('name', '???'), 'desc': p.get('desc', ''), 'portrait': None}
            portrait = p.get('portrait')
            if portrait:
                try:
                    prof['portrait'] = load_img(*portrait) if isinstance(portrait, (list, tuple)) else load_img(portrait)
                except:
                    pass
            self.profiles.append(prof)
        while len(self.profiles) < 5:
            self.profiles.append({'name': '???', 'desc': '', 'portrait': None})

        # Profile typing state
        self.profile_selected = 0
        self.profile_full_text = ''
        self.profile_display_text = ''
        self.profile_char_index = 0
        self.profile_typing_timer = 0
        self.profile_typing_delay = 2

    def get_rank_index(self, score):
        thresholds = [0, 100, 300, 800, 1300, 1800, 2300, 2800]
        for i, t in enumerate(thresholds):
            if score < t:
                return i - 1 if i > 0 else 0
        return 7

    def update_rank(self, score):
        self.current_rank_index = self.get_rank_index(score)

    def draw_menu(self):
        if self.about_mode > 0:
            idx = self.about_mode - 1
            if 0 <= idx < len(self.about_slides):
                self.screen.blit(self.about_slides[idx], (0, 0))
            return

        self.screen.blit(self.deep_menu_background, (0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.howto_img, self.howto_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.highscore_img, self.highscore_rect)
        self.screen.blit(self.about_button_img, self.about_button_rect)

        for img, rect in ((self.training_img, self.training_rect), (self.profile_img, self.profile_rect)):
            shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            self.screen.blit(shadow, (rect.x + 3, rect.y + 3))
            pygame.draw.rect(self.screen, (30, 30, 30), rect, 2)
            self.screen.blit(img, rect)

    def draw_instructions(self):
        if self.showing_instructions:
            self.screen.blit(self.instruction_slides[self.current_slide], (0, 0))

    def draw_highscore_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.highscore_bg, (0, 0))

        if self.rank_images[self.current_rank_index]:
            rank_rect = self.rank_images[self.current_rank_index].get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            self.screen.blit(self.rank_images[self.current_rank_index], rank_rect)

        recent_list = self.recent_scores[:self.recent_limit]
        panel_w = 380
        line_h = self.small_font.get_height()
        content_h = 80 + len(recent_list) * (line_h + 6)
        panel_h = max(260, content_h)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((10, 10, 10, 200))
        pygame.draw.rect(panel, (200, 200, 200), (0, 0, panel_w, panel_h), 2)

        y = 8
        title = self.font.render("HIGH SCORE", True, (240, 220, 60))
        panel.blit(title, (12, y))
        y += title.get_height() + 6
        hs = self.small_font.render(str(self.high_score), True, (255, 255, 255))
        panel.blit(hs, (12, y))
        y += hs.get_height() + 14
        recent_title = self.small_font.render("Recent Scores:", True, (200, 200, 200))
        panel.blit(recent_title, (12, y))
        y += recent_title.get_height() + 6

        for i, sc in enumerate(recent_list):
            line = self.small_font.render(f"{i+1}. {sc}", True, (220, 220, 220))
            panel.blit(line, (12, y))
            y += line.get_height() + 6

        self.screen.blit(panel, (40, 80))

    def draw_profile_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(210)
        self.screen.blit(overlay, (0, 0))

        panel_w = WIDTH - 120
        panel_h = HEIGHT - 140
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((18, 18, 18, 240))
        pygame.draw.rect(panel, (200, 200, 200), (0, 0, panel_w, panel_h), 2)

        sel = max(0, min(self.profile_selected, len(self.profiles) - 1))
        p = self.profiles[sel]

        por_w = por_h = 320
        por_x = 40
        por_y = 60
        por_rect = pygame.Rect(por_x, por_y, por_w, por_h)
        pygame.draw.rect(panel, (40, 40, 40), por_rect)
        pygame.draw.rect(panel, (150, 150, 150), por_rect, 2)

        if p.get('portrait'):
            img = pygame.transform.smoothscale(p['portrait'], (por_w - 12, por_h - 12))
            panel.blit(img, (por_x + 6, por_y + 6))
        else:
            qm = self.font.render('?', True, (200, 200, 200))
            panel.blit(qm, qm.get_rect(center=por_rect.center))

        desc_x = por_x + por_w + 30
        desc_y = por_y
        desc_w = panel_w - desc_x - 40

        if self.profile_full_text != p.get('desc', ''):
            self.profile_full_text = p.get('desc', '')
            self.profile_display_text = ''
            self.profile_char_index = 0
            self.profile_typing_timer = 0
        else:
            self.profile_typing_timer += 1
            if self.profile_typing_timer >= self.profile_typing_delay and self.profile_char_index < len(self.profile_full_text):
                self.profile_typing_timer = 0
                self.profile_char_index += 1
                self.profile_display_text = self.profile_full_text[:self.profile_char_index]

        name_s = self.font.render(p.get('name', '???'), True, (220, 200, 60))
        panel.blit(name_s, (desc_x, desc_y))

        words = (self.profile_display_text or '').split(' ')
        lines = []
        cur = ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if self.small_font.size(test)[0] > desc_w:
                if cur:
                    lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)

        ty = desc_y + name_s.get_height() + 12
        for line in lines[:10]:
            surf = self.small_font.render(line, True, (220, 220, 220))
            panel.blit(surf, (desc_x, ty))
            ty += surf.get_height() + 6

        ph_size = 96
        gap = 18
        ph_y = por_y + por_h + 24
        for i in range(1, 5):
            px = por_x + (i - 1) * (ph_size + gap)
            pygame.draw.rect(panel, (30, 30, 30), (px, ph_y, ph_size, ph_size))
            pygame.draw.rect(panel, (120, 120, 120), (px, ph_y, ph_size, ph_size), 1)
            try:
                ps = self.profiles[i]
                if ps.get('portrait'):
                    img = pygame.transform.smoothscale(ps['portrait'], (ph_size - 8, ph_size - 8))
                    panel.blit(img, (px + 4, ph_y + 4))
                else:
                    qm = self.font.render('?', True, (200, 200, 200))
                    panel.blit(qm, qm.get_rect(center=(px + ph_size // 2, ph_y + ph_size // 2)))
            except:
                qm = self.font.render('?', True, (200, 200, 200))
                panel.blit(qm, qm.get_rect(center=(px + ph_size // 2, ph_y + ph_size // 2)))

        back_size = 96
        back_x = panel_w - back_size - 20
        back_y = 12
        back_img = pygame.transform.smoothscale(self.btn_home_over, (back_size, back_size))
        panel.blit(back_img, (back_x, back_y))
        self.profile_back_rect = pygame.Rect(60 + back_x, 70 + back_y, back_size, back_size)

        slot_rects = [pygame.Rect(60 + por_x, 70 + por_y, por_w, por_h)]
        for i in range(1, 5):
            px = 60 + por_x + (i - 1) * (ph_size + gap)
            slot_rects.append(pygame.Rect(px, 70 + ph_y, ph_size, ph_size))
        self.profile_slot_rects = slot_rects

        self.screen.blit(panel, (60, 70))

    def start_profile(self, index=0):
        self.profile_selected = max(0, min(index, len(self.profiles) - 1))
        self.profile_full_text = self.profiles[self.profile_selected].get('desc', '')
        self.profile_display_text = ''
        self.profile_char_index = 0
        self.profile_typing_timer = 0

    def get_profile_click_rects(self):
        return {'back': getattr(self, 'profile_back_rect', None), 'slots': getattr(self, 'profile_slot_rects', [])}

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

    def get_menu_button_rects(self):
        return {
            'highscore': self.highscore_rect,
            'restart': self.restart_rect,
            'training': self.training_rect,
            'profile': self.profile_rect,
            'howto': self.howto_rect,
            'quit': self.quit_rect
        }

    def get_ingame_button_rects(self):
        return {'backhome': self.backhome_rect, 'pause': self.pause_rect, 'mute': self.mute_rect}

    def get_game_over_buttons(self):
        return {'quit': self.rect_quit_over, 'home': self.rect_home_over, 'restart': self.rect_restart_over}

    def draw_game_over(self):
        self.screen.blit(self.defeat_bg, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        score_s = self.small_font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
        self.screen.blit(score_s, score_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

        self.screen.blit(self.btn_quit_over, self.rect_quit_over)
        self.screen.blit(self.btn_restart_over, self.rect_restart_over)
        self.screen.blit(self.btn_home_over, self.rect_home_over)

    def draw_victory_screen(self):
        self.screen.blit(self.victory_bg or pygame.Surface((WIDTH, HEIGHT)).fill((20, 120, 20)), (0, 0))
        txt = self.font.render("Victory!", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        score_s = self.small_font.render(f"Score: {int(self.score)}", True, (240, 220, 60))
        self.screen.blit(score_s, score_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        self.screen.blit(self.btn_quit_over, self.rect_quit_over)
        self.screen.blit(self.btn_restart_over, self.rect_restart_over)
        self.screen.blit(self.btn_home_over, self.rect_home_over)

    def draw_hud(self, health, ammo=None, max_ammo=None):
        score_s = self.small_font.render(f"Score: {int(self.score)}", True, (240, 220, 60))
        self.screen.blit(score_s, score_s.get_rect(topleft=(12, 70)))

    def draw_ingame_buttons(self):
        self.screen.blit(self.backhome_img, self.backhome_rect)
        self.screen.blit(self.pause_img, self.pause_rect)
        self.screen.blit(self.mute_img, self.mute_rect)

    def load_high_score(self):
        scores = []
        if os.path.exists('scores.txt'):
            with open('scores.txt', 'r') as f:
                for line in f:
                    try:
                        scores.append(int(line.strip()))
                    except:
                        pass
        elif os.path.exists('highscore.txt'):
            try:
                with open('highscore.txt', 'r') as f:
                    scores = [int(f.read().strip())]
            except:
                pass
        self.all_scores = scores[:self.recent_limit]
        self.recent_scores = list(self.all_scores)
        self.high_score = max(self.all_scores) if self.all_scores else 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass

    def record_score(self, score):
        current = []
        if os.path.exists('scores.txt'):
            with open('scores.txt', 'r') as f:
                for line in f:
                    try:
                        current.append(int(line.strip()))
                    except:
                        pass
        current.insert(0, int(score))
        current = current[:self.recent_limit]
        with open('scores.txt', 'w') as f:
            for s in current:
                f.write(str(s) + '\n')
        self.all_scores = current
        self.recent_scores = list(current)
        self.high_score = max(current) if current else 0
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass