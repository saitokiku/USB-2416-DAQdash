# analog_output.py
from mcculw import ul
from config import BOARD_NUM, AI_RANGE

def write_analog_output(channel, value, ao_range=AI_RANGE):
    ul.a_out(BOARD_NUM, channel, ao_range, value)
