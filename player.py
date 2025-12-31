# player.py
import pygame
import math
from settings import *   # dùng WIDTH, HEIGHT, PLAYER_SPEED, PLAYER_SIZE, BULLET_SPEED, BULLET_LIFETIME, ...
from sounds import SoundManager
from bullet import Bullet



# Cấu hình ammo / reload / fire rate (theo yêu cầu)
MAX_AMMO = 15
RELOAD_MS = 3000      # 3 giây
FIRE_RATE_MS = 200    # khoảng thời gian giữa 2 viên (ms)


class Player(pygame.sprite.Sprite):
    def __init__(self, bullet_group=None, start_pos=None, map_manager=None, all_sprites=None):
        self.camera = None
        super().__init__()
        


        # cố gắng load ảnh từ folder player/
        try:
            gun_img = pygame.image.load("player/survivor1_gun.png").convert_alpha()
            reload_img = pygame.image.load("player/survivor1_reload.png").convert_alpha()
        except Exception:
            # fallback: vẽ tạm 1 circle + "súng" chữ nhật
            gun_img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(gun_img, (0, 150, 200), (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2)
            pygame.draw.rect(gun_img, (50, 50, 50), (PLAYER_SIZE//2, PLAYER_SIZE//2 - 6, PLAYER_SIZE//2, 12))
            reload_img = gun_img.copy()

        # scale để phù hợp PLAYER_SIZE
        gun_img = pygame.transform.smoothscale(gun_img, (PLAYER_SIZE, PLAYER_SIZE))
        reload_img = pygame.transform.smoothscale(reload_img, (PLAYER_SIZE, PLAYER_SIZE))

        # giữ bản gốc để xoay
        self.original_gun = gun_img
        self.original_reload = reload_img
        self.current_original = self.original_gun

        # hình hiện tại và rect
        self.image = self.current_original
        pos = (WIDTH//2, HEIGHT//2) if start_pos is None else start_pos
        self.rect = self.image.get_rect(center=pos)

        # vị trí dạng float
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)

        # trạng thái
        self.health = PLAYER_HP
        # frozen until timestamp (ms) when rooted by web
        self.frozen_until = 0

        # ammo / reload
        self.max_ammo = MAX_AMMO
        self.ammo = self.max_ammo
        self.reloading = False
        self.reload_time = RELOAD_MS
        self.reload_start = 0

        # tốc độ bắn
        self.fire_rate = FIRE_RATE_MS
        self.last_shot = 0

        # nhóm đạn để spawn
        self.bullet_group = bullet_group
        self.map_manager = map_manager
        # optional reference to global sprite group so bullets can be drawn/updated there too
        self.all_sprites = all_sprites


        # font HUD
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 26)

    # -------- input & movement --------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        self.velocity.x = 0
        self.velocity.y = 0
        # if frozen (rooted), do not allow movement
        if now < getattr(self, 'frozen_until', 0):
            # allow reload while frozen, but no movement
            pass
        else:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.velocity.y = -PLAYER_SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.velocity.y = PLAYER_SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velocity.x = -PLAYER_SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velocity.x = PLAYER_SPEED

        # nhấn R để reload nếu cần
        if keys[pygame.K_r] and (not self.reloading) and (self.ammo < self.max_ammo):
            self.start_reload()

    # -------- reload logic --------
    def start_reload(self):
        # bắt đầu nạp đạn: khóa bắn, đổi ảnh
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()
        self.current_original = self.original_reload

        # play reload SFX (will loop; will be stopped by timer or when reload finishes)
        SoundManager.play_reload_sound(duration_ms=self.reload_time)

    def update_reload(self):
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.reloading = False
                self.ammo = self.max_ammo
                self.current_original = self.original_gun

                # stop reload SFX immediately (in case timer didn't fire)
                SoundManager.stop_reload_sound()

    # -------- shooting --------
    def can_shoot(self):
        now = pygame.time.get_ticks()
        if self.reloading:
            return False
        if now - self.last_shot < self.fire_rate:
            return False
        if self.ammo <= 0:
            return False
        return True

    def shoot(self):
        if not self.can_shoot():
            return

        mx, my = pygame.mouse.get_pos()
        if self.camera:
            mx += self.camera.offset[0]
            my += self.camera.offset[1]

        dir_vec = pygame.math.Vector2(mx, my) - self.pos
        if dir_vec.length_squared() == 0:
            return

        vel = dir_vec.normalize() * BULLET_SPEED
        spawn = self.pos + dir_vec.normalize() * (PLAYER_SIZE * 0.5 + 4)

        # ensure spawn not inside wall: nudge forward if colliding
        try:
            if self.map_manager and hasattr(self.map_manager, "collision_rects"):
                test_pos = pygame.math.Vector2(spawn)
                safe = False
                attempts = 0
                while attempts < 10:
                    attempts += 1
                    test_rect = pygame.Rect(0, 0, 8, 8)
                    test_rect.center = (int(test_pos.x), int(test_pos.y))
                    coll = False
                    for w in self.map_manager.collision_rects:
                        if test_rect.colliderect(w):
                            coll = True
                            break
                    if not coll:
                        safe = True
                        break
                    # nudge forward
                    test_pos += dir_vec.normalize() * 8
                if safe:
                    spawn = test_pos
        except Exception:
            pass

        if self.bullet_group is not None:
            b = Bullet(spawn, vel, self.map_manager)
            try:
                self.bullet_group.add(b)
            except Exception:
                # fallback: ignore add errors but keep debug
                pass
            # debug
            try:
                print(f"Shot bullet at {spawn} vel={vel}")
            except Exception:
                pass

        self.ammo -= 1
        self.last_shot = pygame.time.get_ticks()

        if self.ammo <= 0:
            self.start_reload()

    def draw_health(self, screen):
        # draw health bar at top-left, red fill and centered HP text
        hud_x = 12
        hud_y = 12
        bar_w = 220
        bar_h = 18
        try:
            max_hp = PLAYER_HP
        except Exception:
            max_hp = 100
        hp_frac = max(0.0, min(1.0, self.health / float(max_hp) if max_hp else 0.0))

        # background and outer border
        pygame.draw.rect(screen, (20, 20, 20), (hud_x-2, hud_y-2, bar_w+4, bar_h+4))
        pygame.draw.rect(screen, (30, 30, 30), (hud_x, hud_y, bar_w, bar_h))

        # red fill
        fill_w = int(bar_w * hp_frac)
        pygame.draw.rect(screen, (200, 60, 60), (hud_x, hud_y, fill_w, bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (hud_x, hud_y, bar_w, bar_h), 2)

        # centered HP text
        try:
            txt = self.font.render(f"{int(self.health)}/{int(max_hp)}", True, (255, 255, 255))
            txt_rect = txt.get_rect(center=(hud_x + bar_w//2, hud_y + bar_h//2))
            screen.blit(txt, txt_rect)
        except Exception:
            pass


    # -------- rotation --------
    def rotate_towards_mouse(self):
        mx, my = pygame.mouse.get_pos()

        if self.camera:
            mx += self.camera.offset[0]
            my += self.camera.offset[1]

        dx = mx - self.rect.centerx
        dy = my - self.rect.centery

        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.current_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    

    # -------- HUD drawing --------
    def draw_ammo(self, screen):
        # Place ammo bar below the health bar, avoid overlap
        hud_x = 12
        hud_y = 12
        bar_w = 220
        bar_h = 18
        gap = 12
        bar_x = hud_x
        bar_y = hud_y + bar_h + gap

        # background
        pygame.draw.rect(screen, (20, 20, 20), (bar_x-2, bar_y-2, bar_w+4, bar_h+4))
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h))

        # ammo fill (blue)
        try:
            frac = max(0.0, min(1.0, float(self.ammo) / float(self.max_ammo)))
        except Exception:
            frac = 0.0
        fill_w = int(bar_w * frac)
        pygame.draw.rect(screen, (60, 140, 220), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2)

        # ammo text centered
        try:
            if self.reloading:
                txt = self.font.render("Reloading...", True, (255, 100, 100))
            else:
                txt = self.font.render(f"{int(self.ammo)}/{int(self.max_ammo)}", True, (255, 255, 255))
            txt_rect = txt.get_rect(center=(bar_x + bar_w//2, bar_y + bar_h//2))
            screen.blit(txt, txt_rect)
        except Exception:
            pass


    def move(self, dx, dy):
        self.pos.x += dx
        self.rect.centerx = int(self.pos.x)

        if self.map_manager:
            # sử dụng rect nhỏ hơn để kiểm tra va chạm (tránh vấn đề rect xoay/khớp ảnh)
            test_rect = self.rect.copy()
            test_rect.inflate_ip(-8, -8)
            for wall in self.map_manager.collision_rects:
                if test_rect.colliderect(wall):
                    self.pos.x -= dx
                    self.rect.centerx = int(self.pos.x)
                    break

        self.pos.y += dy
        self.rect.centery = int(self.pos.y)

        if self.map_manager:
            test_rect = self.rect.copy()
            test_rect.inflate_ip(-8, -8)
            for wall in self.map_manager.collision_rects:
                if test_rect.colliderect(wall):
                    self.pos.y -= dy
                    self.rect.centery = int(self.pos.y)
                    break




    # -------- update mỗi frame --------
    def update(self):
        self.handle_input()
        self.move(self.velocity.x, self.velocity.y)
        self.update_reload()
        self.rotate_towards_mouse()

