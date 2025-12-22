import pygame
from settings import *
from sounds import SoundManager

class Bullet(pygame.sprite.Sprite):
    last_sound_time = 0
    sound_delay = 120  # ms

    def __init__(self, pos, vel):
        super().__init__()

        # Hình đạn
        r = 7
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (r, r), r)
        pygame.draw.circle(self.image, (255, 100, 0), (r, r), r, 2)

        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))

        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)

        self.spawn_time = pygame.time.get_ticks()

        # ===== AM THANH BAN =====
        now = pygame.time.get_ticks()
        if now - Bullet.last_sound_time >= Bullet.sound_delay:
            SoundManager.play_gun_sound(maxtime_ms=200)
            Bullet.last_sound_time = now

    def update(self):
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
