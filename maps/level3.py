# maps/level3.py
# Level 3: The Junk Maze - mê cung, nhiều tường, nhiều rác, boss area
# Tile convention same as level1

def get_map(width, height):
    # bắt đầu bằng tường toàn bộ, sau đó carve hành lang để tạo mê cung
    m = [[1 for _ in range(width)] for _ in range(height)]

    # carve pattern để tạo đường
    for y in range(1, height-1):
        for x in range(1, width-1):
            if (x * 2 + y * 3) % 5 == 0:
                m[y][x] = 0

    # mở thêm đường lớn hai hàng trên/dưới
    for x in range(2, width-2):
        if x % 5 != 0:
            m[3][x] = 0
            m[height-4][x] = 0

    # rác dày đặc trong ô trống
    for y in range(2, height-2):
        for x in range(2, width-2):
            if m[y][x] == 0 and ((x + y) % 7 == 0):
                m[y][x] = 3

    # khu vực boss (gần giữa), thêm spawn lớn
    cx = width // 2
    cy = height // 2
    for dy in range(-3, 4):
        for dx in range(-6, 7):
            xx = cx + dx
            yy = cy + dy
            if 0 < xx < width-1 and 0 < yy < height-1:
                # make a large open arena with some trash
                if abs(dx) < 3 and abs(dy) < 2:
                    m[yy][xx] = 0
                elif (dx + dy) % 4 == 0:
                    m[yy][xx] = 3

    # thêm vài hồ nhỏ
    for y in range(5, 9):
        for x in range(5, 12):
            if x < width and y < height:
                m[y][x] = 4

    # exit
    m[height-2][width-2] = 5
    return m

def get_spawns(width, height):
    player = (2, 2)
    monsters = []
    # spawn quanh mê cung và khu boss
    for y in range(4, height-4, 3):
        for x in range(4, width-4, 5):
            if (x + y) % 2 == 0:
                monsters.append((x, y))
    # thêm một spawn đặc biệt ở trung tâm (boss)
    monsters.append((width//2, height//2))
    return {"player": player, "monsters": monsters}
