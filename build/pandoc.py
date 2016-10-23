
import subprocess

PANDOC_BIN = 'pandoc'

def convert(input_type, output_type, input_data):
    proc = subprocess.Popen([
            PANDOC_BIN,
            '--from', input_type,
            '--to', output_type,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(input=input_data)
    except Exception:
        stdout = b''
        stderr = b''
    proc.wait()
    return stdout
