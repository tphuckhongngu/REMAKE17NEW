import os
import pygame


class TeleportGate(pygame.sprite.Sprite):
    """Sprite animation for a teleport gate. Frames are loaded from
    the folder `anhcongdichchuyen` as 1.png .. 5.png and loop continuously.
    """
    _frames = None

    def __init__(self, center_pos, folder_path=None, anim_speed=150, flip_horiz=False):
        super().__init__()
        # load frames once
        if TeleportGate._frames is None:
            TeleportGate._frames = []
            base = folder_path or os.path.join(os.path.dirname(__file__), 'anhcongdichchuyen')
            for i in range(1, 6):
                p = os.path.join(base, f"{i}.png")
                try:
                    img = pygame.image.load(p).convert_alpha()
                except Exception:
                    # fallback: create a small surface so code won't crash
                    img = pygame.Surface((48, 48), pygame.SRCALPHA)
                    img.fill((255, 0, 255, 128))
                TeleportGate._frames.append(img)

        # keep original frames in class cache; create a per-instance frames
        # list so individual gates can be flipped without mutating shared data
        if flip_horiz:
            try:
                self.frames = [pygame.transform.flip(f, True, False) for f in TeleportGate._frames]
            except Exception:
                self.frames = list(TeleportGate._frames)
        else:
            self.frames = list(TeleportGate._frames)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = center_pos

        # animation timing
        self.anim_speed = anim_speed  # milliseconds per frame
        self._last_update = pygame.time.get_ticks()

    def update(self, *args):
        now = pygame.time.get_ticks()
        if now - self._last_update >= self.anim_speed:
            self._last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            cur = self.frames[self.frame_index]
            # preserve center when swapping image
            c = self.rect.center
            self.image = cur
            self.rect = self.image.get_rect()
            self.rect.center = c

    def get_spawn_pos(self):
        return self.rect.center
