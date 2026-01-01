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
from boss import Boss
from camera import Camera
from maps.map_manager import MapManager
from maps import trainingmap
from maps import mainmap
from npc import NPC
from item import HealItem
from teleport_gate import TeleportGate
# skill UI disabled: no on-screen skill panel or bullets HUD

# tinh chỉnh spawn (pixel)
ENEMY_SPAWN_MIN_DIST = 200   # tối thiểu khoảng cách spawn enemy cách player (pixel)
ENEMY_SPAWN_TRIES = 500      # số lần thử tìm tile trống trước khi fallback
BOSS_SPAWN_INTERVAL = 25000  # ms between automatic boss spawns
MONSTER2_SPAWN_CHANCE = 0.35  # chance to spawn Monster2 instead of Enemy


class Game:
    def __init__(self):
        pygame.init()
        font = pygame.font.SysFont(None, 24)
        # support starting in fullscreen while keeping logical resolution
        self.fullscreen = bool(globals().get('FULLSCREEN', False))
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
    

        
        # load assets cần thiết
        load_enemy_sprites()  # nếu hàm này tồn tại
        SoundManager.init_mixer()
        SoundManager.play_menu_music(volume=0.4)

        # hệ thống map, camera, UI
        self.map_manager = MapManager("tiles")
        # default: load main complex map. Training/tutorial will be loaded
        # when user clicks the training button from menu.
        try:
            self.map_manager.layout = mainmap.MAP_LAYOUT
            self.map_manager.build_collision(mainmap.MAP_LAYOUT)
            self.tutorial_mode = False
        except Exception:
            # fallback minimal empty layout
            self.map_manager.layout = []
            self.map_manager.collision_rects = []
            self.tutorial_mode = False

        self.camera = Camera(WIDTH, HEIGHT)
        self.ui = UI(self.screen)
        # ensure a font that supports Vietnamese: prefer bundled DejaVuSans.ttf
        import os
        try:
            fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
            os.makedirs(fonts_dir, exist_ok=True)
            bundled = os.path.join(fonts_dir, 'DejaVuSans.ttf')
            if not os.path.exists(bundled):
                # try to download DejaVu Sans (OSS) if network available
                try:
                    from urllib.request import urlretrieve
                    url = 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
                    urlretrieve(url, bundled)
                except Exception:
                    # ignore download failures; will fall back to system fonts
                    pass

            if os.path.exists(bundled):
                try:
                    self.dialog_font = pygame.font.Font(bundled, 22)
                except Exception:
                    self.dialog_font = pygame.font.SysFont(None, 22)
            else:
                # fall back to a selection of common system fonts
                found = False
                for name in ("segoeui", "tahoma", "arial", "dejavusans"):
                    path = pygame.font.match_font(name)
                    if path:
                        try:
                            self.dialog_font = pygame.font.Font(path, 22)
                            found = True
                            break
                        except Exception:
                            continue
                if not found:
                    self.dialog_font = pygame.font.SysFont(None, 22)
        except Exception:
            self.dialog_font = pygame.font.SysFont(None, 22)
        self.ui.load_high_score()
        self.ui.update_rank(self.ui.high_score)
        
        # trạng thái game
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER, INSTRUCTIONS
        
        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        # teleport gates (created for main map only)
        self.gates = pygame.sprite.Group()
        # boss attack groups
        self.boss_bullets = pygame.sprite.Group()
        self.poison_pools = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.webs = pygame.sprite.Group()


        # event handler (nếu bạn có class này)
        self.event_handler = EventHandler(self)

        # player và các timer
        self.player = None
        self.spawn_timer = 0
        # tutorial / training flags
        self.practice_started = False
        self.tutorial_followup_done = False
        self.training_started = False
        self.training_spawned = False
        self.training_completed = False
        self.training_moved_map = False
        # tutorial practice tracking
        self.practice_started = False
        self.tutorial_followup_done = False

        # boss / score
        self.boss_spawned = False
        self.last_boss_score = 0
        # time (ms) of last periodic boss spawn
        try:
            self.last_boss_time = pygame.time.get_ticks()
        except Exception:
            self.last_boss_time = 0
        # persistent boss health across appearances
        self.boss_persistent_health = 100
        # heal items
        self.heal_items = pygame.sprite.Group()
        self.heal_spawn_timer = 0
        # play begin sound only once
        self.has_played_begin_sound = False
        # damage flash
        self.hit_timer = 0  # Thời gian còn lại để nhấp nháy
        self.flash_duration = 200 # Nhấp nháy trong 200ms (0.2 giây)
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

    def new_game(self, tutorial=False):
        # reset toàn bộ
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        self.npcs.empty()
        try:
            self.gates.empty()
        except Exception:
            pass
        self.practice_started = False
        self.tutorial_followup_done = False
        self.training_started = False
        self.training_spawned = False
        self.training_enemies_created = False
        self.training_gate_opened = False
        self.training_completed = False
        self.training_moved_map = False
        self.has_played_begin_sound = False

        # debug: kiểm tra collision rects (tùy in)
        # print("collision rects:", len(self.map_manager.collision_rects))

        # set tutorial mode according to caller request
        self.tutorial_mode = bool(tutorial)

        # ensure correct map is loaded for chosen mode
        if self.tutorial_mode:
            try:
                self.map_manager.layout = trainingmap.MAP_LAYOUT
                self.map_manager.build_collision(trainingmap.MAP_LAYOUT)
            except Exception:
                pass
        else:
            try:
                self.map_manager.layout = mainmap.MAP_LAYOUT
                self.map_manager.build_collision(mainmap.MAP_LAYOUT)
            except Exception:
                pass
            # explicitly remove any tutorial NPC so player enters immediately
            try:
                self.npc = None
                self.npcs.empty()
            except Exception:
                pass

        # nếu đang tutorial: tạo NPC hướng dẫn trước để spawn player bên cạnh
        if getattr(self, "tutorial_mode", False):
            try:
                # tạo NPC tại tile (6,5) với tên hiển thị
                self.npc = NPC((6, 5), name="Đại úy. Chí Hướng")
                self.npcs.add(self.npc)
                self.all_sprites.add(self.npc)
                # đặt vị trí spawn player ngay bên phải NPC nếu có thể
                try:
                    sample_img = next(iter(self.map_manager.tiles.values()))
                    tile_size = sample_img.get_width()
                except Exception:
                    tile_size = 64

                spawn_x = (self.npc.tile_x + 1) * tile_size + tile_size // 2
                spawn_y = self.npc.tile_y * tile_size + tile_size // 2
                spawn_pos = (spawn_x, spawn_y)

                # tạo player, truyền group đạn để Player spawn bullet vào
                self.player = Player(
                    bullet_group=self.bullets,
                    start_pos=spawn_pos,
                    map_manager=self.map_manager,
                    all_sprites=self.all_sprites
                )
                # bắt đầu chuỗi thoại tutorial (nội dung được quản lý trong NPC)
                try:
                    self.npc.start_initial_tutorial(typing_delay=2)
                except Exception:
                    try:
                        self.npc.start_dialog(["chào mừng đến với buổi tập huấn ngày hôm nay!"], typing_delay=2)
                    except Exception:
                        pass
            except Exception:
                self.npc = None
                # fallback tạo player ở nơi trống
                spawn_pos = self.find_free_tile_center(avoid_pos=None, min_dist=0)
                self.player = Player(
                    bullet_group=self.bullets,
                    start_pos=spawn_pos,
                    map_manager=self.map_manager,
                    all_sprites=self.all_sprites
                )
        else:
            # tìm vị trí spawn an toàn cho player (bản đồ chính)
            spawn_pos = self.find_free_tile_center(avoid_pos=None, min_dist=0)
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

        # create teleport gates only for main (non-tutorial) map
        try:
            self.gates.empty()
            if not getattr(self, 'tutorial_mode', False):
                # determine tile size and layout size
                try:
                    sample_img = next(iter(self.map_manager.tiles.values()))
                    tile_size = sample_img.get_width()
                except Exception:
                    tile_size = 64
                rows = len(getattr(self.map_manager, 'layout', []))
                cols = len(getattr(self.map_manager, 'layout', [[]])[0]) if rows > 0 else 0

                # choose four corner-ish cells (keep inside bounds)
                corners = []
                if cols >= 3 and rows >= 3:
                    corners = [(1, 1), (cols - 2, 1), (1, rows - 2), (cols - 2, rows - 2)]
                else:
                    corners = [(1, 1), (1, 1), (1, 1), (1, 1)]

                for tx, ty in corners:
                    x = tx * tile_size + tile_size // 2
                    y = ty * tile_size + tile_size // 2
                    # flip horizontally for gates on the right half
                    flip = True if tx > (cols // 2) else False
                    g = TeleportGate((x, y), flip_horiz=flip)
                    self.gates.add(g)
                    self.all_sprites.add(g)
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
        # nếu không đặt self.npc ở trên, đảm bảo có thuộc tính
        if not hasattr(self, 'npc'):
            self.npc = None

    def switch_to_main_map(self):
        """Chuyển từ tutorial sang màn chính (mainmap)."""
        try:
            self.map_manager.layout = mainmap.MAP_LAYOUT
            self.map_manager.build_collision(mainmap.MAP_LAYOUT)
        except Exception:
            return
        self.tutorial_mode = False
        # tạo lại player và sprite groups trên map mới
        self.new_game(tutorial=False)

    def start_training(self):
        """Load tutorial map and start training run immediately."""
        try:
            self.map_manager.layout = trainingmap.MAP_LAYOUT
            self.map_manager.build_collision(trainingmap.MAP_LAYOUT)
            self.tutorial_mode = True
        except Exception:
            return
        # reset training gate state and begin the run (will spawn NPC and player appropriately)
        self.training_gate_opened = False
        # set the exact line after which monsters should be released
        self.training_release_line = "Hãy tiêu diệt hết tất cả bọn quái vật này để chứng minh bạn đủ sức để giải cứu thế giới tan hoang này!"
        self.new_game(tutorial=True)

        # Immediately pre-place training enemies inside enclosure (they are trapped until gate opens)
        try:
            spawns = getattr(trainingmap, 'TRAINING_SPAWNS', None)
            tile_size = 64
            try:
                sample_img = next(iter(self.map_manager.tiles.values()))
                tile_size = sample_img.get_width()
            except Exception:
                pass

            if spawns:
                cells = list(spawns) if spawns else []
                if not cells:
                    cells = [(1, 1)]
                # distribute monsters to unique cells first
                random.shuffle(cells)
                total_m1 = 15
                total_m2 = 5
                used_positions = set()
                idx = 0

                # helper to get unique center with small jitter if necessary
                def get_center(sx, sy):
                    base_x = sx * tile_size + tile_size // 2
                    base_y = sy * tile_size + tile_size // 2
                    # jitter a bit to avoid exact overlaps
                    jx = random.randint(-8, 8)
                    jy = random.randint(-8, 8)
                    return (base_x + jx, base_y + jy)

                # place Monster1
                for i in range(total_m1):
                    sx, sy = cells[idx % len(cells)]
                    idx += 1
                    x, y = get_center(sx, sy)
                    # avoid exact duplicates by nudging if already used
                    while (x, y) in used_positions:
                        x += random.randint(-6, 6)
                        y += random.randint(-6, 6)
                    used_positions.add((x, y))
                    e = Enemy(self.player, map_manager=self.map_manager)
                    e.rect.center = (x, y)
                    try:
                        e.pos = pygame.Vector2((x, y))
                    except Exception:
                        pass
                    self.enemies.add(e)
                    self.all_sprites.add(e)

                # place Monster2
                for i in range(total_m2):
                    sx, sy = cells[idx % len(cells)]
                    idx += 1
                    x, y = get_center(sx, sy)
                    while (x, y) in used_positions:
                        x += random.randint(-6, 6)
                        y += random.randint(-6, 6)
                    used_positions.add((x, y))
                    m = Monster2(self.player, map_manager=self.map_manager)
                    m.rect.center = (x, y)
                    try:
                        m.pos = pygame.Vector2((x, y))
                    except Exception:
                        pass
                    self.enemies.add(m)
                    self.all_sprites.add(m)

            # mark created so update() won't re-create
            self.training_enemies_created = True
            self.training_spawned = True
        except Exception:
            pass
    def trigger_hit_effect(self):
        """Gọi hàm này mỗi khi bị quái chạm"""
        self.hit_timer = pygame.time.get_ticks()
    def update(self):
        if self.game_state != "PLAYING":
            return

        if getattr(self.ui, "is_paused", False):
            return

        # update tất cả sprites
        self.all_sprites.update()
        self.bullets.update()
        self.boss_bullets.update()
        self.poison_pools.update()
        self.lasers.update()
        self.webs.update()
        self.heal_items.update()
        # update NPCs (typing effect)
        for n in self.npcs:
            try:
                n.update()
            except Exception:
                pass
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
            # không spawn enemy khi đang tutorial
            if not getattr(self, "tutorial_mode", False):
                self.spawn_enemy()   # gọi helper

           

        # periodic spawn every BOSS_SPAWN_INTERVAL (ms)
        try:
            now = pygame.time.get_ticks()
        except Exception:
            now = 0

        # do not spawn if a boss already exists
        has_boss = any([e.__class__.__name__ == 'Boss' for e in self.enemies])
        if not has_boss and now - getattr(self, 'last_boss_time', 0) >= BOSS_SPAWN_INTERVAL:
            self.spawn_boss()
            self.last_boss_time = now

        # legacy score-based spawn (kept but less aggressive)
        if getattr(self.ui, "score", 0) - self.last_boss_score >= 100:
            if not has_boss:
                self.spawn_boss()
            self.last_boss_score += 150

        # Tìm đoạn này trong hàm update() của bạn và thay bằng:

        # Thu thập đòn đánh từ Boss
        for e in list(self.enemies):
            # Kiểm tra xem enemy có phải là Boss không và có đòn đánh chờ xử lý không
            if isinstance(e, Boss) and hasattr(e, 'pending_attacks'):
                while e.pending_attacks:
                    atk = e.pending_attacks.pop(0)
                    self.all_sprites.add(atk)
                    
                    # Phân loại đạn dựa trên class thực tế
                    from boss import BossBullet, PoisonPool, Laser, Web # Import nếu cần
                    
                    if isinstance(atk, BossBullet):
                        self.boss_bullets.add(atk)
                    elif isinstance(atk, PoisonPool):
                        atk.damage_interval = 500
                        self.poison_pools.add(atk)
                    elif isinstance(atk, Laser):
                        self.lasers.add(atk)
                    elif isinstance(atk, Web):
                        self.webs.add(atk)

        # --- Tutorial practice detection ---
        if getattr(self, "tutorial_mode", False) and getattr(self, 'npc', None) is not None and not self.tutorial_followup_done:
            try:
                # if player shot at least one bullet
                if self.player is not None and hasattr(self.player, 'ammo'):
                    if self.player.ammo < self.player.max_ammo:
                        self.practice_started = True

                    # detect reload completion: ammo restored to full after having started practice
                    if self.practice_started and not getattr(self.player, 'reloading', False) and self.player.ammo == self.player.max_ammo:
                        # ensure initial tutorial dialog finished (npc not speaking and not waiting)
                        if not getattr(self.npc, 'is_speaking', False) and not getattr(self.npc, 'waiting_for_input', False):
                            # show follow-up dialog once (handled by NPC)
                            try:
                                self.npc.start_followup_after_reload(typing_delay=2)
                            except Exception:
                                pass
                            self.tutorial_followup_done = True
            except Exception:
                pass

        # --- Start serious training after follow-up dialog finished ---
        if getattr(self, 'tutorial_mode', False) and self.tutorial_followup_done and not self.training_started:
            # wait until follow-up dialog fully finished (npc not speaking and not waiting)
            if not getattr(self.npc, 'is_speaking', False) and not getattr(self.npc, 'waiting_for_input', False):
                try:
                    self.npc.start_training_intro(typing_delay=2)
                except Exception:
                    pass
                self.training_started = True

        # --- Spawn training enemies inside the enclosure (they stay trapped) ---
        if self.training_started and not getattr(self, 'training_enemies_created', False):
            try:
                # create enemies at training spawn points so they are pre-placed inside the enclosure
                spawns = getattr(trainingmap, 'TRAINING_SPAWNS', None)
                tile_size = 64
                try:
                    sample_img = next(iter(self.map_manager.tiles.values()))
                    tile_size = sample_img.get_width()
                except Exception:
                    pass

                if spawns:
                    # create 15 Monster1 and 5 Monster2, distributing across available interior cells
                    total_m1 = 15
                    total_m2 = 5
                    cells = list(spawns)
                    if not cells:
                        # fallback to the first spawn cell if nothing else
                        cells = [spawns[0]] if spawns else [(1,1)]
                    # shuffle-like distribution by cycling index
                    idx = 0
                    # place Monster1
                    for i in range(total_m1):
                        sx, sy = cells[idx % len(cells)]
                        idx += 1
                        x = sx * tile_size + tile_size // 2
                        y = sy * tile_size + tile_size // 2
                        e = Enemy(self.player, map_manager=self.map_manager)
                        e.rect.center = (x, y)
                        try:
                            e.pos = pygame.Vector2((x, y))
                        except Exception:
                            pass
                        self.enemies.add(e)
                        self.all_sprites.add(e)

                    # place Monster2
                    for i in range(total_m2):
                        sx, sy = cells[idx % len(cells)]
                        idx += 1
                        x = sx * tile_size + tile_size // 2
                        y = sy * tile_size + tile_size // 2
                        m = Monster2(self.player, map_manager=self.map_manager)
                        m.rect.center = (x, y)
                        try:
                            m.pos = pygame.Vector2((x, y))
                        except Exception:
                            pass
                        self.enemies.add(m)
                        self.all_sprites.add(m)
                else:
                    for i in range(10):
                        e = Enemy(self.player, map_manager=self.map_manager)
                        self.enemies.add(e)
                        self.all_sprites.add(e)
                    for i in range(3):
                        m = Monster2(self.player, map_manager=self.map_manager)
                        self.enemies.add(m)
                        self.all_sprites.add(m)
            except Exception:
                pass
            # mark created (still trapped until gate opens)
            self.training_enemies_created = True
            self.training_spawned = True

        # --- When NPC finished guiding the specific line, open enclosure gate so enemies pour out ---
        if getattr(self, 'training_enemies_created', False) and not getattr(self, 'training_gate_opened', False):
            try:
                release_line = getattr(self, 'training_release_line', None)
                if release_line and getattr(self, 'npc', None) is not None:
                    # open gate only when NPC finished typing that exact line
                    if getattr(self.npc, 'waiting_for_input', False) and getattr(self.npc, 'full_text', '') == release_line:
                        enclosure = getattr(trainingmap, 'ENCLOSURE_WALLS', None)
                        if enclosure:
                            for gx, gy in enclosure:
                                try:
                                    self.map_manager.layout[gy][gx] = 'co'
                                except Exception:
                                    pass
                            try:
                                self.map_manager.build_collision(self.map_manager.layout)
                            except Exception:
                                pass
                            try:
                                SoundManager.play_begin_sound()
                            except Exception:
                                pass
                            self.training_gate_opened = True
            except Exception:
                pass

        # --- detect training completion (all spawned enemies dead) ---
        if getattr(self, 'training_enemies_created', False) and not self.training_completed:
            if len(self.enemies) == 0:
                try:
                    self.npc.start_training_end(typing_delay=2)
                except Exception:
                    pass
                self.training_completed = True

        # --- after final dialog, return to main menu once dialog done ---
        if self.training_completed and not self.training_moved_map:
            if not getattr(self.npc, 'is_speaking', False) and not getattr(self.npc, 'waiting_for_input', False):
                try:
                    # go back to main menu instead of immediately switching maps
                    self.game_state = "MENU"
                    SoundManager.stop_music()
                    SoundManager.play_menu_music(volume=0.4)
                    self.training_moved_map = True
                except Exception:
                    pass

        # va chạm đạn - quái
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            dmg = len(bullets_hit)
            if hasattr(enemy, "take_damage"):
                enemy.take_damage(dmg)
            else:
                enemy.hp = getattr(enemy, "hp", 0) - dmg

            # persist boss health if applicable
            try:
                if enemy.__class__.__name__ == 'Boss':
                    # update persistent health
                    try:
                        self.boss_persistent_health = max(0, int(getattr(enemy, 'health', 0)))
                    except Exception:
                        pass
            except Exception:
                pass

            if getattr(enemy, "hp", 1) <= 0:
                # boss gets special handling: award 1000 and reset persistent health
                if enemy.__class__.__name__ == 'Boss':
                    try:
                        if not getattr(self, 'tutorial_mode', False):
                            self.ui.score += 1000
                            if self.ui.score > self.ui.high_score:
                                self.ui.high_score = self.ui.score
                                self.ui.save_high_score()
                    except Exception:
                        pass
                    # reset persistent health for next full boss
                    try:
                        self.boss_persistent_health = getattr(enemy, 'max_health', 100)
                    except Exception:
                        self.boss_persistent_health = 100
                else:
                    if hasattr(enemy, "score_value"):
                        try:
                            # do not count scores earned during tutorial/training runs
                            if not getattr(self, 'tutorial_mode', False):
                                self.ui.score += enemy.score_value
                                if self.ui.score > self.ui.high_score:
                                    self.ui.high_score = self.ui.score
                                    self.ui.save_high_score()
                        except Exception:
                            pass
                enemy.kill()

        # Thêm vào cuối hàm update() trong main.py
        if self.player is not None:
            # 1. Va chạm với đạn thường của Boss
            if pygame.sprite.spritecollide(self.player, self.boss_bullets, True):
                self.player.health -= 10  # Trừ máu trực tiếp
                self.player.hit_timer = pygame.time.get_ticks() # Hiệu ứng nhấp nháy
                self.trigger_hit_effect()
                SoundManager.play_hurt_sound() # Phát âm thanh khi trúng đòn

            # 2. Va chạm với đầm lầy độc (Poison Pool)
            pool_hits = pygame.sprite.spritecollide(self.player, self.poison_pools, False)
            for pool in pool_hits:
                # Giả sử PoisonPool có hàm gây dame theo thời gian
                if hasattr(pool, 'apply_damage'):
                    pool.apply_damage(self.player)

        # boss bullets hit player
        try:
            bb_hits = pygame.sprite.spritecollide(self.player, self.boss_bullets, True)
            for b in bb_hits:
                SoundManager.play_hurt_sound()
                self.player.hit_timer = pygame.time.get_ticks()
                self.player.health -= 12
        except Exception:
            pass

        # poison pools damage over time
        try:
            now = pygame.time.get_ticks()
            pools = pygame.sprite.spritecollide(self.player, self.poison_pools, False)
            for p in pools:
                last = getattr(p, 'last_hurt', 0)
                if now - last >= getattr(p, 'damage_interval', 500):
                    try:
                        self.player.health -= 5
                        p.last_hurt = now
                    except Exception:
                        pass
        except Exception:
            pass

        # lasers instant damage (only once per laser)
        try:
            lasers = pygame.sprite.spritecollide(self.player, self.lasers, False)
            for l in lasers:
                if not getattr(l, 'hit_done', False):
                    try:
                        self.player.health -= 20
                        l.hit_done = True
                        SoundManager.play_hurt_sound()
                    except Exception:
                        pass
        except Exception:
            pass

        # webs: root player for duration (handled by web sprite on collision)
        try:
            webs_hit = pygame.sprite.spritecollide(self.player, self.webs, True)
            for w in webs_hit:
                try:
                    now = pygame.time.get_ticks()
                    dur = getattr(w, 'root_duration', 3000)
                    # set player frozen_until timestamp
                    try:
                        self.player.frozen_until = now + dur
                    except Exception:
                        setattr(self.player, 'frozen_until', now + dur)
                    # optional sound
                    try:
                        SoundManager.play_hurt_sound()
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass
        # Trong Game.update()
        # Thêm điều kiện kiểm tra thời gian bất tử (ví dụ: 500ms)
        now = pygame.time.get_ticks()
        is_invincible = now - getattr(self.player, 'hit_timer', 0) < self.flash_duration

        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            if not is_invincible:
                self.player.hit_timer = now
                SoundManager.play_hurt_sound()
                
                if getattr(enemy, "type", "") == "boss":
                    self.player.health -= 20
                else:
                    self.player.health -= 10
                    enemy.kill() # Chỉ giết quái thường khi va chạm
        # Nếu đang ở tutorial, kiểm tra điều kiện hoàn thành: player đi tới gần mép phải map
        if getattr(self, "tutorial_mode", False) and self.player is not None:
            try:
                tile_size = next(iter(self.map_manager.tiles.values())).get_width()
            except Exception:
                tile_size = 64
            cols = len(self.map_manager.layout[0]) if self.map_manager.layout else 0
            # nếu player vượt quá cột thứ cols-4 thì xem là hoàn thành tutorial
            if self.player.rect.centerx >= (cols - 4) * tile_size:
                # chuyển sang màn chính
                self.switch_to_main_map()
        # --- Trong Game.update ---
        self.heal_spawn_timer += 1
        if self.heal_spawn_timer >= 15 * FPS and len(self.heal_items) < 3:
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
            # Lưu high score lần cuối nếu phá kỷ lục
            if self.ui.score > self.ui.high_score:
                self.ui.high_score = self.ui.score
                self.ui.save_high_score()
            # record this play session's score in recent scores list (skip tutorial runs)
            try:
                if not getattr(self, 'tutorial_mode', False):
                    self.ui.record_score(self.ui.score)
            except Exception:
                pass
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
        if self.game_state == "HIGHSCORE":
            self.ui.draw_highscore_screen()
            pygame.display.flip()
            return
        if self.game_state == "PROFILE":
            self.ui.draw_profile_screen()
            pygame.display.flip()
            return

        # PLAYING
        self.screen.fill((30, 30, 30))

        # 1) draw map
        try:
            self.map_manager.draw(self.screen, self.camera)
        except Exception:
            pass

        # 2) Vẽ Túi máu (Dưới chân Player)
        for item in self.heal_items:
            try:
                self.screen.blit(item.image, self.camera.apply(item.rect))
            except Exception:
                try:
                    self.screen.blit(item.image, item.rect)
                except Exception:
                    pass

        # 3) draw bullets (trước player để layering)
        for b in self.bullets:
            try:
                draw_rect = self.camera.apply(b.rect) if self.camera else b.rect
            except Exception:
                draw_rect = b.rect
            try:
                self.screen.blit(b.image, draw_rect)
            except Exception:
                pass

        # debug overlay removed: no on-screen bullet count or debug rectangles

        # 4) draw sprites with camera
        for s in self.all_sprites:
            try:
                draw_rect = self.camera.apply(s.rect) if self.camera else s.rect
            except Exception:
                draw_rect = s.rect

            # player hit flash
            if s == self.player and getattr(s, 'hit_timer', 0) > 0:
                try:
                    current_time = pygame.time.get_ticks()
                    if current_time - s.hit_timer < self.flash_duration:
                        red_img = s.image.copy()
                        red_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
                        self.screen.blit(red_img, draw_rect)
                    else:
                        s.hit_timer = 0
                        self.screen.blit(s.image, draw_rect)
                except Exception:
                    try:
                        self.screen.blit(s.image, draw_rect)
                    except Exception:
                        pass
            else:
                try:
                    self.screen.blit(s.image, draw_rect)
                except Exception:
                    pass

        # draw NPC dialog (if any)
        try:
            if getattr(self, 'npc', None) is not None:
                font = getattr(self, 'dialog_font', pygame.font.SysFont(None, 22))
                try:
                    self.npc.draw_dialog(self.screen, font, (WIDTH, HEIGHT))
                except Exception:
                    pass
        except Exception:
            pass

        # UI + ammo
        try:
            # draw HUD: include ammo when player present
            if self.player is not None:
                try:
                    # draw UI HUD (score etc.) then draw player's detailed HUD visuals
                    self.ui.draw_hud(self.player.health, ammo=getattr(self.player, 'ammo', None), max_ammo=getattr(self.player, 'max_ammo', None))
                    try:
                        # re-enable old player HUD visuals
                        self.player.draw_health(self.screen)
                    except Exception:
                        pass
                    try:
                        self.player.draw_ammo(self.screen)
                    except Exception:
                        pass
                except Exception:
                    self.ui.draw_hud(self.player.health)
            else:
                self.ui.draw_hud(0)
        except Exception:
            try:
                self.ui.draw_hud(0)
            except Exception:
                pass

        try:
            self.ui.draw_ingame_buttons()
        except Exception:
            pass

        # --- Boss health bar (top-center, below score) ---
        try:
            boss = None
            for e in self.enemies:
                if e.__class__.__name__ == 'Boss':
                    boss = e
                    break
            if boss is not None:
                try:
                    # place under score (UI draws score at midtop y=12)
                    score_h = 0
                    try:
                        score_h = self.ui.small_font.get_height()
                    except Exception:
                        score_h = 18
                    bar_w = 320
                    bar_h = 14
                    x = WIDTH // 2 - bar_w // 2
                    y = 12 + score_h + 8
                    # background
                    pygame.draw.rect(self.screen, (20, 20, 20), (x-2, y-2, bar_w+4, bar_h+4))
                    pygame.draw.rect(self.screen, (40, 10, 60), (x, y, bar_w, bar_h))
                    # fill
                    try:
                        frac = max(0.0, min(1.0, float(boss.health) / float(getattr(boss, 'max_health', 100))))
                    except Exception:
                        frac = 1.0
                    fill_w = int(bar_w * frac)
                    pygame.draw.rect(self.screen, (180, 0, 180), (x, y, fill_w, bar_h))
                    pygame.draw.rect(self.screen, (200, 200, 200), (x, y, bar_w, bar_h), 2)
                    # hp text
                    try:
                        txt = self.ui.small_font.render(f"Boss {int(boss.health)}/{int(getattr(boss,'max_health',100))}", True, (255, 255, 255))
                        self.screen.blit(txt, txt.get_rect(center=(WIDTH//2, y + bar_h//2)))
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass

        # ammo HUD removed: player.draw_ammo() not called so player enters directly

        # pause overlay
        try:
            if getattr(self.ui, "is_paused", False):
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                try:
                    pause_text = self.ui.font.render("PAUSED", True, (255, 255, 255))
                    self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                                    
                except Exception:
                    pass
                    # VẼ NÚT CONTINUE
                if hasattr(self.ui, 'continue_btn_img') and self.ui.continue_btn_img:
                    self.screen.blit(self.ui.continue_btn_img, self.ui.continue_btn_rect)
        except Exception:
            pass

        # skill UI
        try:
            if self.player is not None:
                try:
                    # still update skills (logic/cooldowns) but do not draw skill UI
                    self.player.update_skills()
                except Exception:
                    pass
                try:
                    self.player.draw_shield(self.screen)
                except Exception:
                    pass
                # skill UI rendering intentionally removed
        except Exception:
            pass
        except Exception:
            pass

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
                            self.new_game(tutorial=False)

            self.update()
            self.draw()
            self.clock.tick(FPS)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode (keeps logical resolution WIDTHxHEIGHT)."""
        try:
            self.fullscreen = not getattr(self, 'fullscreen', False)
            if self.fullscreen:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            # update UI to use new surface
            try:
                self.ui.screen = self.screen
            except Exception:
                pass
            # force redraw of menu background if needed
            pygame.display.flip()
        except Exception:
            pass
    
    def spawn_enemy(self):
        """Spawn một enemy thông thường, tránh player"""
        # Do not spawn normal enemies during tutorial/training
        if getattr(self, 'tutorial_mode', False):
            return
        # --- THÊM LOGIC PHÁT ÂM THANH 1 LẦN TẠI ĐÂY ---
        if not self.has_played_begin_sound:
            SoundManager.play_begin_sound()
            self.has_played_begin_sound = True
        # if teleport gates exist (main map), spawn at a random gate center
        spawn_pos = None
        try:
            gates_list = list(self.gates.sprites()) if hasattr(self, 'gates') else []
            if gates_list:
                g = random.choice(gates_list)
                spawn_pos = g.get_spawn_pos()
        except Exception:
            spawn_pos = None

        if spawn_pos is None:
            spawn_pos = self.find_free_tile_center(
                avoid_pos=self.player.rect.center if self.player else None,
                min_dist=ENEMY_SPAWN_MIN_DIST
            )

        # choose Monster2 sometimes (stronger) and allow it to spawn from gates
        try:
            if random.random() < MONSTER2_SPAWN_CHANCE:
                enemy = Monster2(self.player, map_manager=self.map_manager)
            else:
                enemy = Enemy(self.player, map_manager=self.map_manager)
        except Exception:
            enemy = Enemy(self.player, map_manager=self.map_manager)

        # place enemy, avoid being placed overlapping walls (Monster2 prone to get stuck)
        enemy.rect.center = spawn_pos
        enemy.pos = pygame.Vector2(spawn_pos)

        # if initial placement collides with a wall, nudge toward map center until free
        try:
            test_rect = enemy.rect.copy()
            blocked = False
            for wall in getattr(self.map_manager, 'collision_rects', []):
                if test_rect.colliderect(wall):
                    blocked = True
                    break
            if blocked:
                # compute map center in pixels
                layout = getattr(self.map_manager, 'layout', [])
                tile_size = 64
                try:
                    sample_img = next(iter(self.map_manager.tiles.values()))
                    tile_size = sample_img.get_width()
                except Exception:
                    pass
                rows = len(layout)
                cols = len(layout[0]) if rows > 0 else 0
                map_center = pygame.Vector2((cols * tile_size) / 2, (rows * tile_size) / 2)
                attempts = 0
                while blocked and attempts < 8:
                    attempts += 1
                    dirv = (map_center - pygame.Vector2(enemy.rect.center))
                    if dirv.length_squared() == 0:
                        dirv = pygame.Vector2(1, 0)
                    dirn = dirv.normalize()
                    # nudge by half a tile toward center
                    new_center = pygame.Vector2(enemy.rect.center) + dirn * (tile_size // 2)
                    enemy.rect.center = (int(new_center.x), int(new_center.y))
                    enemy.pos = pygame.Vector2(enemy.rect.center)
                    # re-check collisions
                    test_rect = enemy.rect.copy()
                    blocked = False
                    for wall in getattr(self.map_manager, 'collision_rects', []):
                        if test_rect.colliderect(wall):
                            blocked = True
                            break
        except Exception:
            pass

        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def spawn_boss(self):
        """Spawn boss khi score đủ, ưu tiên trong tầm nhìn và tránh kẹt tường"""
        if getattr(self, 'tutorial_mode', False):
            return

        # 1. Xác định thông số bản đồ và tile
        layout = self.map_manager.layout
        if not layout: return
        
        # Lấy tile_size an toàn
        try:
            sample_img = next(iter(self.map_manager.tiles.values()))
            tile_size = sample_img.get_width()
        except StopIteration:
            tile_size = 64

        rows = len(layout)
        cols = len(layout[0])

        # 2. Xác định vùng nhìn thấy (Viewport) để ưu tiên spawn
        # Lưu ý: Tùy vào class Camera, vx/vy có thể là self.camera.rect.x hoặc offset
        try:
            vx = -self.camera.offset.x  # World X tại góc trái màn hình
            vy = -self.camera.offset.y  # World Y tại góc trên màn hình
        except:
            vx, vy = 0, 0

        # Giới hạn vùng tìm kiếm trong tile (tránh sát mép map quá 1 tile)
        tx_min = max(1, int(vx // tile_size))
        ty_min = max(1, int(vy // tile_size))
        tx_max = min(cols - 2, int((vx + WIDTH) // tile_size))
        ty_max = min(rows - 2, int((vy + HEIGHT) // tile_size))

        # Sửa lỗi tx_min > tx_max nếu camera ở sát rìa
        if tx_min >= tx_max: tx_min, tx_max = 1, cols - 2
        if ty_min >= ty_max: ty_min, ty_max = 1, rows - 2

        spawn_pos = None
        # 3. Vòng lặp tìm vị trí hợp lý
        tries = 0
        while tries < 20: # ENEMY_SPAWN_TRIES
            tries += 1
            tx = random.randint(tx_min, tx_max)
            ty = random.randint(ty_min, ty_max)
            x = tx * tile_size + tile_size // 2
            y = ty * tile_size + tile_size // 2

            # Kiểm tra khoảng cách với Player (Boss không được đè lên đầu Player)
            if self.player:
                dist_sq = (x - self.player.rect.centerx)**2 + (y - self.player.rect.centery)**2
                if dist_sq < 300**2: # Không spawn trong bán kính 300px
                    continue

            # Kiểm tra va chạm tường cho Boss (giả sử Boss to khoảng 1.5 tile)
            boss_test_size = int(tile_size * 1.2) 
            test_rect = pygame.Rect(0, 0, boss_test_size, boss_test_size)
            test_rect.center = (x, y)
            
            blocked = any(test_rect.colliderect(wall) for wall in self.map_manager.collision_rects)
            
            if not blocked:
                spawn_pos = (x, y)
                break

        # 4. Fallback nếu không tìm được chỗ trong Viewport
        if spawn_pos is None:
            spawn_pos = self.find_free_tile_center(
                avoid_pos=self.player.rect.center if self.player else None,
                min_dist=400
            )

        # 5. Khởi tạo Boss
        boss = Boss(self.player, map_manager=self.map_manager, start_pos=spawn_pos)
        boss.type = 'boss'
        
        # Khôi phục máu cũ nếu có (Persistent Health)
        boss.max_health = getattr(boss, 'max_health', 150) # Tăng máu boss cho xứng tầm
        boss.health = getattr(self, 'boss_persistent_health', boss.max_health)
        
        self.enemies.add(boss)
        self.all_sprites.add(boss)

if __name__ == "__main__":
    g = Game()
    g.run()



