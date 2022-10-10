import tkinter as tk
import tkinter.ttk as ttk

# Create the master object
master = tk.Tk()

# Create a progressbar widget
progress_bar = ttk.Progressbar(master, orient="horizontal",
                              mode="determinate", maximum=100, value=0)

# And a label for it
label_1 = tk.Label(master, text="Progress Bar")


# Use the grid manager
label_1.grid(row=0, column=0)
progress_bar.grid(row=0, column=1)

# Start auto-incrementing periodically
progress_bar.start()
progress_bar.step(10)

# The application mainloop
tk.mainloop()


