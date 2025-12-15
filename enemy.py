import pygame
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player # Cần biết vị trí player để đuổi theo
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        
        # Spawn logic (đã tách ra từ hàm cũ)
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top": start_pos = (random.randint(0, WIDTH), -50)
        elif side == "bottom": start_pos = (random.randint(0, WIDTH), HEIGHT + 50)
        elif side == "left": start_pos = (-50, random.randint(0, HEIGHT))
        else: start_pos = (WIDTH + 50, random.randint(0, HEIGHT))
        
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = ENEMY_SPEED

    def update(self):
        # Logic đuổi theo player
        player_vector = pygame.math.Vector2(self.player.rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        
        if player_vector != enemy_vector: # Tránh chia cho 0
            direction = (player_vector - enemy_vector).normalize()
            self.rect.center += direction * self.speed
#