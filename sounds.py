# sounds.py
import pygame
import os

class SoundManager:
    @staticmethod
    def init_mixer():
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    @staticmethod
    def play_background_music(volume=0.4):
        base_path = os.path.dirname(__file__)
        sound_path = os.path.join(base_path, 'background_music.mp3')

        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    @staticmethod
    def play_menu_music(volume=0.4):
        base_path = os.path.dirname(__file__)
        sound_path = os.path.join(base_path, 'menu_music.mp3')

        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()

    @staticmethod
    def fadeout_background_music(ms=1000):
        pygame.mixer.music.fadeout(ms)
