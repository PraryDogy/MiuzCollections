import subprocess


def copy(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))

def paste():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')
