import argparse
import asyncio
import os
import sys
from shlex import split
from mood.common import SIZE


class serverMUD:
    HEIGHT, WIDTH = SIZE
    weapons = {"sword": 10, "spear": 15, "axe": 20}

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
        return (f"moved {pos_x} {pos_y} " + self._encounter(pos_x, pos_y)), False

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

    def addmon(self, x: int, y: int, name: str, hello: str, hp: int):
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


MUD = serverMUD()


async def echo(reader, writer):
    data = await reader.readline()
    _, name = split(data.decode())
    if name in MUD.clients.keys():
        writer.write("not_ok".encode())
    else:
        writer.write("ok".encode())
        for out, _, _ in MUD.clients.values():
            await out.put(f"started '{name}'")

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

                    res, other_fl, user_fl = None, False, True
                    if command == "left":
                        res, other_fl = MUD.do_left(name)
                    elif command == "right":
                        res, other_fl = MUD.do_right(name)
                    elif command == "down":
                        res, other_fl = MUD.do_down(name)
                    elif command == "up":
                        res, other_fl = MUD.do_up(name)
                    elif command == "addmon":
                        res, other_fl = MUD.addmon(int(args[0]), int(args[1]), args[2], args[3], int(args[4]))
                    elif command == "attack":
                        res, other_fl = MUD.attack(args[0], args[1], name)
                    elif command == "sayall":
                        res, other_fl, user_fl = "sayed " + f"'{args[0]}'", True, False
                    elif command == "stop":
                        cont_fl = False
                        res, other_fl, user_fl = "stopped", True, False
                    if res:
                        if other_fl:
                            for out, _, _ in MUD.clients.values():
                                if user_fl or out is not MUD.clients[name][0]:
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

parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                 description="Server for MUD")

parser.add_argument('--host', type=str, default='localhost', help='Host, default localhost')
parser.add_argument('--port', type=int, default=1337, help='Port, default 1337')
args = parser.parse_args()

asyncio.run(server_main(args.port))
