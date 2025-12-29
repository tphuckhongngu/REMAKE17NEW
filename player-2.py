
import pygame
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, bullet_group):
        super().__init__(groups)

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 180, 255), self.image.get_rect(), border_radius=8)
        self.rect = self.image.get_rect(center=pos)

        self.bullet_group = bullet_group

        # ===== Di chuyển =====
        self.speed = 5

        # ===== Bắn =====
        self.shoot_delay = 250
        self.last_shot = 0
        self.bullet_speed = 10

        # ===== Trạng thái skill =====
        self.fast_shot = False     # phím 1
        self.triple_shot = False   # phím 2
        self.shield = False        # phím 3

        # ===== Timer =====
        self.fast_timer = 0
        self.triple_timer = 0
        self.shield_timer = 0

    def input(self):
        keys = pygame.key.get_pressed()

        # Di chuyển
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        # Skill
        if keys[pygame.K_1]:
            self.activate_fast_shot()

        if keys[pygame.K_2]:
            self.activate_triple_shot()

        if keys[pygame.K_3]:
            self.activate_shield()

        # Bắn
        if pygame.mouse.get_pressed()[0]:
            self.shoot()

    # ===== SKILLS =====
    def activate_fast_shot(self):
        if not self.fast_shot:
            self.fast_shot = True
            self.fast_timer = pygame.time.get_ticks()
            self.bullet_speed = 18  # bắn nhanh hơn

    def activate_triple_shot(self):
        if not self.triple_shot:
            self.triple_shot = True
            self.triple_timer = pygame.time.get_ticks()

    def activate_shield(self):
        if not self.shield:
            self.shield = True
            self.shield_timer = pygame.time.get_ticks()

    # ===== BẮN =====
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return

        self.last_shot = now

        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(
            mouse_pos[0] - self.rect.centerx,
            mouse_pos[1] - self.rect.centery
        )

        if direction.length() == 0:
            return

        if self.triple_shot:
            for angle in (-15, 0, 15):
                Bullet(
                    self.rect.center,
                    dir
