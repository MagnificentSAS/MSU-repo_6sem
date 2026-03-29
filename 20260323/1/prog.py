import argparse
import asyncio
import cmd
import os
import random
import socket
import sys
import threading
from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
from shlex import split

SIZE = (10, 10)

class serverMUD:
    HEIGHT, WIDTH = SIZE
    weapons = { "sword": 10, "spear": 15, "axe": 20 }

    def __init__(self):
        self.clients = {}
        self.monsters = [[None for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    def do_up(self, autor):
        q, pos_x, pos_y = self.clients[autor]
        pos_y = (pos_y - 1 + self.HEIGHT) % self.HEIGHT
        self.clients[autor] = (q, pos_x, pos_y)
        return (f"moved {pos_x} {pos_y} " + self._encounter(pos_x, pos_y)), False

    def do_down(self, autor):
        q, pos_x, pos_y = self.clients[autor]
        pos_y = (pos_y + 1) % self.HEIGHT
        self.clients[autor] = (q, pos_x, pos_y)
        return(f"moved {pos_x} {pos_y} " + self._encounter(pos_x, pos_y)), False

    def do_left(self, autor):
        q, pos_x, pos_y = self.clients[autor]
        pos_x = (pos_x - 1 + self.WIDTH) % self.WIDTH
        self.clients[autor] = (q, pos_x, pos_y)
        return (f"moved {pos_x} {pos_y} " + self._encounter(pos_x, pos_y)), False

    def do_right(self, autor):
        q, pos_x, pos_y = self.clients[autor]
        pos_x = (pos_x + 1) % self.WIDTH
        self.clients[autor] = (q, pos_x, pos_y)
        return (f"moved {pos_x} {pos_y} " + self._encounter(pos_x, pos_y)), False

    def _encounter(self, pos_x, pos_y) -> str:
        if self.monsters[pos_x][pos_y]:
            name, hello, hp = self.monsters[pos_x][pos_y]
            return f"{name} '{hello}'"

        return ""

    def addmon(self, x: int, y: int, name: str,  hello: str, hp: int):
        if self.monsters[x][y]:
            res_str = "1"
        else:
            res_str = "0"
        self.monsters[x][y] = (name, hello, hp)
        res_str = f"addmoned {res_str} {name} {x} {y} '{hello}'"
        return res_str, True

    def attack(self, attack_name, weapon, autor):
        q, pos_x, pos_y = self.clients[autor]
        if self.monsters[pos_x][pos_y] is None or attack_name != self.monsters[pos_x][pos_y][0]:
            return f"attacked 0 {attack_name}", False
        name, hello, hp = self.monsters[pos_x][pos_y]

        damage = min(hp, self.weapons[weapon])

        hp -= damage
        res = f"attacked {name} {weapon} {damage} {hp}"
        if hp == 0:
            self.monsters[pos_x][pos_y] = None
        else:
            self.monsters[pos_x][pos_y] = (name, hello, hp)
        return res, True


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


    def complete_attack(self, text, line, begidx, endidx):
        line_words = split(line[:begidx])
        if len(line_words) <= 1:
            return [cow for cow in list_cows() + ["jgsbat"] if cow.startswith(text)]
        elif len(line_words) == 2:
            return ["with"] if "with".startswith(text) else []
        else:
            return [weapon for weapon in self.weapons if weapon.startswith(text)]


MUD = serverMUD()

async def echo(reader, writer):
    data = await reader.readline()
    _, name = split(data.decode())
    if name in MUD.clients.keys():
        writer.write("not_ok".encode())
    else:
        writer.write("ok".encode())
        MUD.clients[name] = (asyncio.Queue(), 0, 0)
        send = asyncio.create_task(reader.readline())
        receive = asyncio.create_task(MUD.clients[name][0].get())
        cont_fl = True
        while cont_fl:
            done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
            for q in done:
                if q is send:
                    send = asyncio.create_task(reader.readline())
                    command, *args = split(q.result().decode())

                    res, fl = None, False
                    if command == "left":
                        res, fl = MUD.do_left(name)
                    elif command == "right":
                        res, fl = MUD.do_right(name)
                    elif command == "down":
                        res, fl = MUD.do_down(name)
                    elif command == "up":
                        res, fl = MUD.do_up(name)
                    elif command == "addmon":
                        res, fl = MUD.addmon(int(args[0]), int(args[1]), args[2], args[3], int(args[4]))
                    elif command == "attack":
                        res, fl = MUD.attack(args[0], args[1], name)
                    elif command == "stop":
                        cont_fl = False
                        break
                    if res:
                        if fl:
                            for out, _, _ in MUD.clients.values():
                                await out.put(f"{res} '{name}'")
                        else:
                            writer.write(res.encode())
                            await writer.drain()

                elif q is receive:
                    receive = asyncio.create_task(MUD.clients[name][0].get())
                    writer.write(f"{q.result()}".encode())
                    await writer.drain()

        send.cancel()
        receive.cancel()
        del MUD.clients[name]

    print(name, "DONE")
    writer.write(b"")
    writer.close()
    await writer.wait_closed()

async def server_main(port):
    server = await asyncio.start_server(echo, '0.0.0.0', port)
    async with server:
        await server.serve_forever()

def server(port):
    asyncio.run(server_main(port))

def client(host, port, name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        clientMUD(s, host, port, name).cmdloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     description="Client-server one user MUD")

    parser.add_argument('name', nargs='?', default=f"Guest{random.randint(1, 1000000)}", type=str, help="Name of user. Used only for client, but write evety time")
    parser.add_argument('-m', '--mode', choices=['client', 'server'],
                        default='client', help="Work mode: client or server. client mode is default.")
    parser.add_argument('--host', type=str, default='localhost', help='Host, default localhost')
    parser.add_argument('--port', type=int, default=1337, help='Port, default 1337')
    args = parser.parse_args()

    if args.mode == 'client':
        print("<<< Welcome to Python-MUD 0.1 >>>")
        client(args.host, args.port, args.name)
    else:
        server(args.port)