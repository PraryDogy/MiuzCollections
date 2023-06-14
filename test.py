import subprocess
from cfg import conf

def smb_ip(path):
    df = subprocess.Popen(['df', path], stdout=subprocess.PIPE)
    outputLine = df.stdout.readlines()[1]
    unc_path = str(outputLine.split()[0])
    return "smb://" + unc_path.split("@")[-1]
