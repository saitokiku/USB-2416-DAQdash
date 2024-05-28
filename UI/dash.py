import tkinter as tk
from tkinter import Menu, messagebox

def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

def right_click_menu(event, widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Remove Block", command=widget.remove_widget)
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title('DAQ Dashboard')

        # Setup the menu
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        # Add menu items
        self.dashboard_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Components', menu=self.dashboard_menu)
        self.dashboard_menu.add_command(label='Add Digital Out', command=self.add_digital_out)
        self.dashboard_menu.add_command(label='Add Digital In', command=self.add_digital_in)
        self.dashboard_menu.add_command(label='Add Counter Display', command=self.add_counter)
        self.dashboard_menu.add_command(label='Add Analog In Display', command=self.add_analog_in)

        # A frame to contain all dashboard elements
        self.dashboard_frame = tk.Frame(self.root, bg='white')
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Check device availability
        self.check_device_availability()

    def check_device_availability(self):
        self.device_available = False  # This should be updated with actual device check logic
        if not self.device_available:
            messagebox.showwarning("Device Warning", "DAQ Device not available. You can add components but no live data will be displayed.")

    def add_digital_out(self):
        button = DigitalOutButton(self.dashboard_frame)
        button.place(x=20, y=20)

    def add_digital_in(self):
        label = DigitalInBinaryIndicator(self.dashboard_frame)
        label.place(x=20, y=100)

    def add_counter(self):
        counter = CounterDisplay(self.dashboard_frame)
        counter.place(x=20, y=180)

    def add_analog_in(self):
        display = AnalogInDisplay(self.dashboard_frame)
        display.place(x=20, y=260)

class DigitalOutButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, text='Digital Out: OFF', font=('Helvetica', 14), height=2, width=20, **kwargs)
        self.config(command=self.toggle)
        self.state = False
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))

    def toggle(self):
        self.state = not self.state
        self.config(text=f'Digital Out: {"ON" if self.state else "OFF"}')

    def remove_widget(self):
        self.destroy()

class DigitalInBinaryIndicator(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, text='Digital In: 0', font=('Helvetica', 14), height=2, width=20, bg='lightgrey', **kwargs)
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_indicator()

    def update_indicator(self):
        self.after(100, self.update_indicator)  # Placeholder for actual digital input read

    def remove_widget(self):
        self.destroy()

class CounterDisplay(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, text='Counter: 0', font=('Helvetica', 14), height=2, width=20, bg='lightgrey', **kwargs)
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_display()

    def update_display(self):
        self.after(500, self.update_display)  # Placeholder for actual counter read

    def remove_widget(self):
        self.destroy()

class AnalogInDisplay(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scalar_label = tk.Label(self, text='Analog In: 0.00 V', font=('Helvetica', 14), height=2, width=20)
        self.scalar_label.pack()
        self.init_plot()
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))

    def init_plot(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.animation import FuncAnimation

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlim(0, 50)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100, blit=True)

    def update_display(self):
        self.after(100, self.update_display)  # Placeholder for analog input read

    def update_plot(self, frame):
        # Placeholder for updating plot data
        return self.line,

    def remove_widget(self):
        self.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
