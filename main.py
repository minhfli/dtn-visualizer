from platform import node
from app.ui import StepDelay, VisualizerApp
from app.parser import parse_log_file
import tkinter.font as tkfont
import tkinter as tk
import sys

if __name__ == "__main__":
    LOG_FILE = "log/dtn-SIRA_1.log"
    # change log file based on commandline
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        LOG_FILE = sys.argv[idx + 1]

    root = tk.Tk()
    root.option_add("*Font", tkfont.Font(family="DejaVu Sans", size=11))
    area, nodes, timeline = parse_log_file(LOG_FILE)
    delay_config = StepDelay(1, 2, 200)
    ui = VisualizerApp(root, area, nodes, timeline, delay_config)
    root.mainloop()
