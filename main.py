from platform import node
from app.ui import VisualizerApp
from app.parser import parse_log_file
import tkinter.font as tkfont
import tkinter as tk

if __name__ == "__main__":
    LOG_FILE = "test.log"
    root = tk.Tk()
    area, nodes, timeline = parse_log_file(LOG_FILE)
    ui = VisualizerApp(root, area, nodes, timeline, 50)
    root.mainloop()
