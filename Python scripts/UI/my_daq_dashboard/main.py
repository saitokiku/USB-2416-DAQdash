import tkinter as tk
from dashboard.app import DashboardApp

if __name__ == '__main__':
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
