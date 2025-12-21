import pygame
import random
import os
import importlib.util  # THÊM ĐÂY để load file .py động KHÔNG cần __init__.py
from settings import *

class Item(pygame.sprite.Sprite):
    def __init__(self, abs_x, abs_y, item_type="health"):
        super().__init__()
        self.item_type = item_type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        color = (0, 255, 0) if item_type == "health" else (0, 255, 255)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(0, 0))  # Dummy, sẽ update screen pos
        self.abs_x = abs_x
        self.abs_y = abs_y

    def update_screen_rect(self, offset):
        self.rect.centerx = self.abs_x - offset[0]
        self.rect.centery = self.abs_y - offset[1]

class MapManager:
    COLORS = {
        0: (139, 69, 19),    # Đất nâu
        1: (105, 105, 105),  # Tường
        2: (0, 255, 0),      # Cỏ xanh
        3: (255, 0, 0),      # Rác độc
        4: (0, 0, 255),      # Nước
    }
    COLLIDABLE_TYPES = {1, 3}  # Tường và rác chặn đường

    def __init__(self, folder="maps"):
        self.folder = folder
        self.maps = {}
        self.current = None
        self.items = pygame.sprite.Group()
        self.tile_cols = 0
        self.tile_rows = 0
        self.tile_size = TILE_SIZE
        self.width_tiles = 100  # 3200px
        self.height_tiles = 50  # 1600px
        self.load(folder)

    def generate_random_map(self, cols, rows):
        map_data = [[0 for _ in range(cols)] for _ in range(rows)]
        # Biên tường
        for x in range(cols):
            map_data[0][x] = 1
            map_data[rows - 1][x] = 1
        for y in range(rows):
            map_data[y][0] = 1
            map_data[y][cols - 1] = 1
        # Vật cản ngẫu nhiên
        for y in range(1, rows - 1):
            for x in range(1, cols - 1):
                rand = random.random()
                if rand < 0.1: map_data[y][x] = 1
                elif rand < 0.2: map_data[y][x] = 3
                elif rand < 0.25: map_data[y][x] = 4
        return map_data

    def load(self, folder):
        self.maps['random'] = self.generate_random_map(self.width_tiles, self.height_tiles)
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith(".py") and not filename.startswith("__"):
                    name = filename[:-3]
                    filepath = os.path.join(folder, filename)
                    try:
                        spec = importlib.util.spec_from_file_location(name, filepath)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "get_map"):
                            self.maps[name] = mod.get_map(self.width_tiles, self.height_tiles)
                        elif hasattr(mod, "MAP"):
                            self.maps[name] = mod.MAP
                        print(f"Loaded map: {name}")
                    except Exception as e:
                        print(f"Lỗi load {name}: {e}")

    def use(self, name):
        if name in self.maps:
            self.current = self.maps[name]
            self.tile_cols = len(self.current[0])
            self.tile_rows = len(self.current)
            self.items.empty()
            print(f"Using map: {name}")

    def check_environment_collision(self, screen_rect, offset):
        world_rect = screen_rect.move(offset[0], offset[1])
        map_world_w = self.tile_cols * self.tile_size
        map_world_h = self.tile_rows * self.tile_size
        if (world_rect.left < 0 or world_rect.top < 0 or
            world_rect.right > map_world_w or world_rect.bottom > map_world_h):
            return True
        col_left = max(0, world_rect.left // self.tile_size)
        col_right = min(self.tile_cols, (world_rect.right // self.tile_size) + 1)
        row_top = max(0, world_rect.top // self.tile_size)
        row_bottom = min(self.tile_rows, (world_rect.bottom // self.tile_size) + 1)
        for row in range(row_top, row_bottom):
            for col in range(col_left, col_right):
                t = self.current[row][col]
                if t in self.COLLIDABLE_TYPES:
                    tile_rect = pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size)
                    if world_rect.colliderect(tile_rect):
                        return True
        return False

    def process_bullets(self, bullets, offset):
        cleaned = 0
        to_kill = set()
        for bullet in bullets:
            world_rect = bullet.rect.move(offset[0], offset[1])
            tx = int(world_rect.centerx // self.tile_size)
            ty = int(world_rect.centery // self.tile_size)
            if 0 <= tx < self.tile_cols and 0 <= ty < self.tile_rows:
                t = self.current[ty][tx]
                if t in self.COLLIDABLE_TYPES:
                    to_kill.add(bullet)
                    if t == 3:
                        self.current[ty][tx] = 2
                        cleaned += 1
        for bullet in to_kill:
            bullet.kill()
        return cleaned

    def drop_item(self, world_x, world_y):
        if random.random() < 0.5:
            item_type = random.choice(["health", "ammo"])
            item = Item(world_x, world_y, item_type)
            self.items.add(item)

    def update_items(self, offset):
        for item in self.items:
            item.update_screen_rect(offset)

    def handle_items(self, player_screen_rect):
        collected = pygame.sprite.spritecollide(player_screen_rect, self.items, True)
        bonuses = {"health": 0, "ammo": 0}
        for item in collected:
            if item.item_type == "health":
                bonuses["health"] += 20
        return bonuses

    def draw(self, screen, camera):
        if not self.current:
            return
        offset = camera.offset
        start_col = max(0, int(offset[0] // self.tile_size) - 2)  # SỬA: -2 để cover thừa
        end_col = min(self.tile_cols, int((offset[0] + WIDTH) // self.tile_size) + 2)  # +2
        start_row = max(0, int(offset[1] // self.tile_size) - 2)  # -2
        end_row = min(self.tile_rows, int((offset[1] + HEIGHT) // self.tile_size) + 2)  # +2
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                t = self.current[row][col]
                color = self.COLORS.get(t, (40, 40, 40))
                px = col * self.tile_size - offset[0]
                py = row * self.tile_size - offset[1]
                pygame.draw.rect(screen, color, (px, py, self.tile_size, self.tile_size))

    def draw_items(self, screen):
        self.items.draw(screen)