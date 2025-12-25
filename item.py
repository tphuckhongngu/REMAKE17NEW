import pygame
import math

class HealItem(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # 1. ĐỊNH NGHĨA KÍCH THƯỚC MỚI Ở ĐÂY
        # Bạn có thể thay 48, 48 thành 64, 64 nếu muốn to hơn nữa
        ITEM_SIZE = (125, 100) 

        try:
            self.image = pygame.image.load('anh/heal.png').convert_alpha()
            # Phóng to ảnh dựa trên ITEM_SIZE
            self.image = pygame.transform.scale(self.image, ITEM_SIZE)
        except:
            # Nếu lỗi, tạo khối vuông to tương ứng
            self.image = pygame.Surface(ITEM_SIZE)
            self.image.fill((0, 255, 0))
            
        # 2. CẬP NHẬT RECT
        # Quan trọng: get_rect phải gọi SAU KHI scale để khung va chạm khớp với ảnh mới
        self.rect = self.image.get_rect(center=pos)
        
        self.base_y = pos[1]
        self.angle = 0

    def update(self):
        # Hiệu ứng bập bềnh
        self.angle += 0.1
        self.rect.centery = self.base_y + math.sin(self.angle) * 5