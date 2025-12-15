# sounds.py
import pygame

class SoundManager:
    def init_mixer():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def play_background_music(volume=-100000):
        pygame.mixer.music.load('background_music.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def play_menu_music(volume=-10000):
        pygame.mixer.music.load('menu_music.mp3')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def stop_music():
        pygame.mixer.music.stop()

    def fadeout_background_music(ms=1000):
        pygame.mixer.music.fadeout(ms)