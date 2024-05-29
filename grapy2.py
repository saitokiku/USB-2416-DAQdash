import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange, FunctionType, Status
from mcculw.device_info import DaqDeviceInfo
from ctypes import cast, POINTER, c_double
import time
import threading

# Configuration Parameters
board_num = 0
low_chan = 0
high_chan = 0  # Assuming a single channel for simplicity; adjust as needed
rate = 10  # Rate per channel
points_per_channel = 100
total_count = points_per_channel * (high_chan - low_chan + 1)
ai_range = ULRange.BIP10VOLTS  # Voltage range
scan_options = ScanOptions.BACKGROUND | ScanOptions.SCALEDATA | ScanOptions.CONTINUOUS

def config_device():
    """Configure the device based on the specified settings."""
    try:
        DaqDeviceInfo(board_num).config_first_detected_device(board_num, [208, 209, 253, 254])
        print("Device configured successfully.")
    except Exception as e:
        print("Error configuring device:", e)

def update_plot(ax, line, fig, buffer):
    """Update the plot with new data."""
    while True:
        status, curr_count, curr_index = ul.get_status(board_num, FunctionType.AIFUNCTION)
        if status == Status.IDLE:
            break
        time.sleep(0.1)  # More responsive update rate
        new_data = np.array(buffer[:points_per_channel])  # Copy data
        line.set_ydata(new_data)
        ax.set_ylim(new_data.min() - 1, new_data.max() + 1)  # Dynamically adjust y-limits
        fig.canvas.draw()
        fig.canvas.flush_events()

def run_scan():
    """Run the data acquisition scan."""
    memhandle = ul.scaled_win_buf_alloc(total_count)
    if not memhandle:
        raise Exception("Failed to allocate memory.")
    
    ctypes_array = cast(memhandle, POINTER(c_double))
    buffer = np.ctypeslib.as_array(ctypes_array, shape=(total_count,))
    try:
        ul.a_in_scan(board_num, low_chan, high_chan, total_count, rate, ai_range, memhandle, scan_options)
        print("Scan started successfully.")
        return buffer
    except Exception as e:
        print("Error starting scan:", e)
        return None

def main():
    config_device()
    buffer = run_scan()
    if buffer is not None:
        fig, ax = plt.subplots()
        x_data = np.arange(0, points_per_channel)
        y_data = np.zeros(points_per_channel)
        ln, = ax.plot(x_data, y_data, 'r-')
        ax.set_ylim(-10, 10)  # Initial y-axis limits

        def init():
            ln.set_data(x_data, y_data)
            return ln,

        def update(frame):
            new_data = np.array(buffer[:points_per_channel])  # Copy data
            ln.set_data(x_data, new_data)
            ax.set_ylim(new_data.min() - 1, new_data.max() + 1)  # Dynamically adjust y-limits
            return ln,

        ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True)
        threading.Thread(target=update_plot, args=(ax, ln, fig, buffer), daemon=True).start()
        plt.show()

if __name__ == '__main__':
    main()
