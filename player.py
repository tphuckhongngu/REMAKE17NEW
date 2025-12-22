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
    def __init__(self, bullet_group=None, start_pos=None):
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

        # font HUD
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 26)

    # -------- input & movement --------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
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
        """Gọi khi click chuột trái"""
        if not self.can_shoot():
            return
        # hướng tới chuột
        mx, my = pygame.mouse.get_pos()
        dir_vec = pygame.math.Vector2(mx, my) - self.pos
        if dir_vec.length_squared() == 0:
            return
        vel = dir_vec.normalize() * BULLET_SPEED

        # spawn point: hơi chếch ra trước nhân vật
        spawn = self.pos + dir_vec.normalize() * (PLAYER_SIZE * 0.5 + 4)
        if self.bullet_group is not None:
            b = Bullet(spawn, vel)
            self.bullet_group.add(b)
        
        
        self.ammo -= 1
        self.last_shot = pygame.time.get_ticks()

        # auto reload khi hết
        if self.ammo <= 0:
            self.start_reload()

    # -------- rotation --------
    def rotate_towards_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.rect.centerx
        dy = my - self.rect.centery
        # angle in degrees where 0 is right; positive turns ccw
        angle = math.degrees(math.atan2(-dy, dx))
        # rotate currently selected original image
        self.image = pygame.transform.rotate(self.current_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    # -------- constraint to screen --------
    def constrain_to_screen(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        # đồng bộ pos với rect center
        self.pos = pygame.math.Vector2(self.rect.center)

    # -------- HUD drawing --------
    def draw_ammo(self, screen):
        hud_x = 220   # dời sang phải, tránh HUD máu
        hud_y = 10

        if self.reloading:
            text_surf = self.font.render("Reloading...", True, (255, 100, 100))
        else:
            text_surf = self.font.render(f"Ammo: {self.ammo}/{self.max_ammo}", True, (255, 255, 255))

        screen.blit(text_surf, (hud_x, hud_y))

        bar_x = hud_x
        bar_y = hud_y + 30
        bar_w = 180
        bar_h = 12

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * (self.ammo / self.max_ammo))
        pygame.draw.rect(screen, (80, 200, 120), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2)

    # -------- update mỗi frame --------
    def update(self):
        # input + di chuyển
        self.handle_input()
        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # reload logic
        self.update_reload()

        # rotate theo chuột (dùng current_original hiện tại)
        self.rotate_towards_mouse()

        # giới hạn màn hình
        self.constrain_to_screen()
