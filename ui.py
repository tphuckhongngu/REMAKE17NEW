import pygame
import os
from settings import *

# ===== HÀM LOAD ẢNH AN TOÀN =====
BASE_DIR = os.path.dirname(__file__)

def load_img(*path):
    return pygame.image.load(os.path.join(BASE_DIR, *path)).convert_alpha()

class UI:
    def __init__(self, screen):

        # === NÚT ABOUT US ĐỘC LẬP ===
       
        # Trạng thái: 0 = menu bình thường, 1 = slide 1, 2 = slide 2, ...
        self.about_mode = 0

        self.screen = screen
        self.is_paused = False
        try:
            path_cont = os.path.join("anh", "continue.png")
            self.continue_btn_img = pygame.image.load(path_cont).convert_alpha()
            # DÒNG QUAN TRỌNG: Thay đổi (150, 50) theo ý bạn
            self.continue_btn_img = pygame.transform.scale(self.continue_btn_img, (150, 50))
            self.continue_btn_rect = self.continue_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        except Exception as e:
            self.continue_btn_img = None
        # Prefer a bundled font that includes Vietnamese glyphs (DejaVu Sans),
        # fall back to common system fonts then to default.
        try:
            fonts_dir = os.path.join(BASE_DIR, 'fonts')
            bundled = os.path.join(fonts_dir, 'DejaVuSans.ttf')
            if os.path.exists(bundled):
                try:
                    self.font = pygame.font.Font(bundled, 48)
                    self.small_font = pygame.font.Font(bundled, 32)
                except Exception:
                    self.font = pygame.font.SysFont('arial', 48)
                    self.small_font = pygame.font.SysFont('arial', 32)
            else:
                # try common system fonts
                found = False
                for name in ("segoeui", "tahoma", "arial", "dejavusans"):
                    path = pygame.font.match_font(name)
                    if path:
                        try:
                            self.font = pygame.font.Font(path, 48)
                            self.small_font = pygame.font.Font(path, 32)
                            found = True
                            break
                        except Exception:
                            continue
                if not found:
                    self.font = pygame.font.SysFont(None, 48)
                    self.small_font = pygame.font.SysFont(None, 32)
        except Exception:
            self.font = pygame.font.SysFont(None, 48)
            self.small_font = pygame.font.SysFont(None, 32)
        self.score = 0
        self.high_score = 0
        # recent scores (most recent first)
        self.recent_scores = []
        # max number of recent scores to display
        self.recent_limit = 5
        self.all_scores = []
        
        self.has_played_highscore_sound = False
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
        ICON_SIZE = 90
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

        # === ABOUT US - GIỮ NGUYÊN BIẾN CŨ + THÊM STORY SLIDES ===
        # Giữ nguyên biến cũ như bạn yêu cầu
        self.about_us_bg = pygame.transform.scale(load_img('anhgd2', 'about.png'), (WIDTH, HEIGHT))

        # Danh sách slide mới (story mode)
        self.about_slides = []
        try:
            self.about_slides.append(pygame.transform.scale(load_img('anhgd2', 'about.png'), (WIDTH, HEIGHT)))      # Slide 1 (cùng với about_us_bg cũ)
            self.about_slides.append(pygame.transform.scale(load_img('anhgd2', 'about2.png'), (WIDTH, HEIGHT)))     # Slide 2
            self.about_slides.append(pygame.transform.scale(load_img('anhgd2', 'about3.png'), (WIDTH, HEIGHT)))     # Slide 3
            self.about_slides.append(pygame.transform.scale(load_img('anhgd2', 'about4.png'), (WIDTH, HEIGHT)))     # Slide cuối
            # Thêm about5.png, about6.png... nếu cần
        except Exception as e:
            # Fallback: ít nhất có slide đầu
            if not self.about_slides:
                self.about_slides.append(self.about_us_bg)  # dùng biến cũ làm fallback

        # Nút About Us nhỏ góc trái dưới
        self.about_button_img = pygame.transform.scale(load_img('anhgd2', 'aboutshe.png'), (90, 90))
        self.about_button_rect = self.about_button_img.get_rect(bottomleft=(40, HEIGHT - 40))

        # Trạng thái: 0 = menu bình thường, 1 = slide 1, 2 = slide 2, ...
        self.about_mode = 0

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
            # make the main menu/home button brighter and twice as large
            try:
                # scale up to double size (was 200x200 -> now 400x400)
                bright = pygame.transform.smoothscale(img_home, (400, 400))
                # create a light overlay and add it to brighten the image
                overlay = pygame.Surface(bright.get_size())
                overlay.fill((60, 60, 60))
                bright.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.btn_home_over = bright
            except Exception:
                self.btn_home_over = pygame.transform.scale(img_home, (400, 400))
            self.rect_home_over = self.btn_home_over.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        except Exception as e:
            self.defeat_bg = pygame.Surface((WIDTH, HEIGHT))
            self.defeat_bg.fill((50, 0, 0))

        # ==========================================
        # 3.5 LOAD VICTORY IMAGE
        # ==========================================
        try:
            img_victory = load_img('anh', 'victory.png')
            self.victory_bg = pygame.transform.scale(img_victory, (WIDTH, HEIGHT))
        except Exception as e:
            self.victory_bg = None

        # Ensure game-over button surfaces and rects exist even if image loading failed
        try:
            if not hasattr(self, 'btn_quit_over') or self.btn_quit_over is None:
                s = pygame.Surface((100, 100), pygame.SRCALPHA)
                s.fill((120, 20, 20))
                self.btn_quit_over = s
                self.rect_quit_over = s.get_rect(bottomleft=(50, HEIGHT - 50))
        except Exception:
            try:
                self.rect_quit_over = pygame.Rect(50, HEIGHT - 150, 100, 100)
            except Exception:
                self.rect_quit_over = None

        try:
            if not hasattr(self, 'btn_restart_over') or self.btn_restart_over is None:
                s = pygame.Surface((100, 100), pygame.SRCALPHA)
                s.fill((20, 120, 20))
                self.btn_restart_over = s
                self.rect_restart_over = s.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
        except Exception:
            try:
                self.rect_restart_over = pygame.Rect(WIDTH - 150, HEIGHT - 150, 100, 100)
            except Exception:
                self.rect_restart_over = None

        try:
            if not hasattr(self, 'btn_home_over') or self.btn_home_over is None:
                s = pygame.Surface((200, 200), pygame.SRCALPHA)
                s.fill((60, 60, 140))
                self.btn_home_over = s
                self.rect_home_over = s.get_rect(midbottom=(WIDTH // 2, HEIGHT - 10))
        except Exception:
            try:
                self.rect_home_over = pygame.Rect((WIDTH // 2) - 100, HEIGHT - 210, 200, 200)
            except Exception:
                self.rect_home_over = None

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
        rank_dir = os.path.join(BASE_DIR, 'ranks')
        for i in range(1, 9):
            path = os.path.join(rank_dir, f'rank{i}.png')
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.rank_images[i-1] = pygame.transform.scale(img, (1100, 800))


        # ================= PROFILES / CHARACTER CODex =================
        # Load profiles from separate module so they can be edited later
        try:
            from profilenpc import PROFILES as _PROFILES
        except Exception:
            _PROFILES = []

        self.profiles = []
        for p in _PROFILES:
            prof = {'name': p.get('name', '???'), 'desc': p.get('desc', ''), 'portrait': None}
            portrait = p.get('portrait')
            if portrait:
                try:
                    # portrait may be tuple like ('npc','anhnpc.png') or string
                    if isinstance(portrait, (list, tuple)):
                        img = load_img(*portrait)
                    else:
                        img = load_img(portrait)
                    prof['portrait'] = img
                except Exception:
                    prof['portrait'] = None
            self.profiles.append(prof)

        # ensure we always have 5 slots
        while len(self.profiles) < 5:
            self.profiles.append({'name': '???', 'desc': '', 'portrait': None})

        # Profile typing state (for description typewriter)
        self.profile_selected = 0
        self.profile_full_text = ''
        self.profile_display_text = ''
        self.profile_char_index = 0
        self.profile_typing_timer = 0
        self.profile_typing_delay = 2

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
        # === ABOUT US STORY MODE - CHỈ HIỂN THỊ KHI about_mode > 0 ===
        if self.about_mode > 0:
            slide_index = self.about_mode - 1
            if 0 <= slide_index < len(self.about_slides):
                self.screen.blit(self.about_slides[slide_index], (0, 0))
            return  # Che hết menu

        # === MENU BÌNH THƯỜNG ===
        self.screen.blit(self.deep_menu_background, (0, 0))
        self.screen.blit(self.bg_image, self.bg_rect)
        self.screen.blit(self.restart_img, self.restart_rect)
        self.screen.blit(self.howto_img, self.howto_rect)
        self.screen.blit(self.quit_img, self.quit_rect)
        self.screen.blit(self.highscore_img, self.highscore_rect)
        self.screen.blit(self.about_button_img, self.about_button_rect)
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
            # compute dynamic panel height based on fonts and number of recent scores
            recent_list = self.recent_scores[:self.recent_limit]
            title_h = self.font.get_height()
            hs_h = self.small_font.get_height()
            recent_title_h = self.small_font.get_height()
            line_h = self.small_font.get_height()
            spacing = 6
            padding_top = 8
            padding_bottom = 12
            content_h = (padding_top + title_h + 6 + hs_h + 8 + recent_title_h + 6 +
                         len(recent_list) * (line_h + spacing) + padding_bottom)
            panel_h = max(260, content_h)
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
            for i, sc in enumerate(recent_list):
                try:
                    line = self.small_font.render(f"{i+1}. {sc}", True, (220, 220, 220))
                    panel.blit(line, (12, ry + i * (line.get_height() + 6)))
                except Exception:
                    pass

            # blit panel to screen
            self.screen.blit(panel, (panel_x, panel_y))
        except Exception:
            pass

    def draw_profile_screen(self):
        try:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(210)
            self.screen.blit(overlay, (0, 0))

            # panel background
            panel_w = WIDTH - 120
            panel_h = HEIGHT - 140
            panel_x = 60
            panel_y = 70
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((18, 18, 18, 240))
            pygame.draw.rect(panel, (200, 200, 200), (0, 0, panel_w, panel_h), 2)

            # selected profile large view
            sel = max(0, min(self.profile_selected, len(self.profiles)-1))
            p = self.profiles[sel]

            # left portrait area (large)
            por_w = 320
            por_h = 320
            por_x = 40
            por_y = 60
            por_rect = pygame.Rect(por_x, por_y, por_w, por_h)
            pygame.draw.rect(panel, (40,40,40), por_rect)
            pygame.draw.rect(panel, (150,150,150), por_rect, 2)
            if p.get('portrait'):
                try:
                    img = pygame.transform.smoothscale(p['portrait'], (por_w-12, por_h-12))
                    panel.blit(img, (por_x+6, por_y+6))
                except Exception:
                    qm = self.font.render('?', True, (200,200,200))
                    panel.blit(qm, (por_x + (por_w-qm.get_width())//2, por_y + (por_h-qm.get_height())//2))
            else:
                qm = self.font.render('?', True, (200,200,200))
                panel.blit(qm, (por_x + (por_w-qm.get_width())//2, por_y + (por_h-qm.get_height())//2))

            # right description area with typewriter
            desc_x = por_x + por_w + 30
            desc_y = por_y
            desc_w = panel_w - desc_x - 40
            # typing logic
            if self.profile_full_text != p.get('desc', ''):
                self.profile_full_text = p.get('desc', '')
                self.profile_display_text = ''
                self.profile_char_index = 0
                self.profile_typing_timer = 0
            else:
                self.profile_typing_timer += 1
                if self.profile_typing_timer >= self.profile_typing_delay:
                    self.profile_typing_timer = 0
                    if self.profile_char_index < len(self.profile_full_text):
                        self.profile_char_index += 1
                        self.profile_display_text = self.profile_full_text[:self.profile_char_index]

            name_s = self.font.render(p.get('name', '???'), True, (220,200,60))
            panel.blit(name_s, (desc_x, desc_y))

            # wrap and draw profile_display_text
            try:
                text = self.profile_display_text or ''
                words = text.split(' ')
                cur = ''
                lines = []
                for w in words:
                    test = (cur + ' ' + w).strip()
                    ts = self.small_font.render(test, True, (220,220,220))
                    if ts.get_width() > desc_w:
                        if cur:
                            lines.append(cur)
                        cur = w
                    else:
                        cur = test
                if cur:
                    lines.append(cur)
                ty = desc_y + name_s.get_height() + 12
                for i, line in enumerate(lines[:10]):
                    panel.blit(self.small_font.render(line, True, (220,220,220)), (desc_x, ty + i * (self.small_font.get_height() + 6)))
            except Exception:
                pass

            # thumbnails for other profiles below portrait (show image if available)
            try:
                ph_x = por_x
                ph_y = por_y + por_h + 24
                ph_size = 96
                gap = 18
                for i in range(1,5):
                    px = ph_x + (i-1) * (ph_size + gap)
                    pygame.draw.rect(panel, (30,30,30), (px, ph_y, ph_size, ph_size))
                    pygame.draw.rect(panel, (120,120,120), (px, ph_y, ph_size, ph_size), 1)
                    # get profile index i (if exists)
                    try:
                        psmall = self.profiles[i]
                    except Exception:
                        psmall = None
                    if psmall and psmall.get('portrait'):
                        try:
                            timg = pygame.transform.smoothscale(psmall['portrait'], (ph_size-8, ph_size-8))
                            panel.blit(timg, (px+4, ph_y+4))
                        except Exception:
                            qm = self.font.render('?', True, (200,200,200))
                            panel.blit(qm, (px + (ph_size - qm.get_width())//2, ph_y + (ph_size - qm.get_height())//2))
                    else:
                        qm = self.font.render('?', True, (200,200,200))
                        panel.blit(qm, (px + (ph_size - qm.get_width())//2, ph_y + (ph_size - qm.get_height())//2))
            except Exception:
                pass

            # prepare clickable rects (absolute coordinates)
            try:
                # back button (use home image scaled)
                try:
                    back_size = 96
                    back_img = pygame.transform.smoothscale(self.btn_home_over, (back_size, back_size))
                except Exception:
                    back_img = None
                    back_size = 64
                back_x = panel_x + panel_w - (back_size + 20)
                back_y = panel_y + 12
                if back_img is not None:
                    panel.blit(back_img, (back_x - panel_x, back_y - panel_y))
                self.profile_back_rect = pygame.Rect(back_x, back_y, back_size, back_size)

                # slot rects: index 0 = large portrait, 1-4 = small placeholders
                slot_rects = []
                # portrait rect absolute
                slot_rects.append(pygame.Rect(panel_x + por_x, panel_y + por_y, por_w, por_h))
                ph_x = por_x
                ph_y = por_y + por_h + 24
                ph_size = 96
                gap = 18
                for i in range(1,5):
                    px = panel_x + ph_x + (i-1) * (ph_size + gap)
                    py = panel_y + ph_y
                    slot_rects.append(pygame.Rect(px, py, ph_size, ph_size))
                self.profile_slot_rects = slot_rects

            except Exception:
                self.profile_back_rect = None
                self.profile_slot_rects = []

            # blit panel
            self.screen.blit(panel, (panel_x, panel_y))
        except Exception:
            pass

    def start_profile(self, index=0):
        try:
            self.profile_selected = max(0, min(index, len(self.profiles)-1))
            self.profile_full_text = self.profiles[self.profile_selected].get('desc', '')
            self.profile_display_text = ''
            self.profile_char_index = 0
            self.profile_typing_timer = 0
        except Exception:
            pass

    def get_profile_click_rects(self):
        """Return dict with clickable rects on the profile screen: 'back' and 'slots' list.
        Must be called after draw_profile_screen was used (rects are stored on the UI instance).
        """
        out = {
            'back': getattr(self, 'profile_back_rect', None),
            'slots': getattr(self, 'profile_slot_rects', [])
        }
        return out

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
            'profile': self.profile_rect,
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

    def draw_game_over(self):
        """Draw the game over / defeat screen. Safe if images/rects missing."""
        try:
            # background (full-screen defeat image if available)
            try:
                self.screen.blit(self.defeat_bg, (0, 0))
            except Exception:
                try:
                    bg = pygame.Surface((WIDTH, HEIGHT))
                    bg.fill((30, 0, 0))
                    self.screen.blit(bg, (0, 0))
                except Exception:
                    pass

            # dark overlay for readability
            try:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, (0, 0))
            except Exception:
                pass

            # Title intentionally omitted per user request

            # Score
            try:
                score_s = self.small_font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
                self.screen.blit(score_s, score_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            except Exception:
                pass

            # draw buttons: quit (bottom-left), restart (bottom-right), home (center-bottom)
            try:
                if getattr(self, 'btn_quit_over', None) and getattr(self, 'rect_quit_over', None):
                    self.screen.blit(self.btn_quit_over, self.rect_quit_over)
            except Exception:
                pass
            try:
                if getattr(self, 'btn_restart_over', None) and getattr(self, 'rect_restart_over', None):
                    self.screen.blit(self.btn_restart_over, self.rect_restart_over)
            except Exception:
                pass
            try:
                if getattr(self, 'btn_home_over', None) and getattr(self, 'rect_home_over', None):
                    self.screen.blit(self.btn_home_over, self.rect_home_over)
            except Exception:
                pass

            # helper hint intentionally removed per user request
        except Exception:
            try:
                self.screen.fill((0, 0, 0))
            except Exception:
                pass

    def draw_victory_screen(self):
        """Draw a simple victory screen using anh/victory.png if available."""
        try:
            if self.victory_bg:
                self.screen.blit(self.victory_bg, (0, 0))
            else:
                bg = pygame.Surface((WIDTH, HEIGHT))
                bg.fill((20, 120, 20))
                self.screen.blit(bg, (0, 0))
            # overlay text
            try:
                txt = self.font.render("Victory!", True, (255, 255, 255))
                self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            except Exception:
                pass
            try:
                score_s = self.small_font.render(f"Score: {int(self.score)}", True, (240, 220, 60))
                self.screen.blit(score_s, score_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            except Exception:
                pass

            # draw the same buttons as game over so player can restart or go home
            try:
                if getattr(self, 'btn_quit_over', None) and getattr(self, 'rect_quit_over', None):
                    self.screen.blit(self.btn_quit_over, self.rect_quit_over)
            except Exception:
                pass
            try:
                if getattr(self, 'btn_restart_over', None) and getattr(self, 'rect_restart_over', None):
                    self.screen.blit(self.btn_restart_over, self.rect_restart_over)
            except Exception:
                pass
            try:
                if getattr(self, 'btn_home_over', None) and getattr(self, 'rect_home_over', None):
                    self.screen.blit(self.btn_home_over, self.rect_home_over)
            except Exception:
                pass
        except Exception:
            try:
                self.screen.fill((0, 0, 0))
            except Exception:
                pass

    # ================= IN-GAME HUD & BUTTONS =================
    def draw_hud(self, health, ammo=None, max_ammo=None):
        try:
            # Only draw the score label here; detailed health/ammo are drawn by Player methods
            try:
                # place score to the left, below the player's ammo bar
                hud_x = 12
                hud_y = 12
                bar_h = 18
                gap = 12
                ammo_top = hud_y + bar_h + gap
                score_y = ammo_top + bar_h + 8
                score_s = self.small_font.render(f"Score: {int(self.score)}", True, (240, 220, 60))
                self.screen.blit(score_s, score_s.get_rect(topleft=(hud_x, score_y)))
            except Exception:
                pass
        except Exception:
            pass

    def draw_ingame_buttons(self):
        try:
            # draw right-side buttons: backhome, pause, mute
            try:
                if getattr(self, 'backhome_img', None) and getattr(self, 'backhome_rect', None):
                    self.screen.blit(self.backhome_img, self.backhome_rect)
            except Exception:
                pass
            try:
                if getattr(self, 'pause_img', None) and getattr(self, 'pause_rect', None):
                    self.screen.blit(self.pause_img, self.pause_rect)
            except Exception:
                pass
            try:
                if getattr(self, 'mute_img', None) and getattr(self, 'mute_rect', None):
                    self.screen.blit(self.mute_img, self.mute_rect)
            except Exception:
                pass
        except Exception:
            pass

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

            # keep only the most recent `recent_limit` scores
            self.all_scores = list(scores)[:self.recent_limit]
            self.recent_scores = list(self.all_scores)
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
            # keep only the most recent `recent_limit` scores and discard the rest
            current = current[:self.recent_limit]
            with open('scores.txt', 'w') as f:
                for s in current:
                    f.write(str(s) + '\n')

            self.all_scores = current
            self.recent_scores = list(self.all_scores)
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