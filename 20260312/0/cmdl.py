#!~/Документы/MSU-proga/Python/MSU-repo_6sem/hworker-env python3

import cmd
from shlex import split
from pathlib import Path

class SizeCmdl(cmd.Cmd):
    prompt = "==> "

    def do_size(self, arg):
        args = split(arg)
        for name in args:
            print(f"{name} file len: {Path(name).stat().st_size}")

    def do_EOF(self, arg):
        print("BYE")
        return 1

if __name__ == "__main__":
    SizeCmdl().cmdloop()
