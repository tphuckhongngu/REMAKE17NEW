import pygame
import random
import os 
from settings import * # --- 1. TẢI VÀ XỬ LÝ ẢNH ---
enemy_sprites_normal = [] 
enemy_sprites_mon2 = []   

def load_enemy_sprites():
    global enemy_sprites_normal, enemy_sprites_mon2
    
    # Load Mon1
    folder_path = os.path.join(os.path.dirname(__file__), 'monster', 'mon1')
    for i in range(1, 11):
        try:
            fn = f'animation_{i}.png'
            img = pygame.image.load(os.path.join(folder_path, fn)).convert_alpha()
            img = pygame.transform.scale(img, (60, 60)) 
            enemy_sprites_normal.append(img)
        except: pass 

    # Load Mon2 (Boss)
    path_mon2 = os.path.join(os.path.dirname(__file__), 'monster', 'mon2')
    for i in range(1, 7): 
        try:
            fn = f'character_frame_{i}.png'
            img = pygame.image.load(os.path.join(path_mon2, fn)).convert_alpha()
            # Kích thước mới bạn yêu cầu: 200x140
            img = pygame.transform.scale(img, (200, 140)) 
            enemy_sprites_mon2.append(img)
        except Exception as e:
            print(f"Lỗi load mon2: {e}")

# --- 2. CLASS QUÁI THƯỜNG ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.hp = 1             
        self.score_value = 10
        self.type = "normal"    
        
        if enemy_sprites_normal:
            self.sprites = enemy_sprites_normal
        else:
            self.sprites = [pygame.Surface((60, 60))]
            self.sprites[0].fill((200, 50, 50))
            
        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.animation_speed = 0.2

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":    start_pos = (random.randint(0, WIDTH), -50)
        elif side == "bottom": start_pos = (random.randint(0, WIDTH), HEIGHT + 50)
        elif side == "left":   start_pos = (-50, random.randint(0, HEIGHT))
        else: start_pos = (WIDTH + 50, random.randint(0, HEIGHT))
        
        self.rect.center = start_pos
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = ENEMY_SPEED

    def update(self):
        player_vec = pygame.math.Vector2(self.player.rect.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        direction = player_vec - enemy_vec
        if direction.length() > 0:
            self.pos += direction.normalize() * self.speed
            self.rect.center = round(self.pos.x), round(self.pos.y)
        
        self.current_frame = (self.current_frame + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_frame)]

# --- 3. CLASS MONSTER 2 (BOSS) ---
class Monster2(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.hp = 10            
        self.score_value = 100  
        self.type = "boss"      
        
        if enemy_sprites_mon2:
            self.sprites = enemy_sprites_mon2
        else:
            self.sprites = [pygame.Surface((200, 140))]
            self.sprites[0].fill((150, 0, 150))

        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.animation_speed = 0.15

        # Xuất hiện ngẫu nhiên ở mép trái hoặc phải để tăng độ khó
        self.rect.center = (random.choice([-100, WIDTH + 100]), HEIGHT // 2)
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 1.8 # Tăng tốc độ lên một chút cho kịch tính

    def update(self):
        # DI CHUYỂN THẲNG TỚI NGƯỜI CHƠI (Đã bỏ stun)
        player_vec = pygame.math.Vector2(self.player.rect.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        direction = player_vec - enemy_vec
        
        if direction.length() > 0:
            self.pos += direction.normalize() * self.speed
            self.rect.center = round(self.pos.x), round(self.pos.y)

        # Animation
        self.current_frame = (self.current_frame + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_frame)]