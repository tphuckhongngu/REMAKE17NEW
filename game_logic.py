import pygame
from sounds import SoundManager
from boss import Boss

# Constants (đặt ở đầu để dễ chỉnh)
VICTORY_DELAY_MS = 800          # Thời gian chờ trước khi hiện VICTORY (cho animation)
VICTORY_ALLOWED_WINDOW_MS = VICTORY_DELAY_MS * 5  # Thời gian tối đa kể từ lúc player giết boss


def handle_bullet_enemy_collisions(game):
    """
    Xử lý va chạm đạn ↔ enemy (bao gồm cả skill boost damage cho boss).
    Khi enemy chết → chuyển toàn bộ xử lý cho process_enemy_death.
    """
    try:
        hits = pygame.sprite.groupcollide(game.enemies, game.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            dmg = len(bullets_hit)

            # Boss damage boost từ skill (nếu có)
            try:
                if (enemy.__class__.__name__ == 'Boss' and
                        game.skill_manager and
                        game.skill_manager.is_boss_damage_boosted()):
                    dmg += 1
            except Exception:
                pass

            # Gây damage
            try:
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(dmg)
                else:
                    enemy.hp = getattr(enemy, 'hp', 0) - dmg
            except Exception:
                pass

            # Cập nhật persistent health cho boss
            try:
                if enemy.__class__.__name__ == 'Boss':
                    game.boss_persistent_health = max(0, int(getattr(enemy, 'health', 0)))
            except Exception:
                pass

            # Kiểm tra chết
            died = False
            try:
                if hasattr(enemy, 'health'):
                    died = enemy.health <= 0
                elif hasattr(enemy, 'hp'):
                    died = enemy.hp <= 0
                else:
                    died = not enemy.alive()
            except Exception:
                died = not enemy.alive()

            if died:
                process_enemy_death(game, enemy)  # <-- TOÀN BỘ XỬ LÝ CHẾT Ở ĐÂY

    except Exception:
        pass  # Không để crash game


def maybe_spawn_boss(game):
    """
    Spawn boss theo thời gian hoặc khi score tăng đủ.
    """
    try:
        if game.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        has_boss = any(isinstance(e, Boss) for e in game.enemies)
        boss_interval = getattr(game, 'boss_spawn_interval', 40000)

        # Spawn theo thời gian cố định
        if not has_boss and (now - getattr(game, 'last_boss_time', 0) >= boss_interval):
            game.spawn_boss()
            game.last_boss_time = now

        # Spawn theo score (legacy)
        current_score = getattr(game.ui, 'score', 0)
        if current_score - game.last_boss_score >= 100:
            if not any(isinstance(e, Boss) for e in game.enemies):
                game.spawn_boss()
            game.last_boss_score += 100

    except Exception:
        pass


def process_enemy_death(game, enemy):
    """
    Xử lý tập trung khi enemy chết (dù do đạn hay skill).
    Đây là nơi duy nhất xử lý: +score, kill sprite, persistent health, set flag.
    """
    try:
        is_boss = isinstance(enemy, Boss)
    except Exception:
        is_boss = False

    if is_boss:
        # +1000 điểm (chỉ khi không phải tutorial)
        if not getattr(game, 'tutorial_mode', False):
            try:
                game.ui.score += 1000
                if game.ui.score > game.ui.high_score:
                    game.ui.high_score = game.ui.score
                    game.ui.save_high_score()
            except Exception:
                pass

        # Cập nhật thời gian & persistent health
        game.last_boss_time = pygame.time.get_ticks()
        game.boss_persistent_health = getattr(enemy, 'max_health', 100)

        # tránh spawn boss ngay lập tức do nhảy điểm (+1000)
        try:
            game.last_boss_score = getattr(game.ui, 'score', getattr(game, 'last_boss_score', 0))
        except Exception:
            pass

        # Đánh dấu là player vừa giết boss (rất quan trọng cho victory logic)
        game.boss_just_killed_at = pygame.time.get_ticks()
        # start the victory pending window immediately so post_update_boss_check won't early-return
        try:
            game.victory_pending = True
            game.victory_pending_at = pygame.time.get_ticks()
        except Exception:
            pass
        # mark spawn false (no active boss) — keep victory_pending True to allow VICTORY flow
        game.boss_spawned = False
    else:
        # Enemy thường: +score theo score_value
        if (hasattr(enemy, 'score_value') and
                not getattr(game, 'tutorial_mode', False)):
            try:
                game.ui.score += enemy.score_value
                if game.ui.score > game.ui.high_score:
                    game.ui.high_score = game.ui.score
                    game.ui.save_high_score()
            except Exception:
                pass

    # Kill sprite (common cho cả boss và enemy)
    try:
        enemy.kill()
    except Exception:
        pass


def post_update_boss_check(game):
    """
    Kiểm tra sau mỗi frame: nếu đã spawn boss nhưng không còn boss sống → trigger VICTORY.
    CHỈ THẮNG nếu player thực sự giết boss (có boss_just_killed_at gần đây).
    """
    try:
        # Nếu chưa từng spawn boss hoặc đang pending → bỏ qua
        if not getattr(game, 'boss_spawned', False) and not getattr(game, 'victory_pending', False):
            return

        # Tìm tất cả instance Boss còn sống
        bosses = [e for e in game.enemies if isinstance(e, Boss)]
        bosses.extend([s for s in game.all_sprites if isinstance(s, Boss) and s not in bosses])

        alive_bosses = []
        for b in bosses:
            try:
                if getattr(b, 'health', 0) > 0:
                    alive_bosses.append(b)
            except Exception:
                alive_bosses.append(b)  # an toàn: coi như còn sống nếu không xác định được

        now = pygame.time.get_ticks()

        if alive_bosses:
            # Còn boss sống → hủy pending victory
            game.victory_pending = False
            return

        # Không còn boss sống → kiểm tra nguyên nhân
        delay = getattr(game, 'victory_delay_ms', VICTORY_DELAY_MS)

        if not getattr(game, 'victory_pending', False):
            last_killed = getattr(game, 'boss_just_killed_at', 0)

            if last_killed == 0:
                # Không có bằng chứng player giết → boss tự biến mất (hết thời gian, blink timeout...)
                game.boss_spawned = False
                game.victory_pending = False
                return

            if (now - last_killed) <= VICTORY_ALLOWED_WINDOW_MS:
                # Player thực sự giết boss gần đây → bắt đầu đếm delay
                game.victory_pending = True
                game.victory_pending_at = now
            else:
                # Quá lâu từ lúc giết → coi như boss cũ đã hết hạn
                game.boss_spawned = False
                game.victory_pending = False
            return

        # Đủ thời gian delay → HIỆN VICTORY
        if now - game.victory_pending_at >= delay:
            game.game_state = "VICTORY"
            game.victory_pending = False
            game.boss_spawned = False
            game.victory_entered_at = now

            # Xóa input click thừa tránh click nhầm về menu
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)
            pygame.event.clear(pygame.MOUSEBUTTONUP)

            SoundManager.stop_music()

    except Exception as e:
        pass