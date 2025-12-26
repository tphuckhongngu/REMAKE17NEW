# maps/map_manager.py
import pygame

TILE_SIZE = 64

# Tile chặn di chuyển
BLOCK_TILES = {"tuong",
               "thung",
               }

class MapManager:
    def __init__(self, tile_folder):
        self.tiles = {}
        self.collision_rects = []
        self.layout = []
        self.map_width = 0
        self.map_height = 0
        self.load_tiles(tile_folder)

    def load_tiles(self, folder):
        tile_names = ["co", "nuoc", "dat", "betong", "tuong", "thung"]

        for name in tile_names:
            try:
                img = pygame.image.load(f"{folder}/{name}.png").convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.tiles[name] = img
            except:
                # try a couple of common alternative filenames (e.g. đat.png)
                alt_loaded = False
                try:
                    if name == "dat":
                        img = pygame.image.load(f"{folder}/đat.png").convert_alpha()
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                        self.tiles[name] = img
                        alt_loaded = True
                except Exception:
                    alt_loaded = False

                if not alt_loaded:
                    # tile fallback nếu thiếu ảnh — dùng màu magenta rõ ràng và log
                    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    # use neutral grey fallback instead of magenta
                    surf.fill((120, 120, 120))
                    self.tiles[name] = surf
                    try:
                        print(f"Warning: missing tile image for '{name}' in '{folder}', using placeholder.")
                    except Exception:
                        pass

    def build_collision(self, layout):
        self.layout = layout
        self.collision_rects.clear()

        self.map_height = len(layout) * TILE_SIZE
        self.map_width = len(layout[0]) * TILE_SIZE

        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile in BLOCK_TILES:
                    self.collision_rects.append(
                        pygame.Rect(
                            x * TILE_SIZE,
                            y * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )

    def draw(self, screen, camera=None):
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                draw_rect = camera.apply(rect) if camera else rect
                screen.blit(self.tiles[tile], draw_rect.topleft)
