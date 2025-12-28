# sounds.py
import pygame
import os

BASE_DIR = os.path.dirname(__file__)

def sound_path(filename):
    return os.path.join(BASE_DIR, filename)


class SoundManager:
    # static attrs (will be set by init_mixer)
    gun_sound = None
    reload_sound = None
    shoot_channel = None
    reload_channel = None
    initialized = False
    begin_sound = None

    @staticmethod
    def init_mixer():
        """Init mixer and load SFX. Call once early (Game.__init__)."""
        if SoundManager.initialized:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print("Mixer init failed:", e)
            # continue; attempts to load may fail later

        # create dedicated channels (choose indexes that don't conflict)
        try:
            SoundManager.shoot_channel = pygame.mixer.Channel(4)
            SoundManager.reload_channel = pygame.mixer.Channel(5)
        except Exception:
            SoundManager.shoot_channel = None
            SoundManager.reload_channel = None

        # load sound files with try/except
        try:
            SoundManager.gun_sound = pygame.mixer.Sound(sound_path("gunsound.mp3"))
            SoundManager.gun_sound.set_volume(0.6)
        except Exception as e:
            print("Can't load gunsound.mp3:", e)
            SoundManager.gun_sound = None

        try:
            SoundManager.reload_sound = pygame.mixer.Sound(sound_path("gunreload.mp3"))
            SoundManager.reload_sound.set_volume(0.7)
        except Exception as e:
            print("Can't load gunreload.mp3:", e)
            SoundManager.reload_sound = None

        SoundManager.initialized = True
        try:
            # Lưu ý: Bạn nói folder là 'soundeffect', hãy kiểm tra lại đường dẫn
            SoundManager.begin_sound = pygame.mixer.Sound(sound_path("soundeffect/soundbegin.mp3"))
            SoundManager.begin_sound.set_volume(0.7)
        except Exception as e:
            print("Can't load soundbegin:", e)
    # --- music helpers (unchanged) ---
    @staticmethod
    def play_begin_sound():
        if SoundManager.begin_sound:
            SoundManager.begin_sound.play()
    @staticmethod
    def play_background_music(volume=0.5):
        try:
            pygame.mixer.music.load(sound_path("background_music.mp3"))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Loi load background_music:", e)

    @staticmethod
    def play_menu_music(volume=0.4):
        try:
            pygame.mixer.music.load(sound_path("menu_music.mp3"))
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

    # --- SFX: gun and reload ---
    @staticmethod
    def play_gun_sound(maxtime_ms=150):
        """
        Play short gun sound. maxtime_ms controls how many milliseconds
        of the clip actually play (clips longer than that are truncated).
        """
        if SoundManager.gun_sound is None:
            return

        try:
            # Stop current short gun if playing (optional)
            if SoundManager.shoot_channel is not None:
                if SoundManager.shoot_channel.get_busy():
                    SoundManager.shoot_channel.stop()
                SoundManager.shoot_channel.play(SoundManager.gun_sound, maxtime=maxtime_ms)
            else:
                # fallback
                SoundManager.gun_sound.play(maxtime=maxtime_ms)
        except Exception as e:
            print("Error play_gun_sound:", e)

    @staticmethod
    def play_reload_sound(duration_ms=3000):
        """
        Play reload loop and schedule to stop after duration_ms using a pygame timer event.
        We'll also provide stop_reload_sound() so code can stop earlier.
        """
        if SoundManager.reload_sound is None:
            return

        try:
            if SoundManager.reload_channel is not None:
                # loop -1 means continuous; we'll stop with stop_reload_sound or timer event
                SoundManager.reload_channel.play(SoundManager.reload_sound, loops=-1)
            else:
                SoundManager.reload_sound.play(loops=-1)
            # set a timer event to stop reload after duration_ms
            pygame.time.set_timer(pygame.USEREVENT + 1, duration_ms)
        except Exception as e:
            print("Error play_reload_sound:", e)

    @staticmethod
    def stop_reload_sound():
        try:
            if SoundManager.reload_channel is not None:
                SoundManager.reload_channel.stop()
            else:
                if SoundManager.reload_sound is not None:
                    SoundManager.reload_sound.stop()
            # cancel timer to be safe
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        except Exception as e:
            print("Error stop_reload_sound:", e)

    @staticmethod
    def play_click_sound():
        try:
            click_sound = pygame.mixer.Sound(sound_path('click.mp3'))
            click_sound.set_volume(0.6)
            click_sound.play()
        except Exception as e:
            print("Loi load click sound:", e)
