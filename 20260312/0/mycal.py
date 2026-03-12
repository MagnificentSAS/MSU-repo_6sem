#!~/Документы/MSU-proga/Python/MSU-repo_6sem/hworker-env python3

import cmd
from shlex import split
from pathlib import Path
import calendar

class CalCmdl(cmd.Cmd):
    prompt = "year> "

    def do_month(self, arg):
        """Print a month’s calendar as returned by formatmonth()."""
        args = split(arg)
        print(calendar.TextCalendar().prmonth(int(args[0]), int(args[1])))

    def do_year(self, arg):
        """Print the calendar for an entire year as returned by formatyear()."""
        args = split(arg)
        print(calendar.TextCalendar().pryear(int(args[0])))

    def do_EOF(self, arg):
        print("BYE")
        return 1

if __name__ == "__main__":
    CalCmdl().cmdloop()
