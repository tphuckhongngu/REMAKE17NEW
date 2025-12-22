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

    def handle_mouse_click(self, mx, my):
        state = self.game.game_state

        if state in ["MENU", "GAME_OVER"]:
            buttons = self.game.ui.get_button_rects()

            if buttons['restart'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.new_game()

            elif buttons['quit'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                pygame.quit()
                sys.exit()

            elif buttons['howto'].collidepoint(mx, my):
                SoundManager.play_click_sound()
                self.game.game_state = "INSTRUCTIONS"

        elif state == "INSTRUCTIONS":
            SoundManager.play_click_sound()
            self.game.game_state = "MENU"

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
