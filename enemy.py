import pygame
import random
import os 
import math
from settings import * # --- 1. KHAI BÁO DANH SÁCH ẢNH (Phải có đủ các dòng này) ---
enemy_sprites_normal = [] 
enemy_sprites_mon2_right = [] # Frame 1-6
enemy_sprites_mon2_left = []  # Frame 7-12

# Separation behaviour: enemies avoid overlapping each other
# radius in pixels within which separation applies, and force multiplier
SEPARATION_RADIUS = 48
SEPARATION_FORCE = 0.9

def load_enemy_sprites():
    global enemy_sprites_normal, enemy_sprites_mon2_right, enemy_sprites_mon2_left
    
    # Đường dẫn thư mục gốc
    base_path = os.path.dirname(__file__)
    
    # 1. Load Mon1
    folder_mon1 = os.path.join(base_path, 'monster', 'mon1')
    for i in range(1, 11):
        try:
            fn = f'animation_{i}.png'
            img = pygame.image.load(os.path.join(folder_mon1, fn)).convert_alpha()
            img = pygame.transform.scale(img, (60, 60)) 
            enemy_sprites_normal.append(img)
        except: pass 

    # 2. Load Mon2 (Boss)
    folder_mon2 = os.path.join(base_path, 'monster', 'mon2')
    
    # Load Hướng Phải (Frame 1-6)
    for i in range(1, 7):
        try:
            fn = f'character_frame_{i}.png'
            img = pygame.image.load(os.path.join(folder_mon2, fn)).convert_alpha()
            img = pygame.transform.scale(img, (200, 140))
            enemy_sprites_mon2_right.append(img)
        except: pass

    # Load Hướng Trái (Frame 7-12)
    for i in range(7, 13):
        try:
            fn = f'character_frame_{i}.png'
            img = pygame.image.load(os.path.join(folder_mon2, fn)).convert_alpha()
            img = pygame.transform.scale(img, (200, 140))
            enemy_sprites_mon2_left.append(img)
        except: pass

# --- 2. CLASS QUÁI THƯỜNG ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, map_manager=None):
        super().__init__()
        self.player = player
        self.map_manager = map_manager

        self.hp = 1             
        self.score_value = 10
        self.type = "normal"    
        
        self.sprites = enemy_sprites_normal if enemy_sprites_normal else [pygame.Surface((60, 60))]
        if not enemy_sprites_normal: self.sprites[0].fill((200, 50, 50))
            
        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.animation_speed = 0.2

        # spawn ngẫu nhiên trong map (tránh tường)
        while True:
            x = random.randint(2, 12) * 64
            y = random.randint(2, 8) * 64
            test_rect = self.rect.copy()
            test_rect.center = (x, y)

            blocked = False
            if self.map_manager:
                for wall in self.map_manager.collision_rects:
                    if test_rect.colliderect(wall):
                        blocked = True
                        break

            if not blocked:
                self.rect.center = (x, y)
                self.pos = pygame.Vector2(self.rect.center)
                self.speed = ENEMY_SPEED
                break

    def move(self, dx, dy):
        # ---- MOVE X ----
        step_x = int(abs(dx)) + 1
        for _ in range(step_x):
            self.pos.x += dx / step_x
            self.rect.centerx = int(self.pos.x)
            if self.map_manager:
                for wall in self.map_manager.collision_rects:
                    if self.rect.colliderect(wall):
                        self.pos.x -= dx / step_x
                        self.rect.centerx = int(self.pos.x)
                        break

        # ---- MOVE Y ----
        step_y = int(abs(dy)) + 1
        for _ in range(step_y):
            self.pos.y += dy / step_y
            self.rect.centery = int(self.pos.y)
            if self.map_manager:
                for wall in self.map_manager.collision_rects:
                    if self.rect.colliderect(wall):
                        self.pos.y -= dy / step_y
                        self.rect.centery = int(self.pos.y)
                        break




    def update(self):
        player_vec = pygame.math.Vector2(self.player.rect.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        direction = player_vec - enemy_vec
        move_vec = pygame.math.Vector2(0, 0)
        if direction.length_squared() > 0:
            move_vec = direction.normalize() * self.speed

        # Separation: avoid overlapping other enemies by applying a small repulsion
        separation = pygame.math.Vector2(0, 0)
        try:
            for g in self.groups():
                for other in g:
                    if other is self or not isinstance(other, Enemy):
                        continue
                    other_vec = pygame.math.Vector2(other.rect.center)
                    delta = enemy_vec - other_vec
                    dist2 = delta.length_squared()
                    if dist2 == 0:
                        # perfect overlap: nudge randomly
                        delta = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                        dist2 = 0.01
                    if dist2 < (SEPARATION_RADIUS * SEPARATION_RADIUS):
                        # stronger repulsion when closer
                        try:
                            rep = delta.normalize() * (SEPARATION_FORCE / max(math.sqrt(dist2), 0.1))
                            separation += rep
                        except Exception:
                            pass
        except Exception:
            pass

        final_move = move_vec + separation
        # cap speed so separation doesn't send them flying
        try:
            max_speed = max(self.speed, 0.1) * 1.5
            if final_move.length_squared() > (max_speed * max_speed):
                final_move = final_move.normalize() * max_speed
        except Exception:
            pass

        # perform movement with collision
        self.move(final_move.x, final_move.y)

        # Nếu là boss, thay sprites trái/phải theo player
        if self.type == "boss":
            if self.player.pos.x > self.pos.x:
                self.sprites = enemy_sprites_mon2_right
            else:
                self.sprites = enemy_sprites_mon2_left

        # update animation frame
        self.current_frame = (self.current_frame + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_frame)]

# --- 3. CLASS MONSTER 2 (BOSS) ---
class Monster2(Enemy):
    def __init__(self, player, map_manager=None):
        super().__init__(player, map_manager)

        self.hp = 6
        self.score_value = 100
        self.type = "boss"
        self.speed = 1.0
        self.animation_speed = 0.15

        spawn_side = random.choice(["left", "right"])
        if spawn_side == "left":
            self.sprites = enemy_sprites_mon2_right
        else:
            self.sprites = enemy_sprites_mon2_left

        if not self.sprites:
            self.sprites = [pygame.Surface((200, 140))]
            self.sprites[0].fill((150, 0, 150))

        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos = pygame.Vector2(self.rect.center)

