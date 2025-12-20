# sounds.py
import pygame
import os

# ===== BASE DIR =====
BASE_DIR = os.path.dirname(__file__)

def sound_path(filename):
    return os.path.join(BASE_DIR, filename)


class SoundManager:
    @staticmethod
    def init_mixer():
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    @staticmethod
    def play_background_music(volume=0.5):
        try:
            pygame.mixer.music.load(sound_path('background_music.mp3'))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Loi load background_music:", e)

    @staticmethod
    def play_menu_music(volume=0.4):
        try:
            pygame.mixer.music.load(sound_path('menu_music.mp3'))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Loi load menu_music:", e)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()

    @staticmethod
    def fadeout_background_music(ms=1000):
        pygame.mixer.music.fadeout(ms)

    @staticmethod
    def set_volume(volume):
        pygame.mixer.music.set_volume(volume)

    @staticmethod
    def play_click_sound():
        try:
            click_sound = pygame.mixer.Sound(sound_path('click.mp3'))
            click_sound.set_volume(0.6)
            click_sound.play()
        except Exception as e:
            print("Loi load click sound:", e)
