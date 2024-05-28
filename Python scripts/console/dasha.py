import tkinter as tk
from tkinter import Menu, messagebox, simpledialog
import ctypes
from mcculw import ul
from mcculw.enums import ULRange, DigitalPortType, InterfaceType
from mcculw.ul import ULError

# Utility functions for handling drag and right-click events
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
    menu.add_command(label="Remove Block", command=widget.destroy)
    menu.add_command(label="Rename Block", command=lambda: rename_widget(widget))
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def rename_widget(widget):
    new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=widget)
    if new_name:
        widget.config(text=f"{new_name}: {widget.value}")

class DigitalOutButton(tk.Button):
    def __init__(self, master, board_num, channel=0, **kwargs):
        super().__init__(master, text='Digital Out: OFF', font=('Helvetica', 14), height=2, width=20, **kwargs)
        self.board_num = board_num
        self.channel = channel
        self.state = False
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.config(command=self.toggle)

    def toggle(self):
        self.state = not self.state
        ul.d_bit_out(self.board_num, DigitalPortType.FIRSTPORTA, self.channel, self.state)
        self.config(text=f"Digital Out: {'ON' if self.state else 'OFF'}")

class DigitalInBinaryIndicator(tk.Label):
    def __init__(self, master, board_num, port_type, **kwargs):
        super().__init__(master, text='Digital In: 0', font=('Helvetica', 14), height=2, width=20, bg='lightgrey', **kwargs)
        self.board_num = board_num
        self.port_type = port_type  # This should be set to the correct DigitalPortType constant for "port 7"
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_indicator()

    def update_indicator(self):
        try:
            # Correct usage: ul.d_in() directly returns the state of the port.
            self.value = ul.d_in(self.board_num, self.port_type)
            self.config(text=f"Digital In {self.port_type.name}: {self.value}")
            self.after(100, self.update_indicator)  # Refresh every 100ms
        except ULError as e:
            print(f"Error reading digital input: {e}")


class CounterDisplay(tk.Label):
    def __init__(self, master, board_num, counter_num=0, **kwargs):
        super().__init__(master, text='Counter: 0', font=('Helvetica', 14), height=2, width=20, bg='lightgrey', **kwargs)
        self.board_num = board_num
        self.counter_num = counter_num
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_display()

    def update_display(self):
        self.value = ul.c_in(self.board_num, self.counter_num)
        self.config(text=f"Counter: {self.value}")
        self.after(500, self.update_display)

class AnalogInDisplay(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Initialize base_text and value before using them
        self.base_text = "Analog In"
        self.value = 0.00
        self.scalar_label = tk.Label(self, text=f"{self.base_text}: {self.value:.2f} V", font=('Helvetica', 14), height=2, width=20)
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
        # Set save_count to limit the cache size
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100, blit=True, save_count=50)
        self.update_display()

    def update_display(self):
        self.value = app.read_analog_input(0)  # Update with real data
        self.scalar_label.config(text=f"{self.base_text}: {self.value:.2f} V")
        self.after(100, self.update_display)

    def update_plot(self, frame):
        # Placeholder for updating plot data
        return self.line,

    def remove_widget(self):
        self.destroy()

    def rename_widget(self):
        new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=self)
        if new_name:
            self.base_text = new_name
            self.scalar_label.config(text=f"{self.base_text}: {self.value:.2f} V")

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title('DAQ Dashboard')
        self.board_num = 0
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        self.dashboard_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Components', menu=self.dashboard_menu)
        self.dashboard_menu.add_command(label='Add Digital Out', command=self.add_digital_out)
        self.dashboard_menu.add_command(label='Add Digital In', command=self.add_digital_in)
        self.dashboard_menu.add_command(label='Add Counter Display', command=self.add_counter)
        self.dashboard_menu.add_command(label='Add Analog In Display', command=self.add_analog_in)
        self.dashboard_frame = tk.Frame(self.root, bg='white')
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        self.initialize_device()

    def add_digital_out(self):
        new_button = DigitalOutButton(self.dashboard_frame, self.board_num)
        new_button.place(x=20, y=20)

    def add_digital_in(self):
    # Initialize DigitalInBinaryIndicator with the appropriate digital port type
        new_label = DigitalInBinaryIndicator(self.dashboard_frame, self.board_num, DigitalPortType.FIRSTPORTA)
        new_label.place(x=20, y=100)

    def add_counter(self):
        new_counter = CounterDisplay(self.dashboard_frame, self.board_num)
        new_counter.place(x=20, y=180)
    
    def add_analog_in(self):
            display = AnalogInDisplay(self.dashboard_frame)
            display.place(x=20, y=260)

    def initialize_device(self):
        try:
            ul.ignore_instacal()
            devices = ul.get_daq_device_inventory(InterfaceType.USB)
            if devices:
                device = devices[0]
                ul.create_daq_device(self.board_num, device)
                messagebox.showinfo("Device Info", f"Successfully connected to {device.product_name}.")
            else:
                messagebox.showwarning("Device Warning", "No DAQ devices found.")
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
