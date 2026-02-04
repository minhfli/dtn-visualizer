from platform import node
from app.ui import StepDelay, VisualizerApp
from app.parser import parse_log_file
import tkinter.font as tkfont
import tkinter as tk

if __name__ == "__main__":
    LOG_FILE = "log/dtn-SIRA_1.log"
    root = tk.Tk()
    root.option_add("*Font", tkfont.Font(family="DejaVu Sans", size=11))
    area, nodes, timeline = parse_log_file(LOG_FILE)
    delay_config = StepDelay(1, 2, 300)
    ui = VisualizerApp(root, area, nodes, timeline, delay_config)
    root.mainloop()
