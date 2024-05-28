"""
File: digital_out.py

Library Call Demonstrated: mcculw.ul.d_out() and mcculw.d_bit_out()

Purpose: Writes to a digital output port.

Demonstration: Configures the first digital port for output
               (if necessary) and writes a value to the port and
               the first bit.

Other Library Calls: mcculw.ul.d_config_port()
                     mcculw.ul.release_daq_device()

Special Requirements: Device must have a digital output port
                      or have digital ports programmable as output.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

def toggle_led(board_num, led_state):
    """
    Toggle the LED connected to digital output 0.
    Args:
        board_num (int): The board number of the DAQ device.
        led_state (bool): True to turn LED on, False to turn it off.
    """
    bit_num = 0
    bit_value = 1 if led_state else 0
    port = DaqDeviceInfo(board_num).get_dio_info().port_info[0]  # Assuming port 0 supports output
    print('Setting digital output', bit_num, 'to', bit_value)
    ul.d_bit_out(board_num, port.type, bit_num, bit_value)

def run_example():
    use_device_detection = True
    dev_id_list = []
    board_num = 0

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_digital_io:
            raise Exception('Error: The DAQ device does not support digital I/O')

        print('\\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\\n', sep='')

        if daq_dev_info.get_dio_info().port_info[0].is_port_configurable:
            ul.d_config_port(board_num, daq_dev_info.get_dio_info().port_info[0].type, DigitalIODirection.OUT)

        toggle_led(board_num, True)  # Example of turning the LED on

    except Exception as e:
        print('\\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)

if __name__ == '__main__':
    run_example()
