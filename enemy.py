import pygame
import random
import os # Cần thư viện này để xây dựng đường dẫn file
from settings import * # Cần đảm bảo file settings.py đã có ENEMY_SPEED, ENEMY_SIZE

# --- 1. TẢI VÀ XỬ LÝ ẢNH TRƯỚC KHI VÀO GAME LOOP ---
all_enemy_sprites = []

def load_enemy_sprites():
    """Tải và resize 10 ảnh quái vật."""
    global all_enemy_sprites
    
    # Tạo đường dẫn tới thư mục chứa 10 ảnh
    folder_path = os.path.join(os.path.dirname(__file__), 'monster')
    
    # 10 ảnh được đánh số từ 1 đến 10
    for i in range(1, 11):
        file_name = f'animation_{i}.png'
        file_path = os.path.join(folder_path, file_name)
        
        try:
            # Tải ảnh, đảm bảo hỗ trợ độ trong suốt (PNG)
            img = pygame.image.load(file_path).convert_alpha()
            
            # Resize ảnh (Ảnh gốc 64x128. Giả sử ta muốn resize về 30x60 để giữ tỉ lệ 1:2)
            resized_img = pygame.transform.scale(img, (60, 60)) 
            all_enemy_sprites.append(resized_img)
        except pygame.error as e:
            print(f"Lỗi tải ảnh {file_name}: {e}")
            # Dùng hình vuông mặc định nếu không load được
            temp_surface = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE)); temp_surface.fill((200, 50, 50))
            all_enemy_sprites = [temp_surface] * 10
            break # Thoát vòng lặp nếu có lỗi
    print(f"DEBUG: Số lượng sprite đã tải: {len(all_enemy_sprites)}")
    if len(all_enemy_sprites) < 10:
        print("DEBUG: LỖI TẢI ẢNH. Có thể do sai đường dẫn file!")
# Bạn cần nhớ gọi hàm này trong file main.py!

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.score_value = 10
        
        # --- Hoạt ảnh ---
        self.sprites = all_enemy_sprites # Dùng danh sách đã tải
        self.current_frame = 0  
        self.animation_speed = 0.2 # Tốc độ chuyển ảnh. (0.2 nghĩa là đổi ảnh sau 5 lần update)

        if self.sprites:
            self.image = self.sprites[0]
            self.rect = self.image.get_rect()
        else:
            # Trường hợp ảnh lỗi (chỉ hiện ô vuông)
            self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE)); self.image.fill((200, 50, 50))
            self.rect = self.image.get_rect(size=(ENEMY_SIZE, ENEMY_SIZE))

        # --- Logic Vị trí & AI ---
        # ... (Phần logic xác định vị trí spawn và AI di chuyển giữ nguyên) ...
        # (Bạn cần copy lại logic spawn từ code trước vào đây)
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":    start_pos = (random.randint(0, WIDTH), -self.rect.height)
        elif side == "bottom": start_pos = (random.randint(0, WIDTH), HEIGHT + self.rect.height)
        elif side == "left":   start_pos = (-self.rect.width, random.randint(0, HEIGHT))
        else: start_pos = (WIDTH + self.rect.width, random.randint(0, HEIGHT))
        
        self.rect.center = start_pos
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = ENEMY_SPEED

    def animate(self):
        """Cập nhật frame hoạt ảnh"""
        self.current_frame += self.animation_speed
        
        if self.current_frame >= len(self.sprites):
            self.current_frame = 0
            
        self.image = self.sprites[int(self.current_frame)]

    def update(self):
        # 1. AI di chuyển (Giữ nguyên logic vector đuổi theo Player)
        player_vec = pygame.math.Vector2(self.player.rect.center) 
        enemy_vec = pygame.math.Vector2(self.rect.center)
        
        direction = player_vec - enemy_vec
        
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.center = round(self.pos.x), round(self.pos.y)

        # 2. Hoạt ảnh
        self.animate()