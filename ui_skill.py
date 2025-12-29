import pygame


def draw_skill_ui(screen, player, font):
    """Minimal fallback: draw simple skill placeholders if available."""
    try:
        if player is None:
            return
        # draw a simple border for skills area
        rect = pygame.Rect(10, 60, 120, 40)
        try:
            pygame.draw.rect(screen, (40, 40, 40), rect)
            pygame.draw.rect(screen, (120, 120, 120), rect, 2)
            # optional: draw skill count if player has attribute
            if hasattr(player, 'skills'):
                text = f"Skills: {len(player.skills)}"
                surf = font.render(text, True, (220,220,220))
                screen.blit(surf, (rect.x + 6, rect.y + 6))
        except Exception:
            pass
    except Exception:
        pass
