from shlex import split, join
import sys

while l := split(sys.stdin.readline()):
    print(join(l))
