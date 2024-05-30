from tkinter import Menu, messagebox
import tkinter as tk  # Make sure to import tk
from mcculw import ul
from mcculw.enums import InterfaceType, DigitalPortType
from dashboard.widgets.digital_out_button import DigitalOutButton
from dashboard.widgets.digital_in_binary_indicator import DigitalInBinaryIndicator
from dashboard.widgets.counter_display import CounterDisplay
from dashboard.widgets.analog_in_display import AnalogInDisplay

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
        display = AnalogInDisplay(self.dashboard_frame, app=self)
        display.place(x=20, y=260)

    def read_analog_input(self, channel):
        value = 0.0  # Placeholder for actual data reading los

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
