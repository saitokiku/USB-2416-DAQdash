import tkinter as tk
from mcculw import ul
from mcculw.enums import DigitalPortType
from utils.events import on_drag_start, on_drag_motion, right_click_menu

class DigitalOutButton(tk.Button):
    def __init__(self, master, board_num, channel=0, **kwargs):
        super().__init__(master, text='Digital Out: OFF', font=('Helvetica', 14), height=2, width=20, **kwargs)
        self.board_num = board_num
        self.channel = channel
        self.state = False
        self.value = 'OFF'  # Add a value attribute
        self.custom_name = "Digital Out"  # Add a custom name attribute
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.config(command=self.toggle)

    def toggle(self):
        self.state = not self.state
        self.value = 'ON' if self.state else 'OFF'
        ul.d_bit_out(self.board_num, DigitalPortType.FIRSTPORTA, self.channel, self.state)
        self.config(text=f"{self.custom_name}: {self.value}")

    def rename(self, new_name):
        self.custom_name = new_name
        self.config(text=f"{self.custom_name}: {self.value}")
