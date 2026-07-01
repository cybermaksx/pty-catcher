import socket

def build_listener(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    return s


s = build_listener("0.0.0.0", 4444)
print("[*] listening on 4444")
conn, addr = s.accept()
print(f"[+] connection from {addr}")

data = conn.recv(4096)
print("got:", data)
