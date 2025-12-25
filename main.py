# main.py
import pygame
import sys
import random
import math

from settings import *
from player import Player
# from bullet import Bullet   # main không tạo bullet trực tiếp nữa
from ui import UI
from events import EventHandler
from sounds import SoundManager
from enemy import Enemy, Monster2, load_enemy_sprites
from camera import Camera
from maps.map_manager import MapManager
from maps.complex_map import MAP_LAYOUT
from item import HealItem

# tinh chỉnh spawn (pixel)
ENEMY_SPAWN_MIN_DIST = 200   # tối thiểu khoảng cách spawn enemy cách player (pixel)
ENEMY_SPAWN_TRIES = 500      # số lần thử tìm tile trống trước khi fallback


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # load assets cần thiết
        load_enemy_sprites()  # nếu hàm này tồn tại
        SoundManager.init_mixer()
        SoundManager.play_menu_music(volume=0.4)

        # hệ thống map, camera, UI
        self.map_manager = MapManager("tiles")
        # gán layout cho map_manager (map lưu bên trong MapManager)
        self.map_manager.layout = MAP_LAYOUT
        # build collision rects từ layout
        self.map_manager.build_collision(MAP_LAYOUT)

        self.camera = Camera(WIDTH, HEIGHT)
        self.ui = UI(self.screen)

        # trạng thái game
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER, INSTRUCTIONS

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # event handler (nếu bạn có class này)
        self.event_handler = EventHandler(self)

        # player và các timer
        self.player = None
        self.spawn_timer = 0

        # boss / score
        self.boss_spawned = False
        self.last_boss_score = 0
        # heal items
        self.heal_items = pygame.sprite.Group()
        self.heal_spawn_timer = 0

    # ---------------- helper ----------------
    def find_free_tile_center(self, avoid_pos=None, min_dist=0):
        """
        Tìm center (pixel) của một tile 'free' (không chạm collision rect).
        avoid_pos: (x,y) pixel để tránh (ví dụ center player)
        min_dist: khoảng cách tối thiểu (pixel) so với avoid_pos
        Trả về (x, y) pixel center.
        """
        layout = getattr(self.map_manager, "layout", None)
        if not layout:
            return (WIDTH // 2, HEIGHT // 2)

        # xác định kích thước tile (nếu load ảnh thành công)
        try:
            sample_img = next(iter(self.map_manager.tiles.values()))
            tile_size = sample_img.get_width()
        except Exception:
            tile_size = 64

        rows = len(layout)
        cols = len(layout[0]) if rows > 0 else 0

        tries = 0
        while tries < ENEMY_SPAWN_TRIES:
            tries += 1
            # Nếu avoid_pos là None (spawn player), ưu tiên vùng cỏ trung tâm
            if avoid_pos is None:
                tx = random.randint(15, 24)
                ty = random.randint(10, 15)
            else:
                # Spawn enemy ở bất kỳ vị trí nào trong bản đồ
                tx = random.randint(1, max(1, cols - 2))
                ty = random.randint(1, max(1, rows - 2))

            x = tx * tile_size + tile_size // 2
            y = ty * tile_size + tile_size // 2

            # tránh quá gần avoid_pos
            if avoid_pos is not None and min_dist > 0:
                dx = x - avoid_pos[0]
                dy = y - avoid_pos[1]
                if (dx * dx + dy * dy) < (min_dist * min_dist):
                    continue

            # test rect (kích thước lấy theo PLAYER_SIZE nếu có)
            try:
                w = h = PLAYER_SIZE
            except Exception:
                w = h = tile_size // 2

            test_rect = pygame.Rect(0, 0, w, h)
            test_rect.center = (x, y)

            blocked = False
            for wall in getattr(self.map_manager, "collision_rects", []):
                if test_rect.colliderect(wall):
                    blocked = True
                    break

            if not blocked:
                return (x, y)

        # fallback: center map
        return (cols * tile_size // 2, rows * tile_size // 2)

    def new_game(self):
        # reset toàn bộ
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()

        # debug: kiểm tra collision rects (tùy in)
        # print("collision rects:", len(self.map_manager.collision_rects))

        # tìm vị trí spawn an toàn cho player
        spawn_pos = self.find_free_tile_center(avoid_pos=None, min_dist=0)

        # tạo player, truyền group đạn để Player spawn bullet vào
        # Player.__init__ nên chấp nhận start_pos và map_manager
        self.player = Player(
            bullet_group=self.bullets,
            start_pos=spawn_pos,
            map_manager=self.map_manager,
            all_sprites=self.all_sprites
        )
        # gán camera cho player để rotation/shoot dùng offset chính xác
        try:
            self.player.camera = self.camera
        except Exception:
            pass
        self.all_sprites.add(self.player)
        # ngay lập tức center camera trên player để player xuất hiện giữa màn hình
        try:
            self.camera.update(self.player)
        except Exception:
            pass

        # đổi state + âm thanh
        self.game_state = "PLAYING"
        SoundManager.stop_music()
        SoundManager.play_background_music(volume=0.5)

        # reset điểm
        try:
            self.ui.score = 0
        except Exception:
            self.ui.score = 0

        self.spawn_timer = 0
        self.last_boss_score = 0
        # heal items
        self.heal_items.empty()
        self.heal_spawn_timer = 0

    def update(self):
        if self.game_state != "PLAYING":
            return

        if getattr(self.ui, "is_paused", False):
            return

        # update tất cả sprites
        self.all_sprites.update()
        self.bullets.update()
        self.heal_items.update()
        # camera update (theo player)
        if self.player is not None:
            self.camera.update(self.player)

        # xử lý bắn: gọi Player.shoot() khi chuột nhấn (Player quản lý fire rate)
        if self.player is not None and pygame.mouse.get_pressed()[0]:
            self.player.shoot()

        # spawn enemy định kỳ
        self.spawn_timer += 1
        if self.spawn_timer >= SPAWN_DELAY:
            self.spawn_timer = 0
            self.spawn_enemy()   # gọi helper

           

        # spawn boss theo điểm
        if getattr(self.ui, "score", 0) - self.last_boss_score >= 100:
            self.spawn_boss()
            self.last_boss_score += 150

        # va chạm đạn - quái
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            dmg = len(bullets_hit)
            if hasattr(enemy, "take_damage"):
                enemy.take_damage(dmg)
            else:
                enemy.hp = getattr(enemy, "hp", 0) - dmg

            if getattr(enemy, "hp", 1) <= 0:
                if hasattr(enemy, "score_value"):
                    try:
                        self.ui.score += enemy.score_value
                    except Exception:
                        pass
                enemy.kill()

        # va chạm quái - player
        if self.player is not None:
            hits_player = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in hits_player:
                if getattr(enemy, "type", "") == "boss":
                    self.player.health -= 20
                else:
                    self.player.health -= 10
                enemy.kill()
        # --- Trong Game.update ---
        self.heal_spawn_timer += 1
        if self.heal_spawn_timer >= 10 * FPS:
            self.heal_spawn_timer = 0
            
            # Sử dụng hàm find_free_tile_center để túi máu không nằm trong tường
            spawn_pos = self.find_free_tile_center() 
            new_heal = HealItem(spawn_pos)
            self.heal_items.add(new_heal)

        # Xử lý va chạm túi máu
        heal_hits = pygame.sprite.spritecollide(self.player, self.heal_items, True)
        for hit in heal_hits:
            self.player.health += 5
            if self.player.health > 100:
                self.player.health = 100
            # Chèn âm thanh hồi máu nếu có
            # SoundManager.play_heal_sound()
        # game over
        if self.player is not None and self.player.health <= 0:
            self.game_state = "GAME_OVER"
            SoundManager.stop_music()

    def draw(self):
        # phân nhánh vẽ cho từng trạng thái
        if self.game_state == "MENU":
            self.ui.draw_menu()
            pygame.display.flip()
            return
        if self.game_state == "GAME_OVER":
            self.ui.draw_game_over()
            pygame.display.flip()
            return
        if self.game_state == "INSTRUCTIONS":
            self.ui.draw_instructions()
            pygame.display.flip()
            return

        # PLAYING
        self.screen.fill((30, 30, 30))

        # 1) draw map
        self.map_manager.draw(self.screen, self.camera)
        # 2. Vẽ Túi máu (Dưới chân Player)
        for item in self.heal_items:
            self.screen.blit(item.image, self.camera.apply(item.rect))
        # 2) draw bullets (trước player để layering) with camera
        for b in self.bullets:
            try:
                draw_rect = self.camera.apply(b.rect) if self.camera else b.rect
            except Exception:
                draw_rect = b.rect
            self.screen.blit(b.image, draw_rect)

        # debug overlay: draw bullet markers and count
        try:
            bullet_count = len(self.bullets)
            dbg_font = pygame.font.SysFont(None, 20)
            txt = dbg_font.render(f"Bullets: {bullet_count}", True, (255,255,0))
            self.screen.blit(txt, (10, 40))
            for b in self.bullets:
                try:
                    r = self.camera.apply(b.rect) if self.camera else b.rect
                    pygame.draw.rect(self.screen, (255,0,0), r, 1)
                except Exception:
                    pass
        except Exception:
            pass

        # 3) draw sprites with camera
        for s in self.all_sprites:
            try:
                draw_rect = self.camera.apply(s.rect) if self.camera else s.rect
            except Exception:
                draw_rect = s.rect
            self.screen.blit(s.image, draw_rect)

        # 4) UI + ammo
        try:
            self.ui.draw_hud(self.player.health)
        except Exception:
            try:
                self.ui.draw_hud()
            except Exception:
                pass

        self.ui.draw_ingame_buttons()

        if self.player is not None:
            self.player.draw_ammo(self.screen)

        # pause overlay
        if getattr(self.ui, "is_paused", False):
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            pause_text = self.ui.font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.display.flip()

    def run(self):
        while True:
            # xử lý event (dùng EventHandler nếu có)
            try:
                self.event_handler.handle_events()
            except Exception:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_n:
                            self.new_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)
    
    def spawn_enemy(self):
        """Spawn một enemy thông thường, tránh player"""
        spawn_pos = self.find_free_tile_center(
            avoid_pos=self.player.rect.center if self.player else None,
            min_dist=ENEMY_SPAWN_MIN_DIST
        )
        enemy = Enemy(self.player, map_manager=self.map_manager)
        enemy.rect.center = spawn_pos
        enemy.pos = pygame.Vector2(spawn_pos)

        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def spawn_boss(self):
        """Spawn boss khi score đủ, tránh player"""
        spawn_pos = self.find_free_tile_center(
            avoid_pos=self.player.rect.center if self.player else None,
            min_dist=ENEMY_SPAWN_MIN_DIST + 100
        )
        boss = Monster2(self.player, map_manager=self.map_manager)
        boss.rect.center = spawn_pos
        boss.pos = pygame.Vector2(spawn_pos)

        self.enemies.add(boss)
        self.all_sprites.add(boss)

if __name__ == "__main__":
    g = Game()
    g.run()
