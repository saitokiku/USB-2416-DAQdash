# analog_input.py
from mcculw import ul
from config import BOARD_NUM, AI_CHANNEL, AI_RANGE

def read_analog_input(channel=AI_CHANNEL, ai_range=AI_RANGE):
    return ul.a_in(BOARD_NUM, channel, ai_range)
