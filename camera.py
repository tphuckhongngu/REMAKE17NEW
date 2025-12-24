import pygame

class Camera:
    def __init__(self, screen_w, screen_h):
        self.offset = pygame.Vector2(0, 0)
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self, target):
        # camera luôn lấy player làm trung tâm
        self.offset.x = target.rect.centerx - self.screen_w // 2
        self.offset.y = target.rect.centery - self.screen_h // 2

    def apply(self, rect):
        # chỉ dịch khi vẽ, KHÔNG ảnh hưởng logic
        return rect.move(-self.offset.x, -self.offset.y)
