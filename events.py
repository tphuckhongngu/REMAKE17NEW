import pygame
from sounds import SoundManager
import sys


class EventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self):
        for event in pygame.event.get():

            # THOÁT GAME
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # DỪNG TIẾNG NẠP ĐẠN KHI HẾT TIMER
            if event.type == pygame.USEREVENT + 1:
                SoundManager.stop_reload_sound()

            # CLICK CHUỘT TRÁI
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.handle_mouse_click(mx, my)

            # NHẤN PHÍM
            if event.type == pygame.KEYDOWN:
                # ESC: quay về menu từ instructions hoặc pause trong game
                if event.key == pygame.K_ESCAPE:
                    if self.game.game_state == "INSTRUCTIONS":
                        SoundManager.play_click_sound()
                        self.game.game_state = "MENU"
                    elif self.game.game_state == "PLAYING":
                        SoundManager.play_click_sound()
                        self.game.ui.is_paused = not self.game.ui.is_paused

                # ENTER: tiến thoại NPC
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if getattr(self.game, 'npc', None) is not None:
                        self.game.npc.advance()

                # F11: toggle fullscreen
                if event.key == pygame.K_F11:
                    self.game.toggle_fullscreen()

    def handle_mouse_click(self, mx, my):
        state = self.game.game_state

        # =================================================
        # 1. MENU CHÍNH
        # =================================================
        if state == "MENU":
            ui = self.game.ui

            # Nút About nhỏ góc trái dưới → bắt đầu story slide
            if ui.about_button_rect.collidepoint(mx, my):
                SoundManager.play_click_sound()
                ui.about_mode = 1  # slide đầu tiên
                return

            # Đang xem About story → click bất kỳ đâu để chuyển slide tiếp
            if ui.about_mode > 0:
                SoundManager.play_click_sound()
                ui.about_mode += 1
                # Nếu hết slide → quay về menu
                if ui.about_mode > len(ui.about_slides):
                    ui.about_mode = 0
                return  # Quan trọng: ngăn các nút menu khác bị kích hoạt

            # Các nút menu chính
            buttons = ui.get_menu_button_rects()

            if buttons['restart'].collidepoint(mx, my):  # Play
                SoundManager.play_click_sound()
                self.game.new_game(tutorial=False)

            elif buttons['training'].collidepoint(mx, my):  # Training
                SoundManager.play_click_sound()
                self.game.start_training()

            elif buttons['quit'].collidepoint(mx, my):  # Quit
                SoundManager.play_click_sound()
                pygame.quit()
                sys.exit()

            elif buttons['howto'].collidepoint(mx, my):  # Instructions
                SoundManager.play_click_sound()
                self.game.game_state = "INSTRUCTIONS"
                ui.start_instructions()

            elif buttons['highscore'].collidepoint(mx, my):  # Highscore
                SoundManager.play_click_sound()
                ui.update_rank(ui.high_score)
                self.game.game_state = "HIGHSCORE"
                if not self.game.ui.has_played_highscore_sound:
                    SoundManager.play_highscore_sound()
                    self.game.ui.has_played_highscore_sound = True
                    

            elif buttons['profile'].collidepoint(mx, my):  # Profile / Codex
                SoundManager.play_click_sound()
                ui.start_profile(0)
                self.game.game_state = "PROFILE"

        # =================================================
        # 2. INSTRUCTIONS (hướng dẫn)
        # =================================================
        elif state == "INSTRUCTIONS":
            SoundManager.play_click_sound()
            if self.game.ui.next_slide():
                self.game.game_state = "MENU"

        # =================================================
        # 3. HIGHSCORE
        # =================================================
        elif state == "HIGHSCORE":
            SoundManager.play_click_sound()
            self.game.game_state = "MENU"
            self.game.ui.has_played_highscore_sound = False
        # =================================================
        # 4. PROFILE / CHARACTER CODEX
        # =================================================
        elif state == "PROFILE":
            rects = self.game.ui.get_profile_click_rects()
            back_rect = rects.get('back')
            slots = rects.get('slots', [])

            # Nút back (góc phải trên)
            if back_rect and back_rect.collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "MENU"
                return

            # Click vào các slot (portrait lớn hoặc thumbnail nhỏ)
            for idx, rect in enumerate(slots):
                if rect.collidepoint(mx, my):
                    SoundManager.play_click_sound()
                    profiles = self.game.ui.profiles

                    # Nếu click thumbnail (idx 1-4) → đưa lên đầu danh sách
                    if idx > 0 and idx < len(profiles):
                        prof = profiles.pop(idx)
                        profiles.insert(0, prof)
                        self.game.ui.start_profile(0)
                    else:
                        self.game.ui.start_profile(idx)

                    # Nếu profile đầu không có mô tả → hiển thị thông báo placeholder
                    if not profiles[0].get('desc'):
                        self.game.ui.profile_full_text = 'NPC còn lại đang chờ bạn khám phá!'
                        self.game.ui.profile_display_text = ''
                        self.game.ui.profile_char_index = 0
                        self.game.ui.profile_typing_timer = 0
                    return

        # =================================================
        # 5. GAME OVER
        # =================================================
        elif state == "GAME_OVER":
            buttons = self.game.ui.get_game_over_buttons()

            if buttons['restart'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.new_game(tutorial=False)

            elif buttons['home'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "MENU"
                SoundManager.play_menu_music(volume=0.4)

            elif buttons['quit'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                pygame.quit()
                sys.exit()

        # =================================================
        # 6. PLAYING (trong game)
        # =================================================
        elif state == "PLAYING":
            buttons = self.game.ui.get_ingame_button_rects()

            if buttons['backhome'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "MENU"
                SoundManager.fadeout_background_music(500)
                SoundManager.play_menu_music(volume=0.4)

            elif buttons['pause'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.ui.is_paused = not self.game.ui.is_paused

            elif buttons['mute'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.ui.is_muted = not self.game.ui.is_muted
                volume = 0.0 if self.game.ui.is_muted else 0.5
                SoundManager.set_volume(volume)