import os
import pygame
import math

try:
    from PIL import Image, ImageSequence
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False


class Boss(pygame.sprite.Sprite):
    """A simple boss enemy that animates from a GIF (or a single image fallback).

    Constructor:
      Boss(player, map_manager, gif_path='anh/boss.gif', pos=None)

    If Pillow is available, frames are extracted and animated with per-frame delays.
    Otherwise the sprite will use a single surface loaded by pygame.image.load.
    """

    def __init__(self, player, map_manager, gif_path=None, start_pos=(0, 0)):
        super().__init__()
        self.player = player
        self.map_manager = map_manager

        self.frames = [] 
        self.delays = []  # milliseconds per frame

        # prefer user-provided gif, then project folder 'bossgif', then legacy 'anh'
        path = gif_path or os.path.join('bossgif', 'boss.gif')
        if not os.path.exists(path):
            path = os.path.join('anh', 'boss.gif')
        if _HAS_PIL:
            try:
                im = Image.open(path)
                for frame in ImageSequence.Iterator(im):
                    rgba = frame.convert('RGBA')
                    data = rgba.tobytes()
                    surf = pygame.image.fromstring(data, rgba.size, 'RGBA')
                    self.frames.append(surf)
                    # GIF frame durations are in hundredths of a second sometimes missing
                    self.delays.append(frame.info.get('duration', 100))
            except Exception:
                self._load_fallback(path)
        else:
            self._load_fallback(path)

        if not self.frames:
            # create a visible fallback
            surf = pygame.Surface((96, 96), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 30, 30), (48, 48), 44)
            self.frames = [surf]
            self.delays = [100]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        # position (use start_pos pixel coords)
        try:
            self.pos = pygame.Vector2(start_pos)
        except Exception:
            self.pos = pygame.Vector2(self.rect.center)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # animation timer
        self._last_update = pygame.time.get_ticks()

        # boss stats
        self.max_health = 100
        self.health = 100

        # boss is stationary (per user request)
        self.speed = 0.0

        # lifecycle timing: visible_duration, blink_duration (ms)
        self.visible_duration = 5000
        self.blink_duration = 1000
        self.spawn_time = pygame.time.get_ticks()
        self.blinking = False

        # collision box (approx)
        self.hit_rect = self.rect.copy()

        # attack timers
        self.last_shot = 0
        self.shot_delay = 800  # ms between purple shots
        self.last_poison = 0
        self.poison_delay = 2000  # ms between poison spawns
        self.last_laser = 0
        self.laser_delay = 3000  # ms between laser attacks

        # queue for sprites the boss wants spawned this frame
        self.pending_attacks = []

    def _load_fallback(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            self.frames = [img]
            self.delays = [100]
        except Exception:
            self.frames = []
            self.delays = []

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
        self.health -= amount
        if self.health <= 0:
            self.kill()

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
