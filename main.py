import pygame
import sys
import math
from settings import *
from player import Player
from bullet import Bullet
from enemy import Enemy
from ui import UI
#test commit
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.game_state = "MENU" # MENU, PLAYING, GAME_OVER, INSTRUCTIONS
        # Sprite Groups (Quản lý nhóm đối tượng tối ưu hơn list)
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click trái
                mx, my = event.pos
            
                if self.game_state in ["MENU", "GAME_OVER"]:
                    buttons = self.ui.get_button_rects()
                
                    if buttons['restart'].collidepoint(mx, my):
                        self.new_game()
                    elif buttons['quit'].collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
                    elif 'howto' in buttons and buttons['howto'].collidepoint(mx, my): 
                        self.game_state = "INSTRUCTIONS" 

                elif self.game_state == "INSTRUCTIONS": 
                    self.game_state = "MENU"  # click bất kỳ để back về menu
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_state == "INSTRUCTIONS":
                        self.game_state = "MENU"

    def update(self):
        if self.game_state == "PLAYING":
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

    def draw(self):
        if self.game_state == "MENU":
            self.ui.draw_menu()
        elif self.game_state == "GAME_OVER":
            self.ui.draw_game_over()
        elif self.game_state == "PLAYING":
            self.screen.fill((30, 30, 30))
            self.all_sprites.draw(self.screen)
            self.ui.draw_hud(self.player.health)
        elif self.game_state == "INSTRUCTIONS":  
            self.ui.draw_instructions()         
            
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()