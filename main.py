import pygame
import sys
import math
from settings import *
from player import Player
from bullet import Bullet
from ui import UI
from events import EventHandler  
from sounds import SoundManager
from enemy import Enemy, Monster2, load_enemy_sprites
from map_manager import MapManager
from camera import Camera

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        load_enemy_sprites()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.map_manager = MapManager()
        self.map_manager.use('level1')  # BÂY GIỜ LOAD ĐƯỢC!
        self.camera = Camera(WIDTH, HEIGHT)
        self.ui = UI(self.screen)
        self.game_state = "MENU"
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.event_handler = EventHandler(self)  
        SoundManager.init_mixer()
        SoundManager.play_menu_music(volume=0.4)
        self.player = None
        self.spawn_timer = 0
        self.shoot_cooldown = 0
        self.boss_spawned = False

    def new_game(self):
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        self.ui.score = 0  # RESET SCORE
        self.boss_spawned = False
        self.spawn_timer = 0
        self.shoot_cooldown = 0
        self.map_manager.items.empty()  # RESET ITEMS
        self.player = Player()
        self.all_sprites.add(self.player)
        self.game_state = "PLAYING"
        SoundManager.stop_music()
        SoundManager.play_background_music(volume=0.5)

    def update(self):
        if self.game_state == "PLAYING":
            if self.ui.is_paused:
                return
            # 1. Update camera trước
            self.camera.update(self.player)
            # Clamp offset để bounded camera, loại bỏ phần dư đen
            map_w = self.map_manager.tile_cols * self.map_manager.tile_size
            map_h = self.map_manager.tile_rows * self.map_manager.tile_size
            self.camera.offset[0] = max(0, min(self.camera.offset[0], map_w - WIDTH))
            self.camera.offset[1] = max(0, min(self.camera.offset[1], map_h - HEIGHT))
            # 2. PLAYER MOVE + COLLISION (X TRƯỚC, Y SAU)
            self.player.input()
            dx = self.player.velocity.x
            dy = self.player.velocity.y
            self.player.rect.centerx += dx
            if self.map_manager.check_environment_collision(self.player.rect, self.camera.offset):
                self.player.rect.centerx -= dx
            self.player.rect.centery += dy
            if self.map_manager.check_environment_collision(self.player.rect, self.camera.offset):
                self.player.rect.centery -= dy
            # Update camera lại sau move
            self.camera.update(self.player)
            # Clamp lại
            self.camera.offset[0] = max(0, min(self.camera.offset[0], map_w - WIDTH))
            self.camera.offset[1] = max(0, min(self.camera.offset[1], map_h - HEIGHT))
            # 3. Update sprites khác (bullets, enemies)
            self.all_sprites.update()
            # 4. SHOOTING
            if pygame.mouse.get_pressed()[0] and self.shoot_cooldown == 0:
                mx, my = pygame.mouse.get_pos()
                angle = math.atan2(my - self.player.rect.centery, mx - self.player.rect.centerx)
                bullet = Bullet(self.player.rect.center, angle)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.shoot_cooldown = 15
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            # 5. SPAWN ENEMY THƯỜNG
            self.spawn_timer += 1
            if self.spawn_timer >= SPAWN_DELAY:
                self.spawn_timer = 0
                enemy = Enemy(self.player)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            # 6. SPAWN BOSS
            if self.ui.score >= 50 and not self.boss_spawned:
                boss = Monster2(self.player)
                self.enemies.add(boss)
                self.all_sprites.add(boss)
                self.boss_spawned = True
            # 7. BULLETS HIT ENEMIES + DROP ITEM
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
            for enemy, bullet_list in hits.items():
                enemy.hp -= len(bullet_list)  # SỬA: nhiều đạn = nhiều dmg
                if enemy.hp <= 0:
                    self.ui.score += enemy.score_value
                    # DROP ITEM WORLD POS
                    world_x = enemy.rect.centerx + self.camera.offset[0]
                    world_y = enemy.rect.centery + self.camera.offset[1]
                    self.map_manager.drop_item(world_x, world_y)
                    enemy.kill()
            # 8. BULLETS HIT MAP (dọn rác + score)
            cleaned = self.map_manager.process_bullets(self.bullets, self.camera.offset)
            self.ui.score += cleaned * 5  # 5 điểm/rác
            # 9. ENEMIES HIT PLAYER
            hits_player = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in hits_player:
                if hasattr(enemy, 'type') and enemy.type == "boss":
                    self.player.health = max(0, self.player.health - 1)  # SỬA: không âm
                    enemy.apply_stun()
                else:
                    self.player.health = max(0, self.player.health - 10)  # SỬA: không âm
                    enemy.kill()
            # 10. ITEMS (update + collect)
            self.map_manager.update_items(self.camera.offset)
            bonuses = self.map_manager.handle_items(self.player.rect)
            self.player.health = min(PLAYER_HP, self.player.health + bonuses["health"])
            # 11. GAME OVER CHECK
            if self.player.health <= 0:
                self.game_state = "GAME_OVER"
                SoundManager.stop_music()
                SoundManager.play_menu_music(volume=0.4)

    def draw(self):
        if self.game_state == "MENU":
            self.ui.draw_menu()
        elif self.game_state == "GAME_OVER":
            self.ui.draw_game_over()
        elif self.game_state == "PLAYING":
            self.screen.fill((139, 69, 19))  # SỬA: fill nâu đất để blend nếu có gap nhỏ
            # MAP + ITEMS
            self.map_manager.draw(self.screen, self.camera)
            self.map_manager.draw_items(self.screen)
            # SPRITES
            self.all_sprites.draw(self.screen)
            self.ui.draw_hud(self.player.health)
            self.ui.draw_ingame_buttons()
            if self.ui.is_paused:
                overlay = pygame.surface.Surface((WIDTH, HEIGHT)).convert_alpha()
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                pause_text = self.ui.font.render("PAUSED", True, (255, 255, 255))
                self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        elif self.game_state == "INSTRUCTIONS": 
            self.ui.draw_instructions()         
        pygame.display.flip()

    def run(self):
        while True:
            self.event_handler.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()