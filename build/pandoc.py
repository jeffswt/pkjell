
import subprocess

PANDOC_BIN = 'pandoc'

def convert(input_data):
    proc = subprocess.Popen([
            PANDOC_BIN,
            '--from=markdown',
            '--to=html5',
            '--mathjax',
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    proc.stdin.write(input_data.encode('utf-8', 'ignore'))
    proc.stdin.close()
    try:
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        # Communicate blocks the channel.
        # stdout, stderr = proc.communicate(input=input_data)
    except Exception:
        stdout = b''
        stderr = b''
    stdout = stdout.decode('utf-8', 'ignore')
    stderr = stderr.decode('utf-8', 'ignore')
    proc.wait()
    return stdout
