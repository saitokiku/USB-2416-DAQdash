import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange
from mcculw.device_info import DaqDeviceInfo
from mcculw.ul import ULError
from ctypes import cast, POINTER, c_double
import time
import threading


# Configuration Parameters
device_id_list = []  # List of device IDs to use; if empty, the first detected device will be used
board_num = 0
low_chan = 0
high_chan = 0  # Assuming a single channel for simplicity; adjust as needed
rate = 1  # Rate per channel
total_rate = rate * (high_chan - low_chan + 1)  # Total rate for all channels
ai_range = ULRange.BIP10VOLTS  # Voltage range
points_per_channel = 100
total_count = points_per_channel * (high_chan - low_chan + 1)
scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA

def config_device():
    """Configure the device based on the specified settings."""
    try:
        if device_id_list:
            DaqDeviceInfo(board_num).config_first_detected_device(board_num, device_id_list)
        print("Device configured successfully.")
    except ULError as e:
        print("Error configuring device:", e)

def update_plot(ax, line, fig, buffer):
    """Update the plot with new data."""
    while True:
        if not ul.get_status(board_num, ScanOptions.BACKGROUND)[0]:
            break
        time.sleep(0.1)  # More responsive update rate
        new_data = np.array(buffer[:total_count])  # Copy data
        line.set_ydata(new_data)
        ax.set_ylim(new_data.min() - 1, new_data.max() + 1)  # Dynamically adjust y-limits
        ax.relim()
        ax.autoscale_view(True, True, True)
        fig.canvas.draw()
        fig.canvas.flush_events()

# Initialize plot
fig, ax = plt.subplots()
x_data = np.arange(0, points_per_channel)
y_data = np.zeros(points_per_channel)
ln, = ax.plot(x_data, y_data, 'r-')
ax.set_ylim(-10, 10)  # Set initial y-axis limits

def init():
    ln.set_data(x_data, y_data)
    return ln,

def update(frame):
    memhandle = ul.scaled_win_buf_alloc(total_count)
    if not memhandle:
        print("Failed to allocate memory.")
        return ln,
    
    ctypes_array = cast(memhandle, POINTER(c_double))
    buffer = np.ctypeslib.as_array(ctypes_array, shape=(total_count,))

    try:
        ul.a_in_scan(board_num, low_chan, high_chan, total_count, total_rate, ai_range, memhandle, scan_options)
        data = buffer[:points_per_channel]  # Ensure only the expected number of points are used
        ln.set_data(x_data, data)
        ax.set_ylim(min(data) - 1, max(data) + 1)  # Dynamically adjust y-limits based on data
    except ULError as e:
        print("Error during scan:", e)
    finally:
        ul.win_buf_free(memhandle)
    return ln,

ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True)
plt.show()

def run_scan():
    """Run the data acquisition scan."""
    memhandle = ul.scaled_win_buf_alloc(total_count)
    if not memhandle:
        raise Exception("Failed to allocate memory.")
    
    ctypes_array = cast(memhandle, POINTER(c_double))
    buffer = np.ctypeslib.as_array(ctypes_array, shape=(total_count,))
    try:
        ul.a_in_scan(board_num, low_chan, high_chan, total_count, total_rate, ai_range, memhandle, scan_options)
        print("Scan started successfully.")
        return buffer
    except ULError as e:
        print("Error starting scan:", e)
        return None
    finally:
        ul.win_buf_free(memhandle)

def main():
    config_device()
    buffer = run_scan()
    if buffer is not None:
        fig, ax = plt.subplots()
        line, = ax.plot(buffer, 'r-')  # Red line plot
        ax.set_ylim(-10, 10)  # Initial y-axis limits
        threading.Thread(target=update_plot, args=(ax, line, fig, buffer), daemon=True).start()
        plt.show()

if __name__ == '__main__':
    main()
