import pygame
import random
import os # Cần thư viện này để xây dựng đường dẫn file
from settings import * # Cần đảm bảo file settings.py đã có ENEMY_SPEED, ENEMY_SIZE

# --- 1. TẢI VÀ XỬ LÝ ẢNH TRƯỚC KHI VÀO GAME LOOP ---
enemy_sprites_normal = [] # Ảnh quái thường
enemy_sprites_mon2 = []   # Ảnh quái số 2 (Boss)

def load_enemy_sprites():
    """Tải và resize 10 ảnh quái vật."""
    global enemy_sprites_normal, enemy_sprites_mon2
    
    # Tạo đường dẫn tới thư mục chứa 10 ảnh
    folder_path = os.path.join(os.path.dirname(__file__), 'monster', 'mon1')
    
    # 10 ảnh được đánh số từ 1 đến 10
    for i in range(1, 11):
        try:
            fn = f'animation_{i}.png'
            img = pygame.image.load(os.path.join(folder_path, fn)).convert_alpha()
            img = pygame.transform.scale(img, (60, 60)) 
            enemy_sprites_normal.append(img)
        except: pass # Bỏ qua nếu lỗi
# >> LOAD QUÁI SỐ 2 (Folder monster/mon2)
    path_mon2 = os.path.join(os.path.dirname(__file__), 'monster', 'mon2')

    for i in range(1, 7): 
        try:
            fn = f'character_frame_{i}.png'
            img = pygame.image.load(os.path.join(path_mon2, fn)).convert_alpha()
            # Quái này trâu nên cho to hơn chút (ví dụ 60x60)
            img = pygame.transform.scale(img, (200, 165)) 
            enemy_sprites_mon2.append(img)
        except Exception as e:
            print(f"Lỗi load mon2 frame {i}: {e}")

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.hp = 1             # Máu = 1 (bắn 1 phát chết)
        self.score_value = 10
        self.type = "normal"    # Đánh dấu loại quái
        
        # Ảnh & Rect
        if enemy_sprites_normal:
            self.sprites = enemy_sprites_normal
        else:
            self.sprites = [pygame.Surface((60, 60))]
            self.sprites[0].fill((200, 50, 50))
            
        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.animation_speed = 0.2

        # Spawn ngẫu nhiên
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":    start_pos = (random.randint(0, WIDTH), -50)
        elif side == "bottom": start_pos = (random.randint(0, WIDTH), HEIGHT + 50)
        elif side == "left":   start_pos = (-50, random.randint(0, HEIGHT))
        else: start_pos = (WIDTH + 50, random.randint(0, HEIGHT))
        
        self.rect.center = start_pos
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = ENEMY_SPEED

    def update(self):
        # Di chuyển liên tục
        player_vec = pygame.math.Vector2(self.player.rect.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        direction = player_vec - enemy_vec
        if direction.length() > 0:
            self.pos += direction.normalize() * self.speed
            self.rect.center = round(self.pos.x), round(self.pos.y)
        
        # Animation
        self.current_frame = (self.current_frame + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_frame)]
# ==========================================
# CLASS QUÁI SỐ 2 (MONSTER 2 - TÂN BINH)
# ==========================================
class Monster2(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.hp = 10            # << MÁU 10 VIÊN
        self.max_hp = 10        # Để vẽ thanh máu nếu cần
        self.score_value = 100  # Điểm cao hơn
        self.type = "boss"      
        
        # Xử lý choáng (Stun)
        self.stun_timer = 0     # Bộ đếm thời gian dừng
        
        # Ảnh
        if enemy_sprites_mon2:
            self.sprites = enemy_sprites_mon2
        else:
            self.sprites = [pygame.Surface((200, 165))] # Placeholder màu tím
            self.sprites[0].fill((150, 0, 150))

        self.current_frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.animation_speed = 0.15

        # Vị trí Spawn (Cố định hoặc Random tùy bạn, ở đây để Random cho dễ)
        self.rect.center = (-100, HEIGHT // 2) # Spawn từ bên trái xa xa
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 1.5 # Đi chậm hơn quái thường tí

    def apply_stun(self):
        """Gọi hàm này khi chạm vào người chơi"""
        self.stun_timer = 120 # 60 FPS * 2 giây = 120 frames

    def update(self):
        # 1. KIỂM TRA CHOÁNG
        if self.stun_timer > 0:
            self.stun_timer -= 1
            # Có thể thêm hiệu ứng rung lắc ở đây nếu thích
            # Khi bị choáng thì KHÔNG DI CHUYỂN, chỉ chạy animation (hoặc đứng im)
        else:
            # 2. LOGIC DI CHUYỂN (Chỉ chạy khi không bị choáng)
            player_vec = pygame.math.Vector2(self.player.rect.center)
            enemy_vec = pygame.math.Vector2(self.rect.center)
            direction = player_vec - enemy_vec
            
            if direction.length() > 0:
                self.pos += direction.normalize() * self.speed
                self.rect.center = round(self.pos.x), round(self.pos.y)

        # 3. Animation
        self.current_frame = (self.current_frame + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_frame)]