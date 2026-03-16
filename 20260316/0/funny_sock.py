import sys
import socket
import cmd

class snd_rcv(cmd.Cmd):
    completekey = 'tab'
    prompt = "netcat> "

    def __init__(self, s):
        super().__init__()
        self.s = s
        host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
        port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
        self.s.connect((host, port))

    def do_print(self, arg):
        self.s.sendall(("print " + arg).encode() + b'\n')
        print(self.s.recv(1024).rstrip().decode())

    def do_info(self, arg):
        self.s.sendall(("info " + arg).encode() + b'\n')
        print(self.s.recv(1024).rstrip().decode())

    def complete_info(self, text, line, begidx, endidx):
        return [name for name in ["port", "host"] if name.startswith(text)]

    def do_EOF(self, arg):
        return 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    snd_rcv(s).cmdloop()
