import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Thay vì vẽ hình tròn trực tiếp, ta tạo Surface (sau này thay bằng ảnh rất dễ)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = PLAYER_HP

    def input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = PLAYER_SPEED

    def constraint(self):
        # Giữ nhân vật trong màn hình
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

    def update(self):
        self.input()
        self.rect.center += self.velocity
        self.constraint()