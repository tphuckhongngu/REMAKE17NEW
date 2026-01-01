# sounds.py
import pygame
import os

BASE_DIR = os.path.dirname(__file__)

def sound_path(filename):
    """Trả về đường dẫn đầy đủ đến file âm thanh"""
    return os.path.join(BASE_DIR, filename)


class SoundManager:
    # Các âm thanh sẽ được load một lần duy nhất
    gun_sound = None
    reload_sound = None
    begin_sound = None
    hurt_sound = None
    highscore_sound = None

    # Âm thanh dành riêng cho skill
    heal_sound = None
    powerup_sound = None
    magic_sound = None      # Skill 3: Bất tử
    barrage_sound = None    # Skill 4: Bullet Barrage

    # Kênh âm thanh riêng biệt
    shoot_channel = None
    reload_channel = None
    skill_channel = None    # Dùng cho skill lớn (magic, barrage...)

    initialized = False

    @staticmethod
    def init_mixer():
        """Khởi tạo mixer và load tất cả âm thanh. Gọi 1 lần trong Game.__init__()"""
        if SoundManager.initialized:
            return

        # Khởi tạo mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=512)
        except Exception as e:
            print("[SOUND] Mixer init failed:", e)

        # Tạo các kênh riêng
        SoundManager.shoot_channel = pygame.mixer.Channel(4)   # Bắn súng
        SoundManager.reload_channel = pygame.mixer.Channel(5)  # Nạp đạn
        SoundManager.skill_channel = pygame.mixer.Channel(6)   # Skill lớn (magic, barrage)

        # Load các âm thanh chính
        SoundManager._load_sound("gun_sound", "gunsound.mp3", volume=0.6)
        SoundManager._load_sound("reload_sound", "gunreload.mp3", volume=0.7)
        SoundManager._load_sound("begin_sound", "soundeffect/soundbegin.mp3", volume=1.1)
        SoundManager._load_sound("hurt_sound", "soundeffect/hurt.mp3", volume=0.9)
        SoundManager._load_sound("highscore_sound", "soundeffect/highscore_sound.mp3", volume=0.7)

        # Load âm thanh cho SKILL
        SoundManager._load_sound("heal_sound", "soundeffect/heal_sound.mp3", volume=0.8)           # Skill 1: Hồi máu
        SoundManager._load_sound("powerup_sound", "soundeffect/skill2.mp3", volume=0.9)     # Skill 2: Boost
        SoundManager._load_sound("magic_sound", "soundeffect/magic_sound.mp3", volume=1.0)  # Skill 3: Bất tử
        SoundManager._load_sound("barrage_sound", "soundeffect/skill2.mp3", volume=0.8)     # Skill 4: Barrage

        SoundManager.initialized = True
        print("[SOUND] SoundManager initialized successfully.")

    @staticmethod
    def _load_sound(attr_name, filename, volume=1.0):
        """Hàm phụ để load âm thanh an toàn"""
        try:
            full_path = sound_path(filename)
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(volume)
            setattr(SoundManager, attr_name, sound)
        except Exception as e:
            print(f"[SOUND] Không load được {filename}: {e}")
            setattr(SoundManager, attr_name, None)

    # ===================== MUSIC =====================
    @staticmethod
    def play_background_music(volume=0.5):
        try:
            pygame.mixer.music.load(sound_path("background_music.mp3"))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("[SOUND] Lỗi load background_music.mp3:", e)

    @staticmethod
    def play_menu_music(volume=0.4):
        try:
            pygame.mixer.music.load(sound_path("menu_music.mp3"))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("[SOUND] Lỗi load menu_music.mp3:", e)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()

    @staticmethod
    def fadeout_background_music(ms=1000):
        pygame.mixer.music.fadeout(ms)

    @staticmethod
    def set_volume(volume):
        pygame.mixer.music.set_volume(volume)

    # ===================== SFX CƠ BẢN =====================
    @staticmethod
    def play_begin_sound():
        if SoundManager.begin_sound:
            SoundManager.begin_sound.play()

    @staticmethod
    def play_hurt_sound():
        if SoundManager.hurt_sound and not pygame.mixer.Channel(7).get_busy():
            pygame.mixer.Channel(7).play(SoundManager.hurt_sound)

    @staticmethod
    def play_highscore_sound():
        if SoundManager.highscore_sound:
            SoundManager.highscore_sound.play()

    @staticmethod
    def play_click_sound():
        try:
            click = pygame.mixer.Sound(sound_path("click.mp3"))
            click.set_volume(0.6)
            click.play()
        except Exception as e:
            print("[SOUND] Lỗi play click:", e)

    # ===================== GUN & RELOAD =====================
    @staticmethod
    def play_gun_sound(maxtime_ms=150):
        if not SoundManager.gun_sound:
            return
        try:
            if SoundManager.shoot_channel and SoundManager.shoot_channel.get_busy():
                SoundManager.shoot_channel.stop()
            if SoundManager.shoot_channel:
                SoundManager.shoot_channel.play(SoundManager.gun_sound, maxtime=maxtime_ms)
            else:
                SoundManager.gun_sound.play(maxtime=maxtime_ms)
        except Exception as e:
            print("[SOUND] Lỗi play gun:", e)

    @staticmethod
    def play_reload_sound(duration_ms=3000):
        if not SoundManager.reload_sound:
            return
        try:
            if SoundManager.reload_channel:
                SoundManager.reload_channel.play(SoundManager.reload_sound, loops=-1)
            else:
                SoundManager.reload_sound.play(loops=-1)
            pygame.time.set_timer(pygame.USEREVENT + 1, duration_ms)
        except Exception as e:
            print("[SOUND] Lỗi play reload:", e)

    @staticmethod
    def stop_reload_sound():
        try:
            if SoundManager.reload_channel:
                SoundManager.reload_channel.stop()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        except Exception as e:
            print("[SOUND] Lỗi stop reload:", e)

    # ===================== SKILL SOUND =====================
    @staticmethod
    def play_heal_sound(volume=0.8):
        """Skill 1: Hồi máu"""
        if SoundManager.heal_sound:
            SoundManager.heal_sound.set_volume(volume)
            SoundManager.heal_sound.play()

    @staticmethod
    def play_powerup_sound(volume=0.9):
        """Skill 2: Boost sát thương boss"""
        if SoundManager.powerup_sound:
            SoundManager.powerup_sound.set_volume(volume)
            SoundManager.powerup_sound.play()

    @staticmethod
    def play_magic_sound(volume=1.0):
        """Skill 3: Bất tử 8 giây - âm thanh thần thánh"""
        if SoundManager.magic_sound and SoundManager.skill_channel:
            SoundManager.skill_channel.play(SoundManager.magic_sound)
            SoundManager.magic_sound.set_volume(volume)
        elif SoundManager.magic_sound:
            SoundManager.magic_sound.play()

    @staticmethod
    def play_barrage_sound(volume=0.8):
        """Skill 4: Bullet Barrage - loạt đạn mạnh mẽ"""
        if SoundManager.barrage_sound and SoundManager.skill_channel:
            if SoundManager.skill_channel.get_busy():
                SoundManager.skill_channel.stop()
            SoundManager.skill_channel.play(SoundManager.barrage_sound)
            SoundManager.barrage_sound.set_volume(volume)
        elif SoundManager.barrage_sound:
            SoundManager.barrage_sound.play()