import os
import pygame
import math
class Boss(pygame.sprite.Sprite):
    def __init__(self, player, map_manager, start_pos=(0, 0)):
        super().__init__()
        self.player = player
        self.map_manager = map_manager

        self.frames = [] 
        self.delays = []  # Tốc độ chuyển frame (ms)

        # --- LOGIC NẠP ẢNH TỪ THƯ MỤC MONSTER/BOSS ---
        frame_count = 10
        base_path = os.path.join('monster', 'boss')
        
        for i in range(1, frame_count + 1):
            file_name = f"frame_{i}.png"
            path = os.path.join(base_path, file_name)
            
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    # Bạn có thể thêm dòng scale ảnh ở đây nếu ảnh quá to/nhỏ
                    # img = pygame.transform.scale(img, (128, 128)) 
                    self.frames.append(img)
                    self.delays.append(100)  # Mặc định 100ms mỗi frame
            except Exception as e:
                pass

        # Nếu không nạp được ảnh nào, dùng hình tròn tạm thời làm fallback
        if not self.frames:
            surf = pygame.Surface((96, 96), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 30, 30), (48, 48), 44)
            self.frames = [surf]
            self.delays = [100]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        # Tọa độ
        try:
            self.pos = pygame.Vector2(start_pos)
        except Exception:
            self.pos = pygame.Vector2(0, 0)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self._last_update = pygame.time.get_ticks()

        # Stats và Logic giữ nguyên như cũ
        self.max_health = 100
        self.health = 100
        self.speed = 0.0
        self.visible_duration = 5000
        self.blink_duration = 1000
        self.spawn_time = pygame.time.get_ticks()
        self.blinking = False
        self.hit_rect = self.rect.copy()

        self.last_shot = 0
        self.shot_delay = 1500
        self.last_poison = 0
        self.poison_delay = 5000
        self.last_laser = 0
        self.laser_delay = 10000
        self.pending_attacks = []

    def update(self, *args):
        now = pygame.time.get_ticks()
        if self.delays:
            if now - self._last_update >= (self.delays[self.frame_index] or 100):
                self._last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                # preserve center when switching frames
                try:
                    c = self.rect.center
                except Exception:
                    c = None
                self.image = self.frames[self.frame_index]
                try:
                    if c:
                        # rotate frame to face player (images have head at bottom)
                        try:
                            if getattr(self, 'player', None) is not None:
                                dirv = pygame.Vector2(self.player.rect.center) - pygame.Vector2(c)
                                if dirv.length() != 0:
                                    angle = math.degrees(math.atan2(dirv.y, dirv.x))
                                else:
                                    angle = 90
                                # image default faces down; rotate so down points to player
                                rotate_by = -angle + 90
                                rotated = pygame.transform.rotate(self.image, rotate_by)
                                self.rect = rotated.get_rect(center=c)
                                self.image = rotated
                            else:
                                self.rect = self.image.get_rect(center=c)
                        except Exception:
                            self.rect = self.image.get_rect(center=c)
                    else:
                        self.rect = self.image.get_rect(center=self.rect.center)
                except Exception:
                    self.rect = self.image.get_rect()
        # lifecycle: visible -> blink -> die
        age = now - self.spawn_time
        if not self.blinking and age >= self.visible_duration:
            # enter blinking phase
            self.blinking = True
            self.blink_start = now

        if self.blinking:
            if now - self.blink_start >= self.blink_duration:
                # remove boss after blink
                self.kill()
                return

        # Attacks only while visible (not during blink)
        if not self.blinking:
            try:
                # shoot purple bullets toward player
                if now - self.last_shot >= self.shot_delay:
                    self.last_shot = now
                    self.shoot_purple()

                # spawn poison pool
                if now - self.last_poison >= self.poison_delay:
                    self.last_poison = now
                    self.spawn_poison()

                # laser attack
                if now - self.last_laser >= self.laser_delay:
                    self.last_laser = now
                    self.fire_laser()
            except Exception:
                self.rect = self.image.get_rect()
                self.rect.center = c

        # Boss is stationary: do not attempt to move (ignores map collision)

    def take_damage(self, amount):
        # Reduce health; do NOT call self.kill() here to avoid removing the sprite
        # before centralized death processing (`process_enemy_death`) has a chance to
        # record that the player killed the boss (which is required to trigger VICTORY).
        self.health -= amount * 2
        if self.health <= 0:
            # clamp health to zero and leave actual sprite removal to process_enemy_death
            try:
                self.health = 0
            except Exception:
                pass

    def get_center(self):
        return self.rect.center

    # --- attack helpers create sprites and enqueue them into pending_attacks ---
    def shoot_purple(self):
        # create a BossBullet and enqueue it
        try:
            dirv = pygame.Vector2(self.player.rect.center) - self.pos
        except Exception:
            dirv = pygame.Vector2(0, 1)
        if dirv.length() == 0:
            dirv = pygame.Vector2(0, 1)
        vel = dirv.normalize() * 6
        b = BossBullet(self.pos, vel)
        self.pending_attacks.append(b)
        return b

    def spawn_poison(self):
        try:
            target = pygame.Vector2(self.player.rect.center)
        except Exception:
            target = self.pos
        pos = (self.pos + target) / 2
        p = PoisonPool(pos)
        self.pending_attacks.append(p)
        return p

    def fire_laser(self):
        # spawn a web that can root the player on contact
        try:
            target = pygame.Vector2(self.player.rect.center)
        except Exception:
            target = self.pos + pygame.Vector2(0, 1)
        w = Web(self.pos, target, radius=48, duration=3000, root_duration=3000)
        self.pending_attacks.append(w)
        return w


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, pos, vel):
        super().__init__()
        r = 8
        self.image = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 180), (r, r), r)
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        # short lifetime
        if pygame.time.get_ticks() - self.spawn_time > 5000:
            self.kill()


class PoisonPool(pygame.sprite.Sprite):
    def __init__(self, pos, radius=32, duration=3000):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (80, 0, 120, 160), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, length=800, width=8, duration=400):
        super().__init__()
        sv = pygame.Vector2(start_pos)
        tv = pygame.Vector2(target_pos)
        dirv = (tv - sv)
        dist = dirv.length()
        if dist == 0:
            dirv = pygame.Vector2(0, 1)
        else:
            dirv = dirv.normalize()
        end = sv + dirv * length

        # create an image representing the laser beam and rotate it
        w = int(length)
        h = int(width)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 200), (0, 0, w, h))
        angle = -math.degrees(math.atan2(dirv.y, dirv.x))
        self.image = pygame.transform.rotate(surf, angle)
        self.rect = self.image.get_rect()
        # center between start and end
        mid = (sv + end) / 2
        self.rect.center = (int(mid.x), int(mid.y))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()


class Web(pygame.sprite.Sprite):
    """A sticky web area that roots the player when touched.

    start_pos: pygame.Vector2 where web is centered (we'll use start_pos)
    root_duration: ms to freeze player
    duration: ms the web persists
    """
    def __init__(self, start_pos, target_pos=None, radius=48, duration=3000, root_duration=3000):
        super().__init__()
        # center the web between start and target if target provided
        try:
            sv = pygame.Vector2(start_pos)
        except Exception:
            sv = pygame.Vector2(0, 0)
        try:
            tv = pygame.Vector2(target_pos) if target_pos is not None else sv
        except Exception:
            tv = sv
        center = (sv + tv) / 2
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (120, 80, 160, 180), (radius, radius), radius)
        # some web-like lines
        try:
            pygame.draw.line(self.image, (200, 200, 240, 120), (radius, radius), (radius, 4), 2)
            pygame.draw.line(self.image, (200, 200, 240, 120), (radius, radius), (4, radius), 2)
        except Exception:
            pass
        self.rect = self.image.get_rect(center=(int(center.x), int(center.y)))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration
        self.root_duration = root_duration

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()
