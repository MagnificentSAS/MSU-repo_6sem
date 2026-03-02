import sys
from cowsay import cowsay

pos_x, pos_y = 0, 0
HEIGHT, WIDTH = 10, 10
monsters = [[None for _ in range(HEIGHT)] for _ in range(WIDTH)]

def move(command: str) -> None:
    global pos_x, pos_y
    global HEIGHT, WIDTH
    global monsters
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

def encounter(x: int, y: int) -> None:
    if monsters[x][y]:
        print(cowsay(monsters[x][y]))

def addmon(x: int, y: int, hello: str) -> None:
    global monsters
    print(f"Added monster to ({x}, {y}) saying {hello}")
    if monsters[x][y]:
        print("Replaced the old monster")
    monsters[x][y] = hello

if __name__ == "__main__":
    commands = ["up", "down", "left", "right", "addmon"]
    while line := sys.stdin.readline().split():
        command, args = line[0], line[1:]
        if command in commands[0:4]:
            if len(args) == 0:
                move(command)
            else:
                print("Invalid arguments")
                continue

            encounter(pos_x, pos_y)
        elif command == commands[4]:
            if len(args) != 3:
                print("Invalid arguments")
                continue
            try:
                x, y = int(args[0]), int(args[1])
            except ValueError:
                print("Invalid arguments")
                continue
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                addmon(x, y, args[2])
            else:
                print("Invalid arguments")
        else:
            print("Invalid command")
