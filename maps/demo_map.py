# maps/demo_map.py

C = "co"
D = "dat"
B = "betong"
W = "nuoc"
T = "tuong"

WIDTH = 40
HEIGHT = 25

MAP_LAYOUT = []

for y in range(HEIGHT):
    row = []
    for x in range(WIDTH):

        # Viền ngoài là tường
        if x == 0 or y == 0 or x == WIDTH - 1 or y == HEIGHT - 1:
            row.append(T)

        # Vành tường thứ 2 (cỏ)
        elif x == 1 or y == 1 or x == WIDTH - 2 or y == HEIGHT - 2:
            row.append(C)

        # Khu trung tâm cỏ
        elif 15 <= x <= 24 and 10 <= y <= 15:
            row.append(C)

        # Một số vùng nước
        elif (5 <= x <= 10 and 18 <= y <= 22) or (30 <= x <= 35 and 5 <= y <= 9):
            row.append(W)

        # Một số vùng bê tông xen kẽ
        elif (x + y) % 7 == 0:
            row.append(B)

        else:
            row.append(D)

    MAP_LAYOUT.append(row)

MAP_ROWS = len(MAP_LAYOUT)