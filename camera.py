
class Camera:
    def __init__(self, w, h):
        self.offset = [0, 0]
        self.w = w
        self.h = h

    def update(self, target):
        self.offset[0] = target.rect.centerx - self.w // 2
        self.offset[1] = target.rect.centery - self.h // 2
