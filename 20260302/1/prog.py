from io import StringIO
import sys
from cowsay import cowsay, list_cows, read_dot_cow
from shlex import split

pos_x, pos_y = 0, 0
HEIGHT, WIDTH = 10, 10
monsters = [[None for _ in range(HEIGHT)] for _ in range(WIDTH)]

jgsbat_ascii_art = r"""
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\'--'//__
         (((""`  `"")))
"""

jgsbat = read_dot_cow(StringIO(jgsbat_ascii_art))

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
        name, hello = monsters[x][y]
        if name != "jgsbat":
            print(cowsay(hello, cow=name))
        else:
            print(cowsay(hello, cowfile=jgsbat))

def addmon(x: int, y: int, name: str,  hello: str) -> None:
    global monsters
    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
    if monsters[x][y]:
        print("Replaced the old monster")
    monsters[x][y] = (name, hello)

def parse_addmon(args: list[str]) -> tuple[str ,str, int, int, int]:
    name = args[0]
    hello, hp, x, y = None, None, None, None
    args = args[1:]
    while args:
        if args[0] == "hello":
            if hello is None:
                hello = args[1]
            else:
                raise ValueError
            args = args[2:]
            continue

        if args[0] == "hp":
            if hp is None:
                hp = int(args[1])
            else:
                raise ValueError
            args = args[2:]
            continue

        if args[0] == "coords":
            if x is None and y is None:
                x, y = int(args[1]), int(args[2])
            else:
                raise ValueError
            args = args[3:]
            continue

        raise ValueError

    return name, hello, hp, x, y

if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")

    commands = ["up", "down", "left", "right", "addmon"]
    while line := split(sys.stdin.readline()):
        command, *args = line
        if command in commands[0:4]:
            if len(args) == 0:
                move(command)
            else:
                print("Invalid arguments")
                continue

            encounter(pos_x, pos_y)
        elif command == commands[4]:
            if len(args) != 8:
                print("Invalid arguments")
                continue
            try:
                name, hello, hp, x, y = parse_addmon(args)
            except ValueError:
                print("Invalid arguments")
                continue
            if name not in list_cows() and name != "jgsbat":
                print("Cannot add unknown monster")
                continue
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                addmon(x, y, name, hello)
            else:
                print("Invalid arguments")
        else:
            print("Invalid command")
