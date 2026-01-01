import pygame
from sounds import SoundManager
from boss import Boss


def handle_bullet_enemy_collisions(game):
    """Handle bullet vs enemy collisions and boss death/victory triggers."""
    try:
        hits = pygame.sprite.groupcollide(game.enemies, game.bullets, False, True)
        for enemy, bullets_hit in hits.items():
            dmg = len(bullets_hit)
            # boss damage boost support
            try:
                if enemy.__class__.__name__ == 'Boss' and game.skill_manager and game.skill_manager.is_boss_damage_boosted():
                    dmg += 5
            except Exception:
                pass

            try:
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(dmg)
                else:
                    enemy.hp = getattr(enemy, 'hp', 0) - dmg
            except Exception:
                try:
                    enemy.hp = getattr(enemy, 'hp', 0) - dmg
                except Exception:
                    pass

            # persist boss health
            try:
                if enemy.__class__.__name__ == 'Boss':
                    game.boss_persistent_health = max(0, int(getattr(enemy, 'health', 0)))
            except Exception:
                pass

            # determine death
            try:
                died = False
                if hasattr(enemy, 'health'):
                    died = getattr(enemy, 'health', 0) <= 0
                elif hasattr(enemy, 'hp'):
                    died = getattr(enemy, 'hp', 0) <= 0
                else:
                    died = not enemy.alive()
            except Exception:
                died = not enemy.alive()

            if died:
                # delegate handling to shared helper so other systems (skills) can reuse
                try:
                    process_enemy_death(game, enemy)
                except Exception:
                    # fallback to previous behavior if helper fails
                    try:
                        if enemy.__class__.__name__ == 'Boss':
                            try:
                                if not getattr(game, 'tutorial_mode', False):
                                    game.ui.score += 1000
                                    if game.ui.score > game.ui.high_score:
                                        game.ui.high_score = game.ui.score
                                        game.ui.save_high_score()
                            except Exception:
                                pass
                            try:
                                game.last_boss_time = pygame.time.get_ticks()
                            except Exception:
                                pass
                            try:
                                game.boss_persistent_health = getattr(enemy, 'max_health', 100)
                            except Exception:
                                game.boss_persistent_health = 100
                            try:
                                enemy.kill()
                            except Exception:
                                pass
                            try:
                                rem = sum(1 for e in game.enemies if e.__class__.__name__ == 'Boss')
                            except Exception:
                                rem = 0
                            try:
                                print(f"DEBUG: boss died handling — remaining Boss count = {rem}")
                            except Exception:
                                pass
                            try:
                                print(f"DEBUG: Boss.take_damage -> killed boss: enemy={enemy.__class__.__name__} id={id(enemy)} health={getattr(enemy,'health',None)}")
                            except Exception:
                                pass
                            try:
                                game.boss_spawned = False
                                game.boss_just_killed_at = pygame.time.get_ticks()
                            except Exception:
                                pass
                        else:
                            try:
                                if hasattr(enemy, 'score_value') and not getattr(game, 'tutorial_mode', False):
                                    game.ui.score += enemy.score_value
                                    if game.ui.score > game.ui.high_score:
                                        game.ui.high_score = game.ui.score
                                        game.ui.save_high_score()
                            except Exception:
                                pass
                            try:
                                enemy.kill()
                            except Exception:
                                pass
                    except Exception:
                        pass
    except Exception:
        # swallow to avoid update crash
        pass


def maybe_spawn_boss(game):
    """Handle periodic and score-based boss spawn logic."""
    try:
        if game.game_state != "PLAYING":
            return
        now = pygame.time.get_ticks()
        has_boss = any([e.__class__.__name__ == 'Boss' for e in game.enemies])
        boss_interval = getattr(game, 'boss_spawn_interval', 40000)
        if not has_boss and now - getattr(game, 'last_boss_time', 0) >= boss_interval:
            game.spawn_boss()
            game.last_boss_time = now
            has_boss = True

        # legacy score-based spawn
        if getattr(game.ui, 'score', 0) - game.last_boss_score >= 100:
            has_boss = any([e.__class__.__name__ == 'Boss' for e in game.enemies])
            if not has_boss:
                game.spawn_boss()
            game.last_boss_score += 150
    except Exception:
        pass


def process_enemy_death(game, enemy):
    """Centralize handling when an enemy dies (boss or normal).

    This allows damage from non-bullet sources (skills) to trigger the same
    score, persistence and victory scheduling logic as bullet collisions.
    """
    try:
        # Determine type
        is_boss = enemy.__class__.__name__ == 'Boss'
    except Exception:
        is_boss = False

    if is_boss:
        try:
            if not getattr(game, 'tutorial_mode', False):
                try:
                    game.ui.score += 1000
                    if game.ui.score > game.ui.high_score:
                        game.ui.high_score = game.ui.score
                        game.ui.save_high_score()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            game.last_boss_time = pygame.time.get_ticks()
        except Exception:
            pass
        try:
            game.boss_persistent_health = getattr(enemy, 'max_health', 100)
        except Exception:
            game.boss_persistent_health = 100
        try:
            enemy.kill()
        except Exception:
            pass
        try:
            rem = sum(1 for e in game.enemies if e.__class__.__name__ == 'Boss')
        except Exception:
            rem = 0
        try:
            print(f"DEBUG: boss died handling — remaining Boss count = {rem}")
        except Exception:
            pass

        try:
            boss_list = []
            for s in list(game.all_sprites):
                cname = getattr(s.__class__, '__name__', type(s).__name__)
                t = getattr(s, 'type', '') or ''
                name = getattr(s, 'name', '') or ''
                if 'boss' in cname.lower() or 'boss' in str(t).lower() or 'boss' in str(name).lower():
                    boss_list.append((cname, id(s), getattr(s, 'health', None), t, name))
            print(f"DEBUG: boss-like sprites after kill: {boss_list}")
        except Exception:
            pass

        try:
            print(f"DEBUG: Boss.take_damage -> killed boss: enemy={enemy.__class__.__name__} id={id(enemy)} health={getattr(enemy,'health',None)}")
        except Exception:
            try:
                print("DEBUG: Boss.take_damage -> killed boss")
            except Exception:
                pass
        try:
            game.boss_spawned = False
            game.boss_just_killed_at = pygame.time.get_ticks()
        except Exception:
            try:
                game.boss_spawned = False
                game.boss_just_killed_at = 0
            except Exception:
                pass
    else:
        try:
            if hasattr(enemy, 'score_value') and not getattr(game, 'tutorial_mode', False):
                try:
                    game.ui.score += enemy.score_value
                    if game.ui.score > game.ui.high_score:
                        game.ui.high_score = game.ui.score
                        game.ui.save_high_score()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            enemy.kill()
        except Exception:
            pass


def post_update_boss_check(game):
    """Fallback: if we expected a boss but none remain with >0 health, schedule/trigger victory.

    Uses a short pending window (game.victory_delay_ms) so visuals/animations have time to finish.
    """
    try:
        if not getattr(game, 'boss_spawned', False) and not getattr(game, 'victory_pending', False):
            return

        # Find any Boss instances in enemies or all_sprites
        bosses = []
        try:
            bosses.extend([e for e in game.enemies if isinstance(e, Boss)])
        except Exception:
            pass
        try:
            bosses.extend([e for e in game.all_sprites if isinstance(e, Boss)])
        except Exception:
            pass

        # Deduplicate in case the same boss is present in multiple sprite groups
        try:
            seen = set()
            unique = []
            for b in bosses:
                if id(b) not in seen:
                    seen.add(id(b))
                    unique.append(b)
            bosses = unique
        except Exception:
            pass

        # Filter to bosses that are alive (health > 0) or conservatively assume alive
        alive_bosses = []
        for b in bosses:
            try:
                h = getattr(b, 'health', None)
                if h is None:
                    alive_bosses.append(b)
                else:
                    if h > 0:
                        alive_bosses.append(b)
            except Exception:
                alive_bosses.append(b)

        now = pygame.time.get_ticks()

        if alive_bosses:
            # there is at least one boss still alive; cancel any pending victory
            try:
                details = []
                for b in alive_bosses:
                    try:
                        details.append((b.__class__.__name__, id(b), getattr(b, 'health', None), getattr(b, 'type', None)))
                    except Exception:
                        details.append((type(b).__name__, id(b), None, None))
                print(f"DEBUG: post_update_boss_check - bosses present (alive): {len(alive_bosses)}; skipping VICTORY - {details}")
            except Exception:
                pass
            # cancel pending victory if any (safety)
            try:
                game.victory_pending = False
            except Exception:
                pass
            return

        # Extra safeguard: ensure no other ENEMY instances with type 'boss' remain (e.g., Monster2)
        try:
            suspicious = []
            for s in list(game.enemies):
                try:
                    # if an enemy has type == 'boss' but is not an instance of Boss, consider it suspicious
                    if not isinstance(s, Boss) and getattr(s, 'type', '') == 'boss':
                        suspicious.append((s.__class__.__name__, id(s), getattr(s, 'health', None), getattr(s, 'type', None), getattr(s, 'name', None)))
                except Exception:
                    pass
            if suspicious:
                try:
                    print(f"DEBUG: post_update_boss_check - found suspicious boss-like enemies: {suspicious}; skipping VICTORY")
                except Exception:
                    pass
                try:
                    game.victory_pending = False
                except Exception:
                    pass
                return
        except Exception:
            pass

        # No alive bosses found: either start the pending timer or finalize if enough time passed
        try:
            # ensure we have a default delay
            delay = getattr(game, 'victory_delay_ms', 300)
            if not getattr(game, 'victory_pending', False):
                # start pending window only if the boss was recently killed by the player
                try:
                    last_killed = getattr(game, 'boss_just_killed_at', 0)
                    # allow some leeway: consider recent kills within a few multiples of the delay
                    allowed_window = getattr(game, 'victory_delay_ms', 800) * 5
                    if last_killed and (now - last_killed) <= allowed_window:
                        try:
                            game.victory_pending = True
                            game.victory_pending_at = now
                        except Exception:
                            game.victory_pending = True
                            game.victory_pending_at = now
                        try:
                            print("DEBUG: No Boss instances remain after player kill - scheduling VICTORY (pending)")
                        except Exception:
                            pass
                    else:
                        # likely the boss expired naturally (blink timeout) — do not grant victory
                        try:
                            print("DEBUG: No Boss instances remain but no recent player kill detected; clearing boss state and skipping VICTORY (likely expired)")
                        except Exception:
                            pass
                        try:
                            game.boss_spawned = False
                            game.victory_pending = False
                        except Exception:
                            pass
                except Exception:
                    # fallback: schedule pending if we cannot determine cause
                    try:
                        game.victory_pending = True
                        game.victory_pending_at = now
                    except Exception:
                        game.victory_pending = True
                        game.victory_pending_at = now
                    try:
                        print("DEBUG: No Boss instances remain - scheduling VICTORY (pending) [fallback]")
                    except Exception:
                        pass
                return

            # finalize victory if the pending window elapsed
            if now - getattr(game, 'victory_pending_at', 0) >= delay:
                try:
                    print("DEBUG: No Boss instances remain (post-update check) - triggering VICTORY state")
                except Exception:
                    pass
                game.boss_spawned = False
                game.victory_pending = False
                game.game_state = "VICTORY"
                try:
                    game.victory_entered_at = pygame.time.get_ticks()
                except Exception:
                    game.victory_entered_at = 0
                # Clear any pending mouse clicks to avoid queued input
                try:
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                    pygame.event.clear(pygame.MOUSEBUTTONUP)
                except Exception:
                    pass
                SoundManager.stop_music()
        except Exception:
            pass
    except Exception:
        pass
