import pygame
import random

# Các hằng số (phù hợp với code chung từ các thành viên khác)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32  # Kích thước mỗi tile (thống nhất 32x32 pixel cho assets)
MAP_WIDTH = 100  # Số tile ngang (map rộng để hỗ trợ scrolling)
MAP_HEIGHT = 50  # Số tile dọc (map cao để khám phá)

# Màu sắc cho các loại tile (theme rác thải và môi trường, dùng tạm cho prototype; sau thay bằng hình ảnh PNG)
COLORS = {
    0: (139, 69, 19),    # 0: Đất nâu (đi được, không va chạm)
    1: (105, 105, 105),  # 1: Tường bê tông nứt vỡ (không đi qua, va chạm)
    2: (0, 255, 0),      # 2: Cỏ xanh hồi sinh (đi được, sau khi dọn rác)
    3: (255, 0, 0),      # 3: Rác thải độc hại (không đi qua ban đầu, có thể "dọn" để biến thành 2)
    4: (0, 0, 255)       # 4: Nước (đi được, nhưng có thể thêm hiệu ứng chậm cho player)
}

# Dữ liệu bản đồ cho Chương 1: Thành Phố Rác Thải (ma trận 2D, mở rộng cho các chương khác)
# Sử dụng pattern lặp để tạo map lớn, với tường biên, rác ngẫu nhiên, đường đi
map_data = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]  # Khởi tạo map trống

# Tạo biên tường
for x in range(MAP_WIDTH):
    map_data[0][x] = 1  # Hàng trên
    map_data[MAP_HEIGHT-1][x] = 1  # Hàng dưới
for y in range(MAP_HEIGHT):
    map_data[y][0] = 1  # Cột trái
    map_data[y][MAP_WIDTH-1] = 1  # Cột phải

# Thêm vật cản và rác ngẫu nhiên (ví dụ: 20% tile là tường/rác)
for y in range(1, MAP_HEIGHT-1):
    for x in range(1, MAP_WIDTH-1):
        rand = random.random()
        if rand < 0.1:
            map_data[y][x] = 1  # Tường
        elif rand < 0.2:
            map_data[y][x] = 3  # Rác thải
        elif rand < 0.25:
            map_data[y][x] = 4  # Nước (cho đa dạng)

# Class Tile (mỗi ô bản đồ là một sprite để dễ quản lý va chạm)
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLORS.get(tile_type, (0, 0, 0)))  # Màu theo loại (thay bằng pygame.image.load cho assets thật)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        # Thuộc tính va chạm: Chỉ loại 1 và 3 ban đầu là chặn
        self.collidable = tile_type in [1, 3]

    def update_type(self, new_type):
        """Cập nhật loại tile (ví dụ: dọn rác 3 -> 2)"""
        self.tile_type = new_type
        self.image.fill(COLORS.get(new_type, (0, 0, 0)))
        self.collidable = new_type in [1, 3]

# Class Item (vật phẩm hỗ trợ rớt từ quái)
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type="health"):  # item_type: "health" (hộp máu/phân bón), "ammo" (đạn dược)
        super().__init__()
        self.item_type = item_type
        self.image = pygame.Surface((20, 20))
        if item_type == "health":
            self.image.fill((0, 255, 0))  # Xanh lá - phân bón hồi máu
        elif item_type == "ammo":
            self.image.fill((0, 255, 255))  # Xanh dương - đạn tái chế
        self.rect = self.image.get_rect(center=(x, y))
        self.abs_x = x  # Vị trí tuyệt đối để đồng bộ scroll
        self.abs_y = y

    def update(self, scroll):
        """Đồng bộ vị trí với camera scroll"""
        self.rect.x = self.abs_x - scroll[0]
        self.rect.y = self.abs_y - scroll[1]

# Nhóm sprite cho tiles và items (toàn cục, tích hợp với all_sprites nếu cần)
tiles = pygame.sprite.Group()
items = pygame.sprite.Group()

def init_map():
    """Khởi tạo bản đồ từ map_data (gọi khi bắt đầu game hoặc reset)"""
    tiles.empty()  # Xóa tiles cũ nếu reset
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_type = map_data[y][x]
            tile = Tile(x, y, tile_type)
            tiles.add(tile)

# Khởi tạo map ban đầu
init_map()

# Hàm kiểm tra va chạm với môi trường (cho player và enemies)
def check_environment_collision(entity_rect, scroll, direction=None):
    """
    Kiểm tra va chạm với tiles collidable.
    entity_rect: rect của entity (player/enemy) ở vị trí tuyệt đối (abs_x, abs_y)
    scroll: display_scroll
    direction: Optional, để kiểm tra theo hướng (dx, dy) nếu cần tinh chỉnh
    Trả về True nếu va chạm (không đi được)
    """
    for tile in tiles:
        if tile.collidable:
            tile_rect_adjusted = tile.rect.copy()
            tile_rect_adjusted.x -= scroll[0]
            tile_rect_adjusted.y -= scroll[1]
            if entity_rect.colliderect(tile_rect_adjusted):
                return True
    return False

# Hàm vẽ bản đồ và môi trường (gọi trong game loop, tối ưu chỉ vẽ tiles trong view)
def draw_environment(screen, scroll):
    """Vẽ tiles và items với đồng bộ camera (display_scroll)"""
    # Tính range tiles hiển thị để tối ưu (không vẽ toàn map)
    start_x = max(0, int(scroll[0] // TILE_SIZE) - 2)  # Buffer 2 tiles
    end_x = min(MAP_WIDTH, int((scroll[0] + SCREEN_WIDTH) // TILE_SIZE) + 2)
    start_y = max(0, int(scroll[1] // TILE_SIZE) - 2)
    end_y = min(MAP_HEIGHT, int((scroll[1] + SCREEN_HEIGHT) // TILE_SIZE) + 2)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_type = map_data[y][x]
            tile_x = x * TILE_SIZE - scroll[0]
            tile_y = y * TILE_SIZE - scroll[1]
            pygame.draw.rect(screen, COLORS.get(tile_type, (0,0,0)), (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
    
    # Vẽ items (đã update vị trí)
    for item in items:
        screen.blit(item.image, item.rect)

# Xử lý tương tác với môi trường (ví dụ: dọn rác khi bắn trúng tile loại 3)
# Thêm vào logic va chạm bullet (thành viên 2 và 3):
# for tile in tiles:
#     if tile.tile_type == 3 and bullet.rect.colliderect(tile.rect.move(-display_scroll[0], -display_scroll[1])):
#         tile.update_type(2)  # Biến rác thành cỏ xanh
#         map_data[tile.rect.y // TILE_SIZE][tile.rect.x // TILE_SIZE] = 2  # Cập nhật data
#         global score
#         score += 1  # Tăng % hồi sinh
#         bullet.kill()

# Xử lý thu thập items (gọi trong game loop)
def handle_items(player):
    """Kiểm tra va chạm player với items"""
    collected = pygame.sprite.spritecollide(player, items, True)
    for item in collected:
        if item.item_type == "health":
            player.health = min(100, player.health + 20)
        elif item.item_type == "ammo":
            player.ammo += 10

# Tạo item khi diệt quái (thêm vào logic enemy chết - thành viên 3)
# Ví dụ:
# def drop_item(abs_x, abs_y):
#     if random.random() < 0.5:  # 50% chance rớt item
#         item_type = random.choice(["health", "ammo"])
#         item = Item(abs_x, abs_y, item_type)
#         items.add(item)
#         all_sprites.add(item)  # Nếu dùng all_sprites từ thành viên 1

# Đồng bộ camera: Tất cả tiles và items dùng vị trí tuyệt đối - scroll khi vẽ/update

# HƯỚNG DẪN TÍCH HỢP VÀO MAIN.PY:
# 1. Thêm code này sau import và trước game loop.
# 2. Thêm abs_x, abs_y vào Player và Enemy (tương tự Bullet):
#    - Trong __init__: self.abs_x = SCREEN_WIDTH // 2; self.abs_y = SCREEN_HEIGHT // 2
#    - Trong update: Tính new_abs_x = self.abs_x + dx; new_rect = self.rect.copy(); new_rect.center = (new_abs_x, new_abs_y)
#      if not check_environment_collision(new_rect, display_scroll):
#          self.abs_x = new_abs_x; self.abs_y = new_abs_y
#          display_scroll[0] -= dx  # Chỉ cho player (scroll theo player)
#          display_scroll[1] -= dy
#      self.rect.centerx = self.abs_x - display_scroll[0]  # Cập nhật rect hiển thị
#      self.rect.centery = self.abs_y - display_scroll[1]
# 3. Trong game loop (state PLAY):
#     - items.update(display_scroll)  # Update vị trí items
#     - draw_environment(screen, display_scroll)  # Vẽ map trước sprite
#     - handle_items(player)  # Sau update player
# 4. Trong reset_game(): init_map(); items.empty()
# 5. Mở rộng cho các chương: Tạo dict maps = {1: map_ch1_data, ...}; Khi chuyển chương: map_data = maps[chapter]; init_map()
# 6. Assets thật: Thay COLORS bằng dict IMAGES = {0: pygame.image.load('dirt.png'), ...}; self.image = IMAGES[tile_type]
# 7. Nâng cấp: Thêm hiệu ứng hồi sinh (animation khi dọn rác), vật cản động (cây chắn từ phân bón)