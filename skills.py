# skills.py - SKILL 3 MỚI: BẤT TỬ THẦN - INVINCIBILITY 8 GIÂY

import pygame
import os
import math
from settings import WIDTH, HEIGHT, FPS
from sounds import SoundManager
from game_logic import process_enemy_death

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")

def load_skill_img(filename):
    try:
        path = os.path.join(SKILLS_DIR, filename)
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[WARNING] Không load được {filename}: {e}")
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

class SkillManager:
    def __init__(self, game, player, all_sprites, enemies):
        # keep reference to game so skills can trigger game-level effects (scores, boss death handling)
        self.game = game
        self.player = player
        self.all_sprites = all_sprites
        self.enemies = enemies

        self.barrage_bullets = pygame.sprite.Group()

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
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        if keys[pygame.K_1] and now > self.cooldown_end[1]:
            self.activate_skill_1()
            self.cooldown_end[1] = now + self.cooldown_duration[1]
        if keys[pygame.K_2] and now > self.cooldown_end[2]:
            self.activate_skill_2(now)
            self.cooldown_end[2] = now + self.cooldown_duration[2]
        if keys[pygame.K_3] and now > self.cooldown_end[3]:
            self.activate_skill_3()
            self.cooldown_end[3] = now + self.cooldown_duration[3]
        if keys[pygame.K_4] and now > self.cooldown_end[4]:
            self.activate_skill_4()
            self.cooldown_end[4] = now + self.cooldown_duration[4]

    def activate_skill_1(self):
        print("[Skill 1] Hồi máu +30")
        try:
            SoundManager.play_heal_sound()
            self.player.health = min(100, self.player.health + 30)
        except Exception as e:
            print("[Skill 1] LỖI:", str(e))

    def activate_skill_2(self, now):
        print("[Skill 2] Boost damage boss +5 trong 10 giây")
        try:
            SoundManager.play_powerup_sound()
            self.skill2_boost_end = now + 10000
        except Exception as e:
            print("[Skill 2] LỖI:", str(e))

    def activate_skill_3(self):
        print("[Skill 3] BẤT TỬ THẦN - INVINCIBILITY 8 GIÂY!")
        try:
            SoundManager.play_magic_sound()  # hoặc powerup sound

            # Bật bất tử cho player
            try:
                self.player.invincible = True
            except:
                setattr(self.player, 'invincible', True)

            # Hiệu ứng hào quang vàng
            effect = InvincibilityEffect(self.player)
            self.effects.add(effect)
            self.all_sprites.add(effect)
        except Exception as e:
            print("[Skill 3] LỖI:", str(e))

    def activate_skill_4(self):
        print("[Skill 4] Bullet Barrage!")
        try:
            SoundManager.play_barrage_sound()
            class BarrageBullet(pygame.sprite.Sprite):
                def __init__(self, pos, vel):
                    super().__init__()
                    length = 50
                    width = 12
                    self.original_image = pygame.Surface((length, width), pygame.SRCALPHA)
                    pygame.draw.rect(self.original_image, (255, 255, 255), (0, 0, length, width))
                    pygame.draw.rect(self.original_image, (0, 255, 255), (0, 0, length, width), 4)
                    angle = math.degrees(math.atan2(-vel.y, vel.x))
                    self.image = pygame.transform.rotate(self.original_image, angle)
                    self.rect = self.image.get_rect(center=pos)
                    self.vel = vel
                    self.pos = pygame.Vector2(pos)
                def update(self):
                    self.pos += self.vel
                    self.rect.center = (int(self.pos.x), int(self.pos.y))
                    if not pygame.Rect(-2000, -2000, WIDTH + 4000, HEIGHT + 4000).colliderect(self.rect):
                        self.kill()

            for i in range(8):
                angle = math.radians(i * 45)
                vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * 14
                bullet = BarrageBullet(self.player.rect.center, vel)
                self.barrage_bullets.add(bullet)
                self.all_sprites.add(bullet)

        except Exception as e:
            print("[Skill 4] LỖI:", str(e))

    def is_boss_damage_boosted(self):
        return pygame.time.get_ticks() < self.skill2_boost_end

    def check_magic_ball_hits(self):
        pass

    def check_barrage_hits(self):
        hits = pygame.sprite.groupcollide(self.barrage_bullets, self.enemies, True, False)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
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