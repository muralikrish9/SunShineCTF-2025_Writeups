# SunshineCTF 2024 - Numbers Game Writeup

## Challenge Overview
- Category: Reverse Engineering
- Binary: numbers-game (64-bit PIE ELF)
- Service: nc chal.sunshinectf.games 25101
- The prompt teased a ridiculous number of fingers, pointing to a deterministic solution hidden in the binary.

## Initial Recon
1. Ran the binary locally to observe the banner and input flow.
2. Used objdump -d and section dumps to follow control flow and find embedded strings.
3. Located the success path that issues system("cat flag.txt") after comparing an unsigned integer.

## Reversing the Core Logic
Key excerpt reconstructed from the disassembly of main:
~~~c
srand(time(NULL));
long r1 = rand();
long r2 = rand();
long r3 = rand();
unsigned long target = (r1 & 0x7fffffff)
                     | ((unsigned long)(r2 & 0x7fffffff) << 31)
                     | ((unsigned long)(r3 & 0x3) << 62);
scanf("%llu", &guess);
if (guess == target)
    system("cat flag.txt");
~~~
- The seed comes straight from time(NULL), so the server and client share nearly identical seeds.
- Combining three consecutive rand() outputs into a 64-bit value is still predictable once the seed is known.

## Exploit Strategy
1. Reproduce glibc's PRNG locally via ctypes.CDLL("libc.so.6") to access srand and rand.
2. Recalculate the target value using the current timestamp (optionally scan a few surrounding seconds for skew).
3. Connect to the remote socket, submit the guess, and retry quickly until the remote seed matches the local one.

## Solver Script
~~~python
#!/usr/bin/env python3
import socket
import time
import ctypes

HOST, PORT = "chal.sunshinectf.games", 25101
libc = ctypes.CDLL("libc.so.6")

def compute_target(seed: int) -> int:
    libc.srand(seed)
    r1, r2, r3 = libc.rand(), libc.rand(), libc.rand()
    value  = (r1 & 0x7fffffff)
    value |= (r2 & 0x7fffffff) << 31
    value |= (r3 & 0x3) << 62
    return value & 0xffffffffffffffff

while True:
    with socket.create_connection((HOST, PORT)) as sock:
        banner = sock.recv(4096)
        seed = int(time.time())
        guess = compute_target(seed)
        sock.sendall(f"{guess}\n".encode())
        response = sock.recv(4096)
        print(banner.decode(errors="ignore"))
        print(response.decode(errors="ignore"))
        if b"sun{" in response:
            break
    time.sleep(0.2)
~~~
This loop reattempts the guess every fraction of a second until the timestamp aligns with the server's seed.

## Result
Running the script reveals the flag:
~~~
sun{I_KNOW_YOU_PLACED_A_MIRROR_BEHIND_ME}
~~~

## Takeaways
- PRNGs seeded with low-entropy values such as the current Unix time are trivial to predict.
- Combining multiple rand() outputs does not add security when the seed is guessable.
- Inspecting for system calls or file I/O in reversing challenges often uncovers the win condition immediately.
