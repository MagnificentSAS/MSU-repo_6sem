import shlex

l = input("FIO:")

print(shlex.join(shlex.split(l)))
