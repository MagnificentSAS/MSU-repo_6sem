from cowsay import cowsay

pos_x, pos_y = 0, 0
HEIGHT, WIDTH = 10, 10
monsters = [[None for _ in range(HEIGHT)] for _ in range(WIDTH)]

def move(command: str):
    global pos_x, pos_y
    global HEIGHT, WIDTH
    match(command):
        case "up":
            pos_y = (pos_y - 1 + HEIGHT) % HEIGHT
        case "down":
            pos_y = (pos_y + 1) % HEIGHT
        case "left":
            pos_x = (pos_x - 1 + WIDTH) % WIDTH
        case "right":
            pos_x = (pos_x + 1) % WIDTH

    print(f"Moved to ({pos_x}, {pos_y})")

    if monsters[pos_x][pos_y]:
        print(cowsay(monsters[pos_x][pos_y]))

