# skills.py - SKILL 3 MỚI: BẤT TỬ THẦN - INVINCIBILITY 8 GIÂY

import pygame
import os
import math
from settings import WIDTH, HEIGHT, FPS
from sounds import SoundManager
from game_logic import process_enemy_death

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(str(msg).encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            try:
                import sys
                enc = sys.stdout.encoding or 'utf-8'
                out = str(msg).encode(enc, errors='replace').decode(enc)
                sys.stdout.write(out + "\n")
            except Exception:
                pass

def load_skill_img(filename):
    try:
        path = os.path.join(SKILLS_DIR, filename)
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        safe_print(f"[WARNING] Không load được {filename}: {e}")
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        colors = {1: (0, 200, 0), 2: (200, 100, 0), 3: (100, 100, 255), 4: (255, 200, 0)}
        try:
            num = int(filename.replace("skill", "").split(".")[0].split("_")[0])
        except:
            num = 1
        surf.fill(colors.get(num, (100, 100, 100)))
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
        font = pygame.font.SysFont("arial", 36, bold=True)
        text = font.render(str(num), True, (255, 255, 255))
        surf.blit(text, text.get_rect(center=surf.get_rect().center))
        return surf
    return surf


def load_sequence_frames(folder_name='vuno'):
    """Load ordered image frames from a folder inside `skills`.

    Looks for `skills/<folder_name>/` and loads all image files sorted
    numerically when filenames start with digits, otherwise lexicographically.
    Returns an empty list if nothing is found.
    """
    frames = []
    folder = os.path.join(SKILLS_DIR, folder_name)
    if not os.path.isdir(folder):
        return frames
    try:
        import re
        files = os.listdir(folder)
        def _sort_key(name):
            m = re.match(r'^(\d+)', name)
            if m:
                return (0, int(m.group(1)), name)
            return (1, name.lower())
        files = sorted(files, key=_sort_key)
        for fn in files:
            if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                try:
                    surf = pygame.image.load(os.path.join(folder, fn)).convert_alpha()
                    frames.append(surf)
                except Exception:
                    continue
        safe_print(f"[load_sequence_frames] loaded {len(frames)} frames from {folder}")
    except Exception as e:
        safe_print(f"[load_sequence_frames] error scanning {folder}: {e}")
    return frames

SKILL_ICON_SIZE = 400

class InvincibilityEffect(pygame.sprite.Sprite):
    """Hiệu ứng bất tử: hào quang vàng + nhấp nháy"""
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.life = 8 * FPS  # 8 giây
        self.flash_timer = 0

        # Tạo surface lớn để vẽ hào quang
        size = 200
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=player.rect.center)

    def update(self):
        self.life -= 1
        if self.life <= 0:
            # Hết bất tử
            try:
                self.player.invincible = False
            except:
                pass
            self.kill()
            return

        self.rect.center = self.player.rect.center
        self.image.fill((0, 0, 0, 0))

        # Hào quang vàng lan tỏa
        alpha = 150 + int(50 * math.sin(pygame.time.get_ticks() / 100))
        for r in range(60, 100, 10):
            pygame.draw.circle(self.image, (255, 220, 50, alpha // 2), 
                             (100, 100), r, 15)

        # Vòng sáng vàng
        pygame.draw.circle(self.image, (255, 255, 0, alpha), (100, 100), 80, 10)


class Explosion(pygame.sprite.Sprite):
    """Plays a short explosion animation from a list of frames.

    Optionally accepts an `on_finished` callback and a `pending_enemies` list.
    The callback will be invoked with the pending_enemies when the animation
    completes (or the fallback life expires).
    """
    def __init__(self, pos, frames, frame_rate=4, on_finished=None, pending_enemies=None):
        super().__init__()
        self.frames = frames or []
        self.frame_rate = max(1, int(frame_rate))
        self.index = 0
        self.counter = 0
        self._on_finished = on_finished
        # shallow copy to avoid mutation by caller
        self.pending_enemies = list(pending_enemies) if pending_enemies else []
        # If frames present, scale them so the animation covers the screen
        if self.frames:
            scaled = []
            try:
                for f in self.frames:
                    try:
                        w, h = f.get_width(), f.get_height()
                        scale_ratio = max(WIDTH / max(1, w), HEIGHT / max(1, h))
                        new_size = (max(int(w * scale_ratio), WIDTH), max(int(h * scale_ratio), HEIGHT))
                        sf = pygame.transform.smoothscale(f, new_size)
                        scaled.append(sf)
                    except Exception:
                        scaled.append(f)
            except Exception:
                scaled = list(self.frames)
            self.frames = scaled
            self.image = self.frames[0]
            self.rect = self.image.get_rect(center=pos)
        else:
            # simple fallback circle
            self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 160, 0), (WIDTH//2, HEIGHT//2), min(WIDTH, HEIGHT)//4)
            self.rect = self.image.get_rect(center=pos)
            # longer visible lifetime for fallback
            self.life = max(30, int(self.frame_rate * 30))

    def _finish(self):
        # Invoke callback before killing sprite
        try:
            if callable(self._on_finished):
                try:
                    self._on_finished(self.pending_enemies)
                except Exception:
                    pass
        except Exception:
            pass

    def update(self):
        # If there are no frames available, show the fallback image for a short time
        if not self.frames:
            try:
                self.life -= 1
            except AttributeError:
                self.life = max(6, int(self.frame_rate * 6))
                self.life -= 1
            if self.life <= 0:
                try:
                    self._finish()
                except Exception:
                    pass
                self.kill()
            return

        # advance frame based on frame_rate
        self.counter += 1
        if self.counter < self.frame_rate:
            return
        self.counter = 0
        self.index += 1
        if self.index >= len(self.frames):
            try:
                self._finish()
            except Exception:
                pass
            self.kill()
            return
        # keep center stable between frames
        center = self.rect.center
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)

class SkillManager:
    def __init__(self, game, player, all_sprites, enemies):
        # keep reference to game so skills can trigger game-level effects (scores, boss death handling)
        self.game = game
        self.player = player
        self.all_sprites = all_sprites
        self.enemies = enemies

        self.barrage_bullets = pygame.sprite.Group()
        # preload explosion frames for Skill 4 from folder 'vuno'
        try:
            self.explosion_frames = load_sequence_frames('vuno')
        except Exception:
            self.explosion_frames = []

        def load_square_icon(filename):
            original = load_skill_img(filename)
            square = pygame.Surface((SKILL_ICON_SIZE, SKILL_ICON_SIZE), pygame.SRCALPHA)
            scale_ratio = SKILL_ICON_SIZE / max(original.get_width(), original.get_height())
            new_size = (int(original.get_width() * scale_ratio), int(original.get_height() * scale_ratio))
            scaled = pygame.transform.smoothscale(original, new_size)
            offset_x = (SKILL_ICON_SIZE - scaled.get_width()) // 2
            offset_y = (SKILL_ICON_SIZE - scaled.get_height()) // 2
            square.blit(scaled, (offset_x, offset_y))
            return square

        self.icons = {
            1: load_square_icon("skill1.png"),
            2: load_square_icon("skill2.png"),
            3: load_square_icon("skill3.png"),
            4: load_square_icon("skill4.png"),
        }
        self.cooldown_icons = {
            1: load_square_icon("skill1_1.png"),
            2: load_square_icon("skill2_1.png"),
            3: load_square_icon("skill3_1.png"),
            4: load_square_icon("skill4_1.png"),
        }

        self.cooldown_end = {1: 0, 2: 0, 3: 0, 4: 0}
        self.cooldown_duration = {1: 15000, 2: 20000, 3: 30000, 4: 25000}  # skill 3 cooldown 30s
        self.skill2_boost_end = 0
        self.effects = pygame.sprite.Group()
        self.all_sprites.add(self.effects)

    def update(self):
        now = pygame.time.get_ticks()
        self.effects.update()
        self.barrage_bullets.update()
        if now > self.skill2_boost_end:
            self.skill2_boost_end = 0

    def draw_icons(self, screen):
        ICON_SIZE = SKILL_ICON_SIZE
        font = pygame.font.SysFont("arial", 42, bold=True)
        now = pygame.time.get_ticks()

        # Vị trí cố định cho từng skill (x, y)
        positions = {
            1: (100, HEIGHT - 300),
            2: (250, HEIGHT - 300),
            3: (400, HEIGHT - 300),
            4: (550, HEIGHT - 300),
        }
        for i in range(1, 5):
            x, y = positions[i]

            # Đang cooldown → dùng icon cooldown, hết cooldown → dùng icon thường
            if now < self.cooldown_end.get(i, 0):
                screen.blit(self.cooldown_icons.get(i, self.icons[i]), (x, y))
            else:
                screen.blit(self.icons[i], (x, y))

        

    def handle_input(self):
        # Polling keys here can interact poorly with IME; keep defensive.
        try:
            keys = pygame.key.get_pressed()
            now = pygame.time.get_ticks()
            if keys[pygame.K_1] and now > self.cooldown_end.get(1, 0):
                try:
                    self.activate_skill_1()
                except Exception as e:
                    safe_print('[Skill] activate_skill_1 error: ' + str(e))
                self.cooldown_end[1] = now + self.cooldown_duration.get(1, 0)
            if keys[pygame.K_2] and now > self.cooldown_end.get(2, 0):
                try:
                    self.activate_skill_2(now)
                except Exception as e:
                    safe_print('[Skill] activate_skill_2 error: ' + str(e))
                self.cooldown_end[2] = now + self.cooldown_duration.get(2, 0)
            if keys[pygame.K_3] and now > self.cooldown_end.get(3, 0):
                try:
                    self.activate_skill_3()
                except Exception as e:
                    safe_print('[Skill] activate_skill_3 error: ' + str(e))
                self.cooldown_end[3] = now + self.cooldown_duration.get(3, 0)
            if keys[pygame.K_4] and now > self.cooldown_end.get(4, 0):
                try:
                    self.activate_skill_4()
                except Exception as e:
                    safe_print('[Skill] activate_skill_4 error: ' + str(e))
                self.cooldown_end[4] = now + self.cooldown_duration.get(4, 0)
        except Exception as e:
            safe_print('[Skill] handle_input exception: ' + str(e))

    def activate_skill_1(self):
        safe_print("[Skill 1] Hoi mau +30")
        try:
            # Apply heal first (don't rely on sound)
            try:
                if self.player is not None and hasattr(self.player, 'health'):
                    self.player.health = min(100, self.player.health + 30)
            except Exception as e:
                safe_print('[Skill 1] health update error: ' + str(e))
            try:
                SoundManager.play_heal_sound()
            except Exception as e:
                safe_print('[Skill 1] sound error: ' + str(e))
        except Exception as e:
            safe_print('[Skill 1] unexpected error: ' + str(e))

    def activate_skill_2(self, now):
        safe_print("[Skill 2] Boost damage boss +5 for 10s")
        try:
            try:
                SoundManager.play_powerup_sound()
            except Exception as e:
                safe_print('[Skill 2] sound error: ' + str(e))
            self.skill2_boost_end = now + 10000
        except Exception as e:
            safe_print('[Skill 2] unexpected error: ' + str(e))

    def activate_skill_3(self):
        safe_print('[Skill 3] INVINCIBILITY 8s')
        SoundManager.play_magic_sound()
        # Set invincible flag safely
        try:
            if self.player is None:
                safe_print('[Skill 3] no player')
                return
            self.player.invincible = True
        except Exception:
            setattr(self.player, 'invincible', True)
        # Add visual effect

        effect = InvincibilityEffect(self.player)
        self.effects.add(effect)
        self.all_sprites.add(effect)
    def activate_skill_4(self):
            SoundManager.play_barrage_sound()
        # Explosion position: try player center, otherwise center of screen
        try:
            pos = self.player.rect.center
        except Exception:
            pos = (WIDTH // 2, HEIGHT // 2)

        # spawn explosion animation

        # gather enemies now but delay destruction until explosion finishes
        enemies_copy = list(self.enemies)

        def _on_explosion_finished(pending_list):
            try:
                for en in list(pending_list):
                    try:
                        process_enemy_death(self.game, en)
                    except Exception:
                        try:
                            en.kill()
                        except Exception:
                            pass
            except Exception:
                pass

        frames = getattr(self, 'explosion_frames', []) or []
        expl = Explosion(pos, frames, frame_rate=6,
                            on_finished=_on_explosion_finished,
                            pending_enemies=enemies_copy)
        try:
            self.all_sprites.add(expl)
        except Exception:
            pass


    def is_boss_damage_boosted(self):
        return pygame.time.get_ticks() < self.skill2_boost_end

    def check_magic_ball_hits(self):
        pass

    def check_barrage_hits(self):
        hits = pygame.sprite.groupcollide(self.barrage_bullets, self.enemies, True, False)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                # spawn explosion effect at bullet position (fallback to enemy center)
                try:
                    pos = None
                    try:
                        pos = bullet.rect.center
                    except Exception:
                        pos = None
                    if pos is None and hasattr(enemy, 'rect'):
                        pos = enemy.rect.center
                    if pos is not None:
                        if getattr(self, 'explosion_frames', None):
                            expl = Explosion(pos, self.explosion_frames, frame_rate=4)
                        else:
                            expl = Explosion(pos, [], frame_rate=4)
                        try:
                            self.all_sprites.add(expl)
                        except Exception:
                            pass
                except Exception:
                    pass
                if hasattr(enemy, 'take_damage'):
                    damage = 15 if enemy.__class__.__name__ == 'Boss' else 30
                    enemy.take_damage(damage)
                    # if this kill path killed the enemy directly, ensure centralized death processing
                    try:
                        died = False
                        if hasattr(enemy, 'health'):
                            died = enemy.health <= 0
                        elif hasattr(enemy, 'hp'):
                            died = enemy.hp <= 0
                        else:
                            died = not enemy.alive()
                        if died:
                            process_enemy_death(self.game, enemy)
                    except Exception:
                        pass