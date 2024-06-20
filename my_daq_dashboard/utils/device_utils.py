# device_utils.py
from mcculw import ul
from mcculw.enums import InterfaceType, InfoType, AiChanType, BoardInfo, AnalogInputMode

def initialize_device(board_num):
    ul.ignore_instacal()
    devices = ul.get_daq_device_inventory(InterfaceType.USB)
    if devices:
        device = devices[0]
        ul.create_daq_device(board_num, device)
        return device
    else:
        raise Exception("No DAQ devices found")

def set_channel_settings(board_num):
    channel = 0
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)
    ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
    ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 1000)
