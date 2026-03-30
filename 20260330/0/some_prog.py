"""Dummy module"""

from math import *

print(sin(0))

def func():
    """A ball doing nothing.

    Good line
    BAD line
    """
    return 0


line = """
    PID TTY      STAT   TIME  MAJFL   TRS   DRS   RSS %MEM COMMAND
   3565 tty2     Ssl+   0:00      0    24 233523 6740  0.0 /usr/libexec/gdm-x-session --run-script
    env GNOME_SHELL_SESSION_MODE=ubuntu /usr/bin/gnome-session --session=ubuntu
   3569 tty2     Sl+   57:34     11  1736 1055103 158464  0.4 /usr/lib/xorg/Xorg vt2 -displayfd 3
   -auth /run/user/1000/gdm/Xauthority -nolisten tcp -background none -noreset -keeptty -novtswit
   ch -verbose 3
   3598 tty2     Sl+    0:00      0   144 296067 17124  0.0 /usr/libexec/gnome-session-binary --s
   ession=ubuntu
  42607 pts/1    Ss     0:00      0   952  7855  6084  0.0 bash
  43060 pts/1    R+     0:00      0    63 11488  4948  0.0 ps -v
"""
