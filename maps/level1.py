# maps/level1.py
# Level 1: City Outskirts - nhiều đường đi, rải rác rác thải và vài tường.
# Tile convention:
# 0: ground (đi được)
# 1: wall (tường - chặn)
# 2: grass (cỏ)
# 3: trash (rác độc - chặn)
# 4: water (nước - chậm/không chặn)
# 5: exit (cửa ra màn)
# 6: monster spawn
# 7: player start

def get_map(width, height):
    # tạo map trống
    m = [[0 for _ in range(width)] for _ in range(height)]

    # biên
    for x in range(width):
        m[0][x] = 1
        m[height-1][x] = 1
    for y in range(height):
        m[y][0] = 1
        m[y][width-1] = 1

    # một vài cụm tường nhỏ (barriers)
    for x in range(8, width-8, 14):
        for y in range(4, min(14, height-4)):
            m[y][x] = 1

    # dải cỏ (vùng an toàn) để người chơi hồi phục
    for y in range(2, 6):
        for x in range(2, min(12, width-2)):
            m[y][x] = 2

    # rải rác rác thải (điểm spawn quái có thể gần đó)
    for y in range(6, height-6, 5):
        for x in range(6, width-6, 7):
            m[y][x] = 3

    # water strip (không chặn nhưng tạo trở ngại)
    mid = height // 2
    for x in range(12, min(40, width-12)):
        m[mid][x] = 4

    # exit đặt ở góc phải dưới
    m[height-2][width-2] = 5

    return m

def get_spawns(width, height):
    # trả về tọa độ theo tile (x, y) cho player start và danh sách monsters
    player = (2, 2)  # tile coords
    monsters = []
    # tạo một vài spawn gần cụm rác
    for y in range(6, height-6, 5):
        for x in range(6, min(width-6, 50), 7):
            monsters.append((x, y))
    return {"player": player, "monsters": monsters}
MAP = get_map(100, 50)  # Tạo list 2D tĩnh kích thước chuẩn