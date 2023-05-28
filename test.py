import subprocess

args = (
    "return user locale of (get system info)",
    )

a = subprocess.check_output(["osascript", "-e", *args], text=True)
print(a.split("\n"))