# main.py
import pygame
import sys
from settings import *
from player import Player
# from bullet import Bullet   # main không tạo bullet trực tiếp nữa
from ui import UI
from events import EventHandler
from sounds import SoundManager
from enemy import Enemy, Monster2, load_enemy_sprites
from map_manager import MapManager
from camera import Camera
import math

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # load assets cần thiết
        load_enemy_sprites()  # nếu hàm này tồn tại
        SoundManager.init_mixer()
        SoundManager.play_menu_music(volume=0.4)

        # hệ thống map, camera, UI
        self.map_manager = MapManager()
        self.map_manager.use('level1')  # đổi tên level nếu cần
        self.camera = Camera(WIDTH, HEIGHT)
        self.ui = UI(self.screen)

        # trạng thái game
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER, INSTRUCTIONS

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # event handler (nếu bạn có class này)
        self.event_handler = EventHandler(self)

        # player và các timer
        self.player = None
        self.spawn_timer = 0
        # shoot_cooldown không dùng nữa (Player quản lý fire rate)
        # self.shoot_cooldown = 0

        # boss / score
        self.boss_spawned = False
        self.last_boss_score = 0

    def new_game(self):
        # reset toàn bộ
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()

        # tạo player, truyền group đạn để Player spawn bullet vào
        self.player = Player(bullet_group=self.bullets)
        self.all_sprites.add(self.player)

        # đổi state + âm thanh
        self.game_state = "PLAYING"
        SoundManager.stop_music()
        SoundManager.play_background_music(volume=0.5)

        # reset UI / score nếu cần (tùy implement UI)
        if hasattr(self.ui, "reset"):
            try:
                self.ui.reset()
            except Exception:
                pass
        self.spawn_timer = 0
        self.last_boss_score = 0

    def update(self):
        if self.game_state != "PLAYING":
            return

        if self.ui.is_paused:
            return

        # 1) update sprites (player, enemies) và bullets riêng
        self.all_sprites.update()
        self.bullets.update()            # <<< quan trọng: đảm bảo Bullet.update() chạy
        # Nếu camera cần apply cho sprites, làm ở draw hoặc trong group riêng

        # 2) camera update (theo player)
        if self.player is not None:
            self.camera.update(self.player)

        # 3) xử lý bắn: gọi Player.shoot() khi chuột nhấn
        # player quản lý ammo / reload / fire rate
        if self.player is not None and pygame.mouse.get_pressed()[0]:
            self.player.shoot()

        # 4) spawn quái (điều chỉnh SPAWN_DELAY trong settings)
        self.spawn_timer += 1
        if self.spawn_timer >= SPAWN_DELAY:
            self.spawn_timer = 0
            try:
                enemy = Enemy(self.player)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            except Exception:
                # nếu Enemy khởi tạo khác, thay đổi ở đây
                pass

        # 5) spawn boss theo điểm (nếu UI giữ score)
        try:
            if self.ui.score - self.last_boss_score >= 100:
                boss = Monster2(self.player)
                self.enemies.add(boss)
                self.all_sprites.add(boss)
                self.last_boss_score += 50
        except Exception:
            pass

        # 6) va chạm đạn - quái
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            # bullets_hit là list viên đạn trúng; trừ máu theo số viên
            dmg = len(bullets_hit)
            try:
                enemy.hp -= dmg
            except Exception:
                # nếu enemy có method take_damage, gọi thay
                if hasattr(enemy, "take_damage"):
                    enemy.take_damage(dmg)
                else:
                    enemy.hp = getattr(enemy, "hp", 0) - dmg

            if getattr(enemy, "hp", 1) <= 0:
                # cộng điểm nếu enemy có score_value
                if hasattr(enemy, "score_value"):
                    try:
                        self.ui.score += enemy.score_value
                    except Exception:
                        pass
                enemy.kill()

        # 7) va chạm quái - player
        if self.player is not None:
            hits_player = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in hits_player:
                if hasattr(enemy, 'type') and enemy.type == "boss":
                    self.player.health -= 20
                    enemy.kill()
                else:
                    self.player.health -= 10
                    enemy.kill()

        # 8) kiểm tra game over
        if self.player is not None and self.player.health <= 0:
            self.game_state = "GAME_OVER"
            SoundManager.stop_music()
            # có thể play game over sound

    def draw(self):
        # phân nhánh vẽ cho từng trạng thái
        if self.game_state == "MENU":
            self.ui.draw_menu()
        elif self.game_state == "GAME_OVER":
            self.ui.draw_game_over()
        elif self.game_state == "PLAYING":
            # clear
            self.screen.fill((30, 30, 30))

            # 1) draw map
            self.map_manager.draw(self.screen, self.camera)

            # 2) draw bullets (trước player để tạo layering mong muốn)
            self.bullets.draw(self.screen)

            # 3) draw all_sprites (player + enemies)
            self.all_sprites.draw(self.screen)

            # 4) UI: HP, buttons...
            # ui.draw_hud nhận health (theo implement của bạn)
            try:
                self.ui.draw_hud(self.player.health)
            except Exception:
                try:
                    self.ui.draw_hud()
                except Exception:
                    pass

            self.ui.draw_ingame_buttons()

            # 5) ammo HUD (player)
            if self.player is not None:
                self.player.draw_ammo(self.screen)

            # pause overlay
            if self.ui.is_paused:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                pause_text = self.ui.font.render("PAUSED", True, (255, 255, 255))
                self.screen.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

        elif self.game_state == "INSTRUCTIONS":
            self.ui.draw_instructions()

        # flip màn hình
        pygame.display.flip()

    def run(self):
        # vòng lặp chính: dùng EventHandler nếu bạn có (nó nên quản lý input)
        while True:
            # nếu bạn dùng EventHandler để xử lý key/menu, gọi nó
            try:
                self.event_handler.handle_events()
            except Exception:
                # fallback: xử lý event đơn giản (ESC để thoát, phím N để new game)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_n:
                            self.new_game()

            # update + draw
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    g = Game()
    # Start a new game immediately for quick testing (bạn có thể thay đổi)
    g.new_game()
    g.run()
