import tkinter as tk
import itertools
from tkinter import Menu, messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import ctypes
from mcculw import ul
from mcculw.enums import ULRange, DigitalPortType, InterfaceType, ScanOptions, AnalogInputMode, FunctionType
from mcculw.ul import ULError
import numpy as np

# Utility function to handle the start of a drag event
def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

# Utility function to handle the motion of a drag event
def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

# Function to display a right-click context menu
def right_click_menu(event, widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Remove Block", command=widget.destroy)
    menu.add_command(label="Rename Block", command=lambda: rename_widget(widget))
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

# Function to rename a widget
def rename_widget(widget):
    new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=widget)
    if new_name:
        widget.config(text=f"{new_name}: {widget.value}")

# Class to handle the digital output functionality
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

# Class for displaying binary indicators for digital inputs
class DigitalInBinaryIndicator(tk.Label):
    def __init__(self, master, board_num, port_type, **kwargs):
        super().__init__(master, text='Digital In: 0', font=('Helvetica', 14), height=2, width=20, bg='lightgrey', **kwargs)
        self.board_num = board_num
        self.port_type = port_type
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_indicator()

    def update_indicator(self):
        try:
            self.value = ul.d_in(self.board_num, self.port_type)
            self.config(text=f"Digital In {self.port_type.name}: {self.value}")
            self.after(100, self.update_indicator)
        except ULError as e:
            print(f"Error reading digital input: {e}")

# Class for displaying counters
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

    def reset_counter(self):
        # Functionality to reset the counter (actual method depends on your hardware)
        # This example assumes resetting to zero is possible directly or by reinitializing
        try:
            ul.c_clear(self.board_num, self.counter_num)  # Assuming a method like c_clear exists
            self.value = 0  # Reset the display value
            self.config(text=f"Counter: {self.value}")
        except ULError as e:
            print(f"Error resetting counter: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset counter: {e}")

    def right_click_menu(self, event):
        print("Opening menu")  # Debug print to check if the method is being called
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Remove Block", command=self.destroy)
        menu.add_command(label="Rename Block", command=lambda: rename_widget(self))
        menu.add_command(label="Reset Counter", command=self.reset_counter)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()   

import itertools
import tkinter as tk
from tkinter import simpledialog
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange, AnalogInputMode, FunctionType
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

class AnalogInDisplay(tk.Frame):
    def __init__(self, master, board_num, **kwargs):
        super().__init__(master, **kwargs)
        self.board_num = board_num
        self.low_chan = 0
        self.high_chan = 1
        self.points_per_channel = 100
        self.rate = 100  # adjust according to your DAQ device capabilities
        self.total_count = self.points_per_channel * (self.high_chan - self.low_chan + 1)
        self.memhandle = ul.scaled_win_buf_alloc(self.total_count)

        if not self.memhandle:
            raise MemoryError("Failed to allocate buffer memory")

        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [])
        self.ax.set_xlim(0, self.points_per_channel - 1)
        self.ax.set_ylim(-10, 10)  # Set limits appropriate to your expected signal range

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.configure_device()
        self.start_continuous_scan()

    def configure_device(self):
        ul.a_chan_input_mode(self.board_num, self.low_chan, AnalogInputMode.DIFFERENTIAL)

    def start_continuous_scan(self):
        rate=10
        scan_options = ScanOptions.CONTINUOUS | ScanOptions.BACKGROUND | ScanOptions.SCALEDATA
        ul.a_in_scan(self.board_num, self.low_chan, self.high_chan, self.total_count, self.rate, ULRange.BIP10VOLTS, self.memhandle, scan_options)
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=itertools.count(), interval=100, blit=True)

    def update_plot(self, frame):
        # Example assumes you fetch new data for each frame; adjust as needed for your buffer management
        buffer_array = ul.scaled_win_buf_to_array(self.memhandle, 0, self.total_count)
        self.line.set_data(np.arange(len(buffer_array)), buffer_array)
        return self.line,

    def __del__(self):
        if self.memhandle:
            ul.win_buf_free(self.memhandle)
            self.stop_scan()

    def stop_scan(self):
        ul.stop_background(self.board_num, FunctionType.AIFUNCTION)





    def init_ui(self):
        self.pack(fill=tk.BOTH, expand=True)
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def update_display(self):
        value = app.read_analog_input(0)  # Ensure 'app' is correctly referenced and accessible
        if value is not None:
            self.scalar_label.config(text=f"{self.base_text}: {value:.2f} V")
        else:
            self.scalar_label.config(text=f"{self.base_text}: Error")
        self.after(100, self.update_display)

    def __del__(self):
        if hasattr(self, 'memhandle') and self.memhandle:
            ul.win_buf_free(self.memhandle)
            ul.stop_background(self.board_num, ScanOptions.BACKGROUND)

    def remove_widget(self):
        self.destroy()

    def rename_widget(self):
        new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=self)
        if new_name:
            self.base_text = new_name
            self.scalar_label.config(text=f"{self.base_text}: {self.value:.2f} V")

    def run_example(self):
        # Use the provided example to configure and start the scan
        rate = 10
        points_per_channel = 10
        total_count = points_per_channel  # Adjust based on your setup
        scan_options = ScanOptions.BACKGROUND | ScanOptions.SCALEDATA
        memhandle = ul.scaled_win_buf_alloc(self.memhandle, 0, 10)

        try:
            ul.a_in_scan(self.board_num, 0, 0, total_count, rate, ULRange.BIP10VOLTS, memhandle, scan_options)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scan: {e}")
        finally:
            ul.win_buf_free(memhandle)

# Main application class that sets up the dashboard
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
        new_label = DigitalInBinaryIndicator(self.dashboard_frame, self.board_num, DigitalPortType.FIRSTPORTA)
        new_label.place(x=20, y=100)

    def add_counter(self):
        new_counter = CounterDisplay(self.dashboard_frame, self.board_num)
        new_counter.place(x=20, y=180)
    
    def add_analog_in(self):
    # Pass the board number to the AnalogInDisplay constructor
        display = AnalogInDisplay(self.dashboard_frame, self.board_num)
        display.place(x=20, y=260)


    def read_analog_input(self, channel, range_type=ULRange.BIP10VOLTS):
        """Reads an analog input from the specified channel."""
        try:
            # Reading from the specified channel and converting to engineering units.
            # This assumes you have an Analog Input capable device and channel indexing starts from 0.
            raw_value = ul.a_in(self.board_num, channel, range_type)
            eng_units_value = ul.to_eng_units(self.board_num, range_type, raw_value)
            return eng_units_value
        except ULError as e:
            print(f"Error reading analog input: {e}")
            return None  # Return None or a default value in case of error

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

# Entry point of the application
if __name__ == '__main__':
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
