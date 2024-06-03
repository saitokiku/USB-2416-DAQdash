import tkinter as tk
from mcculw import ul
from mcculw.enums import DigitalPortType
from mcculw.ul import ULError
from utils.events import on_drag_start, on_drag_motion, right_click_menu

class DigitalInBinaryIndicator(tk.Label):
    def __init__(self, master, board_num, port_type, **kwargs):
        super().__init__(master, font=('Helvetica', 14), height=2, width=20, **kwargs)
        self.board_num = board_num
        self.port_type = port_type
        self.locked = False
        self.value = 0  # Add a value attribute
        self.update_indicator_id = None  # To store the after callback ID
        self.custom_name = "Digital In"  # Add a custom name attribute
        self.bind("<Button-1>", on_drag_start)
        self.bind("<B1-Motion>", on_drag_motion)
        self.bind("<Button-3>", lambda event: right_click_menu(event, self))
        self.update_indicator()

    def update_indicator(self):
        try:
            self.value = ul.d_in(self.board_num, self.port_type)
            # Change background color based on the value
            if self.value == 0:
                self.config(bg='lightgrey')
            else:
                self.config(bg='#90EE90')  # Calm, mild green color
            self.update_indicator_id = self.after(100, self.update_indicator)  # Refresh every 100ms
        except ULError as e:
            print(f"Error reading digital input: {e}")
        except tk.TclError:
            # This exception occurs if the widget is destroyed while the callback is still scheduled
            return

    def rename(self, new_name):
        self.custom_name = new_name
        self.config(text=f"{self.custom_name} {self.port_type.name}: {self.value}")

    def remove_widget(self):
        if self.update_indicator_id:
            self.after_cancel(self.update_indicator_id)  # Cancel the scheduled update
        self.destroy()
