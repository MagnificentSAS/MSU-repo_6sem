import sys

while l := sys.stdin.readline().split():
    print(l[0], len(l[1:]), l[1:])
