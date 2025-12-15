import pygame
import sys
import math
from settings import *
from player import Player
from bullet import Bullet
from enemy import Enemy
from ui import UI
from events import EventHandler  
from sounds import SoundManager
from enemy import load_enemy_sprites 
#test commit
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        load_enemy_sprites() # Gọi hàm tải ảnh
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.game_state = "MENU" # MENU, PLAYING, GAME_OVER, INSTRUCTIONS
        # Sprite Groups (Quản lý nhóm đối tượng tối ưu hơn list)
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.event_handler = EventHandler(self)  
        SoundManager.init_mixer()  # Khởi tạo âm thanh
        SoundManager.play_menu_music(volume=0.4) #phát nhạc ngay khi mở ứng dụng
        self.player = None
        self.spawn_timer = 0
        self.shoot_cooldown = 0

    def new_game(self):
        # Reset lại game
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.game_state = "PLAYING"
        SoundManager.stop_music()                   # Dừng nhạc menu cũ
        SoundManager.play_background_music(volume=0.5)  # Phát nhạc chơi game

    def update(self):
        if self.game_state == "PLAYING":
            if self.ui.is_paused:
                return
            # 1. Update sprites
            self.all_sprites.update()
            
            # 2. Player Shooting logic (Đưa về main hoặc để trong Player tùy ý, để đây dễ quản lý đạn hơn)
            if pygame.mouse.get_pressed()[0] and self.shoot_cooldown == 0:
                mx, my = pygame.mouse.get_pos()
                # Tính góc bắn
                angle = math.atan2(my - self.player.rect.centery, mx - self.player.rect.centerx)
                bullet = Bullet(self.player.rect.center, angle)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.shoot_cooldown = 15
            if self.shoot_cooldown > 0: self.shoot_cooldown -= 1

            # 3. Enemy Spawner
            self.spawn_timer += 1
            if self.spawn_timer >= SPAWN_DELAY:
                self.spawn_timer = 0
                enemy = Enemy(self.player)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

            # 4. Collision Detection (Va chạm)
            # Đạn trúng quái
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            
            # Quái chạm người
            hits_player = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if hits_player:
                self.player.health -= 10
                if self.player.health <= 0:
                    self.game_state = "GAME_OVER"
                    SoundManager.fadeout_background_music(1000)
                    SoundManager.play_menu_music(volume=0.4)

    def draw(self):
        if self.game_state == "MENU":
            self.ui.draw_menu()
        elif self.game_state == "GAME_OVER":
            self.ui.draw_game_over()
        elif self.game_state == "PLAYING":
            self.screen.fill((30, 30, 30))
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