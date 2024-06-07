import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange, FunctionType, Status, InterfaceType, InfoType, BoardInfo, AiChanType, AnalogInputMode
from mcculw.device_info import DaqDeviceInfo
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

def release_device():
    try:
        ul.release_daq_device(board_num)
        print("Released DAQ device successfully.")
    except Exception as e:
        print(f"Error releasing device: {e}")

def discover_and_configure_device():
    """Discover and configure the first detected USB-2416 device."""
    try:
        # Reset the board number to avoid conflicts
        ul.release_daq_device(board_num)

        # Get the device inventory
        devices = ul.get_daq_device_inventory(InterfaceType.ANY)
        if not devices:
            raise Exception("No DAQ devices found")
        
        # Check for the specific product ID and configure the device
        for device in devices:
            if device.product_id in [208, 209, 253, 254]:
                ul.create_daq_device(board_num, device)
                print(f"Configured device: {device.product_name}")
                return True
        else:
            raise Exception("No supported DAQ device found")
    except Exception as e:
        print(f"Error discovering and configuring device: {e}")
        return False

def set_channel_settings(board_num):
    try:
        channel = 0
        # Set channel type to voltage
        ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)
        # Set to differential input mode
        ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
        # Set data rate to 1000Hz
        ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 1000)
        print("Channel settings configured successfully.")
    except Exception as e:
        print(f"Error setting channel settings: {e}")

def update_plot(frame, buffer, ln, ax):
    """Update the plot with new data."""
    try:
        status, curr_count, curr_index = ul.get_status(board_num, FunctionType.AIFUNCTION)
        if status == Status.RUNNING and curr_count >= points_per_channel:
            # Get the latest data from the buffer
            new_data = np.frombuffer(buffer, dtype=np.float64)[:points_per_channel]
            print(f"Buffer data (first 10 samples): {new_data[:10]}")  # Debugging: print first 10 samples
            if len(new_data) == points_per_channel:
                ln.set_ydata(new_data)
                ax.set_ylim(new_data.min() - 1, new_data.max() + 1)  # Dynamically adjust y-limits
        return ln,
    except Exception as e:
        print(f"Error updating plot: {e}")

def run_scan(buffer):
    """Run the data acquisition scan."""
    try:
        ul.a_in_scan(board_num, low_chan, high_chan, total_count, rate, ai_range, buffer.ctypes.data, scan_options)
        print("Scan started successfully.")
    except Exception as e:
        print(f"Error starting scan: {e}")

def main():
    if not discover_and_configure_device():
        return  # Exit if device configuration fails
    set_channel_settings(board_num)
    
    # Allocate buffer for the data
    buffer = np.zeros(total_count, dtype=np.float64)
    
    scan_thread = threading.Thread(target=run_scan, args=(buffer,), daemon=True)
    scan_thread.start()

    fig, ax = plt.subplots()
    x_data = np.arange(0, points_per_channel)
    y_data = np.zeros(points_per_channel)
    ln, = ax.plot(x_data, y_data, 'r-')
    ax.set_ylim(-10, 10)  # Initial y-axis limits

    ani = FuncAnimation(fig, update_plot, fargs=(buffer, ln, ax), interval=100, cache_frame_data=False)
    plt.show()

    release_device()  # Ensure the device is released after the script ends

if __name__ == '__main__':
    main()
