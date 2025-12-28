
import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, groups):
        super().__init__(groups)

        self.image = pygame.Surface((10, 4), pygame.SRCALPHA)
        self.image.fill((255, 200, 50))  # màu đạn thường
        self.rect = self.image.get_rect(center=pos)

        self.direction = pygame.math.Vector2(direction)
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.speed = speed

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # tự huỷ khi ra khỏi màn hình
        if (
            self.rect.right < 0 or self.rect.left > 1280 or
            self.rect.bottom < 0 or self.rect.top > 720
        ):
            self.kill()
