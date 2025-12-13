import pygame
import math
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 6)
        self.rect = self.image.get_rect(center=pos)
        
        self.speed = BULLET_SPEED
        self.angle = angle
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Xóa đạn nếu ra khỏi màn hình
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill() # Hàm này tự động xóa sprite khỏi tất cả các Group