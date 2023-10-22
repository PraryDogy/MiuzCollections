import subprocess
from cfg import cnf


applescript = f"""
    set appName to "{cnf.app_name}"
    tell application "System Events"
        set visible of application process appName to false
    end tell
    """

args = []
for row in applescript.split("\n"):
    if row.strip():
        args = args + ["-e", row.strip()]


args = [
    arg for row in applescript.split("\n")
    for arg in ("-e", row.strip())
    if row.strip()
    ]



print(args)

# subprocess.call(["osascript"] + args))

indices = [1, 2, 3]
extra_indices = [
    index+i for index in indices
    for i in range(3)
    ]
