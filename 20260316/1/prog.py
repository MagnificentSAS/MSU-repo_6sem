import cmd
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
from shlex import split

class CmdMUD(cmd.Cmd):
    prompt = "(mud) "
    pos_x, pos_y = 0, 0
    HEIGHT, WIDTH = 10, 10

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

    weapons = { "sword": 10, "spear": 15, "axe": 20 }

    def __init__(self):
        super().__init__()
        self.monsters = [[None for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    def do_up(self, args):
        """Use to move up"""
        if args:
            print("Invalid arguments")
            return
        self.pos_y = (self.pos_y - 1 + self.HEIGHT) % self.HEIGHT
        print(f"Moved to ({self.pos_x}, {self.pos_y})")
        self._encounter()

    def do_down(self, args):
        """Use to move down"""
        if args:
            print("Invalid arguments")
            return
        self.pos_y = (self.pos_y + 1) % self.HEIGHT
        print(f"Moved to ({self.pos_x}, {self.pos_y})")
        self._encounter()

    def do_left(self, args):
        """Use to move left"""
        if args:
            print("Invalid arguments")
            return
        self.pos_x = (self.pos_x - 1 + self.WIDTH) % self.WIDTH
        print(f"Moved to ({self.pos_x}, {self.pos_y})")
        self._encounter()

    def do_right(self, args):
        """Use to move right"""
        if args:
            print("Invalid arguments")
            return
        self.pos_x = (self.pos_x + 1) % self.WIDTH
        print(f"Moved to ({self.pos_x}, {self.pos_y})")
        self._encounter()

    def _encounter(self) -> None:
        if self.monsters[self.pos_x][self.pos_y]:
            name, hello, hp = self.monsters[self.pos_x][self.pos_y]
            if name != "jgsbat":
                print(cowsay(hello, cow=name))
            else:
                print(cowsay(hello, cowfile=self.jgsbat))

    def _addmon(self, x: int, y: int, name: str,  hello: str, hp: int) -> None:
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if self.monsters[x][y]:
            print("Replaced the old monster")
        self.monsters[x][y] = (name, hello, hp)

    def _parse_addmon(self, args: list[str]) -> tuple[str ,str, int, int, int]:
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
                    if hp <= 0:
                        raise ValueError
                else:
                    raise ValueError
                args = args[2:]
                continue

            if args[0] == "coords":
                if x is None and y is None:
                    x, y = int(args[1]), int(args[2])
                    if not(0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
                        raise ValueError
                else:
                    raise ValueError
                args = args[3:]
                continue

            raise ValueError

        return name, hello, hp, x, y

    def do_addmon(self, args):
        """Adds monster saying hello to coords with hp.
        Coords, hello message and hp are given after words coords, hello and hp"""
        args = split(args)
        if len(args) != 8:
            print("Invalid arguments")
            return
        try:
            name, hello, hp, x, y = self._parse_addmon(args)
        except ValueError:
            print("Invalid arguments")
            return

        if name not in list_cows() and name != "jgsbat":
            print("Cannot add unknown monster")
            return
        self._addmon(x=x, y=y, name=name, hello=hello, hp=hp)

    def do_EOF(self, args):
        print()
        return 1

    def do_attack(self, args):
        """Damages named monster in room for some hp:
        10 - sword
        15 - spear
        20 - axe
        Chose weapon after with"""
        args = split(args)
        if len(args) != 1 and len(args) != 3:
            print("Invalid arguments")
            return
        elif len(args) == 1:
            attack_name, = args
            weapon = "sword"
        else:
            attack_name, command, weapon = args
            if command != "with":
                print("Invalid arguments")
                return

        if weapon not in self.weapons:
            print("Unknown weapon")
            return

        if self.monsters[self.pos_x][self.pos_y] is None or attack_name != self.monsters[self.pos_x][self.pos_y][0]:
            print(f"No {attack_name} here")
            return
        name, hello, hp = self.monsters[self.pos_x][self.pos_y]

        damage = min(hp, self.weapons[weapon])

        print(f"Attacked {name}, damage {damage} hp")
        hp -= damage
        if hp == 0:
            print(f"{name} died")
            self.monsters[self.pos_x][self.pos_y] = None
        else:
            print(f"{name} now has {hp}")
            self.monsters[self.pos_x][self.pos_y] = (name, hello, hp)

    def complete_attack(self, text, line, begidx, endidx):
        line_words = split(line[:begidx])
        if len(line_words) <= 1:
            return [cow for cow in list_cows() + ["jgsbat"] if cow.startswith(text)]
        elif len(line_words) == 2:
            return ["with"] if "with".startswith(text) else []
        else:
            return [weapon for weapon in self.weapons if weapon.startswith(text)]


if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")
    CmdMUD().cmdloop()