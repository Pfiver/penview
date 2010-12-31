import Tkinter as tk, tkFont
from tkMessageBox import showinfo, showerror
from os import popen


def main():
    root = tk.Tk()
    
    # Button frame
    frame = tk.Frame(root)
    update = tk.Button(frame, text="GO", command=lambda:
    showinfo("OUCH"))
    update.pack(side=tk.LEFT)
    tk.Button(frame, text="Quit", command=root.quit).pack(side=tk.LEFT)
    frame.pack(fill=tk.X, side=tk.BOTTOM)

    # Log window
    tk.Label(root, text="Log:", anchor=tk.W).pack(fill=tk.X)
    frame = tk.Frame(root)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log = tk.Text(frame, width=80)
    log.config(state=tk.DISABLED)
    log.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    scrollbar.config(command=log.yview)
    frame.pack(fill=tk.BOTH, expand=1)

    root.bind("<Escape>", lambda e: root.quit())
    update.focus()
    root.minsize(-1, 100)
    root.mainloop()

if __name__ == "__main__":
    main()