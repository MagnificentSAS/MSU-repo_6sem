from math import sqrt
import socket
import sys

def func(a, b):
    return a + 1 / b

def sqroots(coeffs:str) -> str:
    a, b, c = coeffs.split()
    a, b, c = float(a), float(b), float(c)
    D = b ** 2 - 4 * a * c
    if D < 0:
        return ""
    elif D == 0:
        return f"{-b / 2 / a}"
    else:
        return f"{-(b - sqrt(D)) / 2 / a} {-(b + sqrt(D)) / 2 / a}"

def sqrootnet(coeffs: str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 1337))
        msg = sys.argv[1].encode() +b"\n"
        s.sendall(msg)
        print(s.recv(1024).rstrip().decode())
