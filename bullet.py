import pygame
from settings import *
from sounds import SoundManager

class Bullet(pygame.sprite.Sprite):
    last_sound_time = 0
    sound_delay = 120  # ms

    def __init__(self, pos, vel, map_manager=None):

        super().__init__()

        # Hình đạn
        r = 7
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (r, r), r)
        pygame.draw.circle(self.image, (255, 100, 0), (r, r), r, 2)

        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.map_manager = map_manager

        try:
            print(f"Bullet created at {self.pos} vel={self.vel}")
        except Exception:
            pass


        self.spawn_time = pygame.time.get_ticks()

        # ===== AM THANH BAN =====
        now = pygame.time.get_ticks()
        if now - Bullet.last_sound_time >= Bullet.sound_delay:
            SoundManager.play_gun_sound(maxtime_ms=200)
            Bullet.last_sound_time = now

    def update(self):
        # di chuyển
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # ---- VA CHAM MAP ----
        if self.map_manager:
            for wall in self.map_manager.collision_rects:
                if self.rect.colliderect(wall):
                    # debug: nếu đạn bị kill ngay khi spawn, in ra vị trí
                    try:
                        print(f"Bullet collided with wall at {self.rect.center}")
                    except Exception:
                        pass
                    self.kill()
                    return

        # ra khỏi vùng map (không kill khi chỉ ra khỏi viewport)
        mw = getattr(self.map_manager, "map_width", WIDTH)
        mh = getattr(self.map_manager, "map_height", HEIGHT)
        if (self.rect.right < 0 or self.rect.left > mw or
            self.rect.bottom < 0 or self.rect.top > mh):
            self.kill()

        # hết lifetime
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
