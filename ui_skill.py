import pygame

def draw_skill_ui(screen, player, font):
	"""Draw a minimal skill UI. Safe no-op if player or font missing."""
	try:
		if screen is None or player is None or font is None:
			return

		# Small skills panel at top-left
		panel = pygame.Rect(10, 60, 140, 48)
		try:
			pygame.draw.rect(screen, (40, 40, 40), panel)
			pygame.draw.rect(screen, (120, 120, 120), panel, 2)
		except Exception:
			pass

		# Draw skill count or placeholders
		try:
			if hasattr(player, 'skills'):
				text = f"Skills: {len(player.skills)}"
			else:
				text = "Skills: 0"
			surf = font.render(text, True, (220, 220, 220))
			screen.blit(surf, (panel.x + 6, panel.y + 6))
		except Exception:
			pass
	except Exception:
		return


__all__ = ['draw_skill_ui']
