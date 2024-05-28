import matplotlib.pyplot as plt
import numpy as np
from mcculw import ul
from mcculw.enums import ScanOptions, ULRange, InfoType, BoardInfo, AiChanType, AnalogInputMode, FunctionType
from mcculw.device_info import DaqDeviceInfo
from ctypes import cast, POINTER, c_double

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

def run_example():
    use_device_detection = True
    dev_id_list = [253, 254, 208, 209]
    board_num = 0
    low_chan = 0
    high_chan = 0
    num_chans = high_chan - low_chan + 1

    if use_device_detection:
        config_first_detected_device(board_num, dev_id_list)

    daq_dev_info = DaqDeviceInfo(board_num)
    print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
          daq_dev_info.unique_id, ')\n', sep='')

    rate = 1  # Acquisition rate in Hz
    points_per_channel = 100  # Points per channel to display
    total_count = points_per_channel * num_chans
    scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA

    memhandle = ul.scaled_win_buf_alloc(total_count)
    if not memhandle:
        raise Exception('Error: Failed to allocate memory')

    set_channel_settings(board_num)

    # Prepare the plot
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'r-')  # Starting with empty data
    ax.set_autoscaley_on(True)
    ax.set_xlim(0, points_per_channel - 1)
    ax.grid()
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    # Start the scan
    ul.a_in_scan(board_num, low_chan, high_chan, total_count, rate, ULRange.BIP10VOLTS, memhandle, scan_options)

    x_data = list(range(points_per_channel))
    y_data = np.zeros(points_per_channel)
    line.set_data(x_data, y_data)
    ctypes_array = cast(memhandle, POINTER(c_double))

    try:
        while True:
            # Update the plot with the new data
            status, curr_count, _ = ul.get_status(board_num, FunctionType.AIFUNCTION)
            if curr_count > 0:
                # Read the data from the buffer
                data_array = np.array([ctypes_array[i] for i in range(curr_count)])
                y_data = np.roll(y_data, -curr_count)
                y_data[-curr_count:] = data_array
                line.set_ydata(y_data)
                ax.relim()
                ax.autoscale_view(True, True, True)
                text.set_text(f'Latest Voltage: {y_data[-1]:.3f} V')
                fig.canvas.draw()
                fig.canvas.flush_events()
    finally:
        ul.stop_background(board_num, FunctionType.AIFUNCTION)
        if memhandle:
            ul.win_buf_free(memhandle)
        ul.release_daq_device(board_num)
        plt.ioff()  # Turn off interactive plotting
        plt.show()  # Keep the window open until manually closed by the user

def set_channel_settings(board_num):
    channel = 0
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)
    ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 1000)

if __name__ == '__main__':
    run_example()
