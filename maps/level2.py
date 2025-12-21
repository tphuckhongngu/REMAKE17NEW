# maps/level2.py
# Level 2: Industrial Zone - corridors, nước chặn, nhiều rác (khó hơn)
# Tile convention same as level1

def get_map(width, height):
    m = [[0 for _ in range(width)] for _ in range(height)]

    # biên
    for x in range(width):
        m[0][x] = 1
        m[height-1][x] = 1
    for y in range(height):
        m[y][0] = 1
        m[y][width-1] = 1

    # hành lang dọc dạng lưới (corridors)
    for x in range(6, width-6, 10):
        for y in range(3, height-3):
            if (y % 5) != 0:
                m[y][x] = 1

    # sông/nước ngang cắt ngang (tạo choke point)
    mid = height // 2
    for x in range(8, min(48, width-8)):
        m[mid][x] = 4
    # chừa vài ô làm cầu hẹp
    for x in range(20, 24):
        if x < width:
            m[mid][x] = 0

    # rác nhiều rải khắp hành lang
    for y in range(4, height-4, 4):
        for x in range(4, width-4, 6):
            if m[y][x] == 0:
                m[y][x] = 3

    # thêm vài tường chặn lớn
    for x in range(15, 25):
        if x < width-2:
            m[10][x] = 1
            m[height-12][x] = 1

    # exit
    m[height-2][width-2] = 5
    return m

def get_spawns(width, height):
    player = (2, 2)
    monsters = []
    # spawn dày đặc quanh hành lang trung tâm
    for y in range(6, height-6, 3):
        for x in range(12, min(48, width-12), 7):
            if x < width-2:
                monsters.append((x, y))
    return {"player": player, "monsters": monsters}
MAP = get_map(100, 50)  # Tạo list 2D tĩnh kích thước chuẩn