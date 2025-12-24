import pygame

# -------------------- Màn hình / FPS --------------------
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Top-Down Shooter Team Project"

# -------------------- Màu sắc --------------------
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (200, 50, 50)
GREEN  = (0, 200, 50)
BLUE   = (0, 200, 255)
YELLOW = (255, 255, 0)

# -------------------- Player --------------------
PLAYER_SPEED = 5         # tốc độ di chuyển (pixel/frame)
PLAYER_SIZE  = 60        # kích thước sprite player (pixel) → khớp với hình
PLAYER_HP    = 100       # máu player

# -------------------- Bullet --------------------
BULLET_SPEED    = 15     # tốc độ đạn (pixel/frame)
BULLET_LIFETIME = 1000   # lifetime đạn (milliseconds)

# -------------------- Enemy --------------------
ENEMY_SPEED = 1          # tốc độ enemy thường
ENEMY_SIZE  = 60         # size enemy (pixel) → khớp với sprite
SPAWN_DELAY = 60         # số frame giữa 2 lần spawn enemy

# -------------------- Map / Tile --------------------
TILE_SIZE = 64           # size tile (pixel) → khớp MapManager
BLOCK_TILES = {
    "tuongbetong",
    "tuonggo",
    "thunggo",
}

# -------------------- Spawn / Enemy --------------------
ENEMY_SPAWN_MIN_DIST = 200   # khoảng cách spawn enemy so với player (pixel)
ENEMY_SPAWN_TRIES    = 500   # số lần thử spawn tránh tường trước khi fallback
import pygame

# -------------------- Màn hình / FPS --------------------
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Top-Down Shooter Team Project"

# -------------------- Màu sắc --------------------
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (200, 50, 50)
GREEN  = (0, 200, 50)
BLUE   = (0, 200, 255)
YELLOW = (255, 255, 0)

# -------------------- Player --------------------
PLAYER_SPEED = 5         # tốc độ di chuyển (pixel/frame)
PLAYER_SIZE  = 60        # kích thước sprite player (pixel) → khớp với hình
PLAYER_HP    = 100       # máu player

# -------------------- Bullet --------------------
BULLET_SPEED    = 15     # tốc độ đạn (pixel/frame)
BULLET_LIFETIME = 1000   # lifetime đạn (milliseconds)

# -------------------- Enemy --------------------
ENEMY_SPEED = 1          # tốc độ enemy thường
ENEMY_SIZE  = 60         # size enemy (pixel) → khớp với sprite
SPAWN_DELAY = 60         # số frame giữa 2 lần spawn enemy

# -------------------- Map / Tile --------------------
TILE_SIZE = 64           # size tile (pixel) → khớp MapManager
BLOCK_TILES = {
    "tuongbetong",
    "tuonggo",
    "thunggo",
}

# -------------------- Spawn / Enemy --------------------
ENEMY_SPAWN_MIN_DIST = 200   # khoảng cách spawn enemy so với player (pixel)
ENEMY_SPAWN_TRIES    = 500   # số lần thử spawn tránh tường trước khi fallback
