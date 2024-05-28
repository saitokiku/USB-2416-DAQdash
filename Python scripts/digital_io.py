# digital_io.py
from mcculw import ul
from mcculw.enums import DigitalIODirection
from config import BOARD_NUM

def configure_digital_channel(channel, direction):
    ul.d_config_bit(BOARD_NUM, channel, direction)

def read_digital_channel(channel):
    return ul.d_bit_in(BOARD_NUM, channel)

def write_digital_channel(channel, state):
    ul.d_bit_out(BOARD_NUM, channel, state)
