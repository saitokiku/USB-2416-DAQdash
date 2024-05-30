import tkinter as tk
from tkinter import simpledialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange, FunctionType, Status, InterfaceType, InfoType, BoardInfo, AiChanType, AnalogInputMode
from mcculw.device_info import DaqDeviceInfo
from ctypes import c_double
import threading
from utils.events import on_drag_start, on_drag_motion, right_click_menu

class AnalogInDisplay(tk.Frame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # Store the DashboardApp instance
        self.custom_name = "Analog In"
        self.value = 0.00
        self.scalar_label = tk.Label(self, text=f"{self.custom_name}: {self.value:.2f} V", font=('Helvetica', 14), height=2, width=20)
        self.scalar_label.pack()

        self.board_num = 0
        self.low_chan = 0
        self.high_chan = 0  # Assuming a single channel for simplicity; adjust as needed
        self.rate = 10  # Rate per channel
        self.points_per_channel = 100
        self.total_count = self.points_per_channel * (self.high_chan - self.low_chan + 1)
        self.ai_range = ULRange.BIP10VOLTS  # Voltage range
        self.scan_options = ScanOptions.BACKGROUND | ScanOptions.SCALEDATA | ScanOptions.CONTINUOUS

        self.buffer = np.zeros(self.total_count, dtype=np.float64)
        self.discover_and_configure_device()
        self.set_channel_settings(self.board_num)

        self.init_plot()
        self.run_scan()

        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))

    def init_plot(self):
        self.fig, self.ax = plt.subplots()
        self.x_data = np.arange(0, self.points_per_channel)
        self.y_data = np.zeros(self.points_per_channel)
        self.ln, = self.ax.plot(self.x_data, self.y_data, 'r-')
        self.ax.set_ylim(-10, 10)  # Initial y-axis limits

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100, cache_frame_data=False)

    def update_plot(self, frame):
        try:
            status, curr_count, curr_index = ul.get_status(self.board_num, FunctionType.AIFUNCTION)
            if status == Status.RUNNING:
                new_data = np.frombuffer(self.buffer, dtype=np.float64)[:self.points_per_channel]
                self.ln.set_ydata(new_data)
                self.ax.set_ylim(new_data.min() - 1, new_data.max() + 1)  # Dynamically adjust y-limits
            self.canvas.draw()
            return self.ln,
        except Exception as e:
            print(f"Error updating plot: {e}")

    def run_scan(self):
        try:
            scan_thread = threading.Thread(target=self._run_scan_thread, daemon=True)
            scan_thread.start()
        except Exception as e:
            print(f"Error starting scan: {e}")

    def _run_scan_thread(self):
        try:
            ul.a_in_scan(self.board_num, self.low_chan, self.high_chan, self.total_count, self.rate, self.ai_range, self.buffer.ctypes.data, self.scan_options)
            print("Scan started successfully.")
        except Exception as e:
            print(f"Error starting scan: {e}")

    def discover_and_configure_device(self):
        try:
            self.release_device()  # Ensure any previously configured device is released
            devices = ul.get_daq_device_inventory(InterfaceType.ANY)
            if not devices:
                raise Exception("No DAQ devices found")
            
            for device in devices:
                if device.product_id in [208, 209, 253, 254]:
                    ul.create_daq_device(self.board_num, device)
                    print(f"Configured device: {device.product_name}")
                    return
            else:
                raise Exception("No supported DAQ device found")
        except Exception as e:
            print(f"Error discovering and configuring device: {e}")

    def set_channel_settings(self, board_num):
        try:
            channel = 0
            ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)
            ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
            ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 1000)
            print("Channel settings configured successfully.")
        except Exception as e:
            print(f"Error setting channel settings: {e}")

    def release_device(self):
        try:
            ul.release_daq_device(self.board_num)
            print("Released DAQ device successfully.")
        except Exception as e:
            print(f"Error releasing device: {e}")

    def remove_widget(self):
        self.release_device()
        self.destroy()

    def rename_widget(self, new_name):
        self.custom_name = new_name
        self.scalar_label.config(text=f"{self.custom_name}: {self.value:.2f} V")
