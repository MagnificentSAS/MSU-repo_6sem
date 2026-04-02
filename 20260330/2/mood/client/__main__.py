import argparse
import cmd
import os
import random
import socket
import sys
import threading
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
from shlex import split
from mood.common import SIZE

class clientMUD(cmd.Cmd):
    HEIGHT, WIDTH = SIZE
    weapons = ["sword", "spear", "axe"]
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
    prompt = ""

    def __init__(self, sock, host=None, port=None, name=None):
        super().__init__()
        self.s = sock
        self.name = name
        host = "localhost" if host is None else host
        port = 1337 if port is None else port
        self.s.connect((host, port))
        self.s.sendall(("start_session '" + self.name + "'\n").encode())
        ans = self.s.recv(1024).rstrip().decode()
        if ans != "ok":
            print("Bad name input. Try another.")
            exit(0)

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def receive_messages(self):
        """Поток для асинхронного приема сообщений от сервера"""
        while True:
            try:
                command, *data = split(self.s.recv(1024).rstrip().decode())
                if command == "moved":
                    print(f"Moved to ({int(data[0])}, {int(data[1])})")
                    if len(data) == 4:
                        self._encounter_redner(data[2], data[3])
                elif command == "addmoned":
                    print(f"{data[5]} added monster {data[1]} to ({data[2]}, {data[3]}) saying {data[4]}")
                    if data[0] == '1':
                        print("Replaced the old monster")
                elif command == "started":
                    print(f"{data[-1]} entered dungeon")
                elif command == "stopped":
                    print(f"{data[-1]} run out of dungeon")
                elif command == "attacked":
                    if data[0] == "0":
                        print(f"No {data[1]} here")
                        return

                    name, weapon, damage, hp, autor = data
                    print(f"{autor} attacked {name} with {weapon}, damage {damage} hp")
                    if hp == "0":
                        print(f"{name} died")
                    else:
                        print(f"{name} now has {hp}")
                elif command == "sayed":
                    print(f"{data[-1]}: {data[0]}")

            except:
                break

    def _encounter_redner(self, name, hello):
        if name != "jgsbat":
            print(cowsay(hello, cow=name))
        else:
            print(cowsay(hello, cowfile=self.jgsbat))

    def do_up(self, args):
        """Use to move up"""
        if args:
            print("Invalid arguments")
            return
        self.s.sendall("up".encode() + b'\n')

    def do_down(self, args):
        """Use to move down"""
        if args:
            print("Invalid arguments")
            return
        self.s.sendall("down".encode() + b'\n')

    def do_left(self, args):
        """Use to move left"""
        if args:
            print("Invalid arguments")
            return
        self.s.sendall("left".encode() + b'\n')

    def do_right(self, args):
        """Use to move right"""
        if args:
            print("Invalid arguments")
            return
        self.s.sendall("right".encode() + b'\n')

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
        self.s.sendall(("addmon "+ f"{x} {y} {name} '{hello}' {hp}\n").encode())

    def do_EOF(self, args):
        self.s.sendall("stop\n".encode())
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

        self.s.sendall(("attack "+ f"{attack_name} {weapon}\n").encode())

    def do_sayall(self, arg):
        """Say something to everyone!

        Use one word or one string in ""
        """
        args = split(arg)
        if len(args) == 0:
            print("You said nothing")
            return

        if len(args) > 1:
            print("Too many arguments")
            return

        self.s.sendall(("sayall "+ f"'{args[0]}'\n").encode())

    def complete_attack(self, text, line, begidx, endidx):
        line_words = split(line[:begidx])
        if len(line_words) <= 1:
            return [cow for cow in list_cows() + ["jgsbat"] if cow.startswith(text)]
        elif len(line_words) == 2:
            return ["with"] if "with".startswith(text) else []
        else:
            return [weapon for weapon in self.weapons if weapon.startswith(text)]


parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                 description="Client for MUD")

parser.add_argument('name', nargs='?', default=f"Guest{random.randint(1, 1000000)}", type=str, help="Name of user. Used only for client, but write evety time")
parser.add_argument('--host', type=str, default='localhost', help='Host, default localhost')
parser.add_argument('--port', type=int, default=1337, help='Port, default 1337')
args = parser.parse_args()

print("<<< Welcome to Python-MUD 0.1 >>>")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    clientMUD(s, args.host, args.port, args.name).cmdloop()
