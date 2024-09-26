import tkinter as tk
from gui import CodeExtractorGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeExtractorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_application)
    root.mainloop()