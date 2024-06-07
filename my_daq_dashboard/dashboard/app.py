import tkinter as tk
from tkinter import Menu, messagebox, ttk, filedialog, PhotoImage
from mcculw import ul
from mcculw.enums import InterfaceType, DigitalPortType, InfoType, BoardInfo
from dashboard.widgets.digital_out_button import DigitalOutButton
from dashboard.widgets.digital_in_binary_indicator import DigitalInBinaryIndicator
from dashboard.widgets.counter_display import CounterDisplay
from dashboard.widgets.analog_in_display import AnalogInDisplay
import os
import json

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title('DAQ Dashboard')
        self.root.geometry("800x600")
        self.board_num = 0
        self.serial_number = "Unknown"
        self.logo_image = PhotoImage(file="C:/Users/mbhardwaj/OneDrive - Inogen/Documents/Measurement Computing/MC-USB-2416/USB-2416-DAQdash/my_daq_dashboard/ino.png")

        # Set the icon
        self.set_icon("C:/Users/mbhardwaj/OneDrive - Inogen/Documents/Measurement Computing/MC-USB-2416/USB-2416-DAQdash/my_daq_dashboard/icon.png")

        # Set a theme
        self.load_azure_theme()

        # Create Frames
        self.create_frames()

        # Create Header
        self.create_header()

        # Create Menu
        self.create_menu()

        # Initialize device
        self.initialize_device()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_azure_theme(self):
        # Path to the azure.tcl file
        azure_theme_path = "C:\\Users\\mbhardwaj\\OneDrive - Inogen\\Documents\\Measurement Computing\\MC-USB-2416\\USB-2416-DAQdash\\my_daq_dashboard\\azure\\azure.tcl"
        
        # Load the theme
        self.root.tk.call("source", azure_theme_path)
        ttk.Style().theme_use('azure-dark')

    def set_icon(self, icon_path):
        self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
    

    def create_frames(self):
        self.header_frame = ttk.Frame(self.root, padding="10")
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.status_frame = ttk.Frame(self.root, padding="5")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create the first tab
        self.add_tab()

    def create_header(self):
        self.serial_label = ttk.Label(self.header_frame, text=f"Board Serial Number: {self.serial_number}", anchor="e")
        self.serial_label.pack(side=tk.LEFT)

        self.image_label = ttk.Label(self.header_frame, image=self.logo_image)
        self.image_label.pack(side=tk.LEFT, padx=(10, 10))

        self.title_label = ttk.Label(self.header_frame, text="MCC DAQ Dashboard", font=("Helvetica", 18))
        self.title_label.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(self.status_frame, text="Status: Ready", anchor="w")
        self.status_label.pack(side=tk.LEFT)


    def create_menu(self):
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.dashboard_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Components', menu=self.dashboard_menu)
        self.dashboard_menu.add_command(label='Add Digital Out', command=self.add_digital_out)
        self.dashboard_menu.add_command(label='Add Digital In', command=self.add_digital_in)
        self.dashboard_menu.add_command(label='Add Counter Display', command=self.add_counter)
        self.dashboard_menu.add_command(label='Add Analog In Display', command=self.add_analog_in)
        self.dashboard_menu.add_separator()
        self.dashboard_menu.add_command(label='New Tab', command=self.add_tab)
        self.dashboard_menu.add_command(label='Save Tab', command=self.save_tab)
        self.dashboard_menu.add_command(label='Load Tab', command=self.load_tab)

        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Save Scan Data', command=self.save_scan_data)

    def add_tab(self):
        tab_count = len(self.notebook.tabs()) + 1
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=f"Tab {tab_count}")
        self.create_widgets(new_tab)

    def create_widgets(self, parent_frame):
        # Any widgets specific to the tab should be added here
        pass

    def add_digital_out(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        new_button = DigitalOutButton(current_tab, self.board_num)
        new_button.place(x=20, y=20)
        self.update_status("Added Digital Out Button")

    def add_digital_in(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        new_label = DigitalInBinaryIndicator(current_tab, self.board_num, DigitalPortType.FIRSTPORTA)
        new_label.place(x=20, y=100)
        self.update_status("Added Digital In Indicator")

    def add_counter(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        new_counter = CounterDisplay(current_tab, self.board_num)
        new_counter.place(x=20, y=180)
        self.update_status("Added Counter Display")

    def add_analog_in(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        display = AnalogInDisplay(current_tab, app=self)
        display.place(x=20, y=260)
        self.update_status("Added Analog In Display")

    def read_analog_input(self, channel):
        value = 0.0  # Placeholder for actual data reading
        return value

    def initialize_device(self):
        try:
            ul.ignore_instacal()
            devices = ul.get_daq_device_inventory(InterfaceType.USB)
            if devices:
                device = devices[0]
                ul.create_daq_device(self.board_num, device)
                
                max_config_len = 100
                self.serial_number = ul.get_config_string(
                    InfoType.BOARDINFO, self.board_num, 0, BoardInfo.DEVUNIQUEID, max_config_len
                )
                
                self.serial_label.config(text=f"Board Serial Number: {self.serial_number}")
                messagebox.showinfo("Device Info", f"Successfully connected to {device.product_name}.")
                self.update_status(f"Connected to {device.product_name}")
            else:
                messagebox.showwarning("Device Warning", "No DAQ devices found.")
                self.update_status("No DAQ devices found")
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.update_status("Initialization Error")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def on_closing(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, AnalogInDisplay):
                widget.remove_widget()
        self.root.destroy()

    def save_tab(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        tab_config = []
        
        for widget in current_tab.winfo_children():
            widget_info = {
                "class": widget.__class__.__name__,
                "x": widget.winfo_x(),
                "y": widget.winfo_y(),
                "width": widget.winfo_width(),
                "height": widget.winfo_height()
            }
            # Add custom name if applicable
            if hasattr(widget, 'custom_name'):
                widget_info['custom_name'] = widget.custom_name
            tab_config.append(widget_info)

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(tab_config, file)
            self.update_status(f"Saved tab to {file_path}")


    def load_tab(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                tab_config = json.load(file)
            self.add_tab()
            current_tab = self.notebook.nametowidget(self.notebook.select())

            for widget_info in tab_config:
                class_name = widget_info["class"]
                x = widget_info["x"]
                y = widget_info["y"]
                custom_name = widget_info.get('custom_name', None)

                if class_name == "DigitalOutButton":
                    new_widget = DigitalOutButton(current_tab, self.board_num, custom_name=custom_name)
                elif class_name == "DigitalInBinaryIndicator":
                    new_widget = DigitalInBinaryIndicator(current_tab, self.board_num, DigitalPortType.FIRSTPORTA)
                    if custom_name:
                        new_widget.rename(custom_name)
                elif class_name == "CounterDisplay":
                    new_widget = CounterDisplay(current_tab, self.board_num, custom_name=custom_name)
                elif class_name == "AnalogInDisplay":
                    new_widget = AnalogInDisplay(current_tab, app=self)
                    if custom_name:
                        new_widget.rename(custom_name)
                else:
                    continue

                new_widget.place(x=x, y=y)

            self.update_status(f"Loaded tab from {file_path}")

    def save_scan_data(self):
        rate = 1  # Set to a lower rate if needed for testing
        file_name = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_name:
            try:
                scan_to_file = ScanToFile(self.board_num, rate, file_name)
                scan_to_file.run_scan()
                self.update_status(f"Saved scan data to {file_name}")
                print(f"Scan data saved to {file_name}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
                self.update_status("Save Error")





