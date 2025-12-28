import pygame
from sounds import SoundManager
import sys

class EventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self):
        for event in pygame.event.get():

            # THOAT GAME
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # TIMER: DUNG TIENG NAP DAN
            if event.type == pygame.USEREVENT + 1:
                SoundManager.stop_reload_sound()

            # CLICK CHUOT TRAI
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.handle_mouse_click(mx, my)

            # NHAN PHIM
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game.game_state == "INSTRUCTIONS":
                        SoundManager.play_click_sound()
                        self.game.game_state = "MENU"
                    elif self.game.game_state == "PLAYING":
                        SoundManager.play_click_sound()
                        self.game.ui.is_paused = not self.game.ui.is_paused
                # advance dialog with Enter / Return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    try:
                        if getattr(self.game, 'npc', None) is not None:
                            self.game.npc.advance()
                    except Exception:
                        pass

    def handle_mouse_click(self, mx, my):
        state = self.game.game_state

        # =================================================
        # 1. MENU CHÍNH (3 Nút: Play, Quit, HowTo)
        # =================================================
        if state == "MENU":
            buttons = self.game.ui.get_menu_button_rects()
            if buttons['restart'].collidepoint(mx, my): # Nút Play
                SoundManager.play_click_sound()
                self.game.new_game()

            elif buttons['quit'].collidepoint(mx, my):  # Nút Quit
                SoundManager.play_click_sound()
                pygame.quit()
                sys.exit()

            elif buttons['howto'].collidepoint(mx, my): # Nút Hướng dẫn
                SoundManager.play_click_sound()
                self.game.game_state = "INSTRUCTIONS"
                self.game.ui.start_instructions()
            elif buttons['highscore'].collidepoint(mx, my):   # ← THÊM MỚI
                SoundManager.play_click_sound()
                self.game.game_state = "HIGHSCORE"
        
        elif state == "INSTRUCTIONS":
            SoundManager.play_click_sound()
            if self.game.ui.next_slide():               # Click bất kỳ → chuyển slide
                    self.game.game_state = "MENU"
        elif state == "HIGHSCORE":
            SoundManager.play_click_sound()
            self.game.game_state = "MENU"        
        # =================================================
        # 2. MÀN HÌNH THUA (GAME_OVER) - (2 Nút: Quit, Restart)
        # =================================================
        elif state == "GAME_OVER":
            # Lấy vị trí nút riêng của màn hình Defeat (đã viết trong UI)
            buttons = self.game.ui.get_game_over_buttons()

            if buttons['restart'].collidepoint(mx, my): # Nút Mũi tên (Chơi lại)
                SoundManager.play_click_sound()
                self.game.new_game()
            # Nút Quay về Menu chính
            elif buttons['home'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "MENU" # Chuyển về trạng thái Menu
                SoundManager.play_menu_music(volume=0.4) # Bật lại nhạc menu nếu cần
            elif buttons['quit'].collidepoint(mx, my):  # Nút X (Thoát)
                SoundManager.play_click_sound()
                pygame.quit()
                sys.exit()

        # =================================================
        # 3. MÀN HÌNH HƯỚNG DẪN
        # =================================================
        elif state == "INSTRUCTIONS":
            SoundManager.play_click_sound()
            self.game.game_state = "MENU"

        # =================================================
        # 4. ĐANG CHƠI (PLAYING) - (3 Nút góc phải)
        # =================================================
        elif state == "PLAYING":
            ingame_buttons = self.game.ui.get_ingame_button_rects()

            if ingame_buttons['backhome'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "MENU"
                SoundManager.fadeout_background_music(500)
                SoundManager.play_menu_music(volume=0.4)

            elif ingame_buttons['pause'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.ui.is_paused = not self.game.ui.is_paused

            elif ingame_buttons['mute'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.ui.is_muted = not self.game.ui.is_muted
                SoundManager.set_volume(0.0 if self.game.ui.is_muted else 0.5)