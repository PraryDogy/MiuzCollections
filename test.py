import subprocess



paths = ["/Users/evlosh/Downloads/new.jpg", "/Users/evlosh/Downloads/15ch16bit.tif"]

paths = (
    f"\"{i}\" as POSIX file"
    for i in paths
    )

paths = ", ".join(paths)

applescript = f"""
    tell application \"Finder\"
    reveal {{{paths}}}
    activate
    end tell
    """

args = [
    item
    for x in [("-e",l.strip())
    for l in applescript.split('\n')
    if l.strip() != ''] for item in x
    ]

# print(args)

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
