import tkinter as tk
from tkinter import filedialog, messagebox
from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status, ULRange
from ctypes import c_double, cast, POINTER, addressof, sizeof
import threading
import numpy as np
from utils.device_utils import initialize_device, set_channel_settings

class ContinuousDataRecorder(tk.Frame):
    def __init__(self, master, board_num, low_chan=0, high_chan=0, rate=100, **kwargs):
        super().__init__(master, **kwargs)
        self.board_num = board_num
        self.low_chan = low_chan
        self.high_chan = high_chan
        self.rate = rate
        self.recording = False
        self.buffer_size_seconds = 2
        self.ul_buffer_count = self.rate * self.buffer_size_seconds
        self.file_path = None

        self.start_button = tk.Button(self, text="Start Recording", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        try:
            device = initialize_device(self.board_num)
            set_channel_settings(self.board_num)
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.start_button.config(state=tk.DISABLED)

        self.pack()

    # ... rest of the ContinuousDataRecorder class remains unchanged ...


    def start_recording(self):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not self.file_path:
            return

        try:
            self.recording = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            self.memhandle = ul.scaled_win_buf_alloc(self.ul_buffer_count)
            if not self.memhandle:
                raise Exception("Failed to allocate memory")

            scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA
            ai_range = ULRange.BIP10VOLTS

            ul.a_in_scan(self.board_num, self.low_chan, self.high_chan, self.ul_buffer_count, self.rate, ai_range, self.memhandle, scan_options)

            self.recording_thread = threading.Thread(target=self.record_data, daemon=True)
            self.recording_thread.start()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.stop_recording()

    def record_data(self):
        try:
            with open(self.file_path, 'w') as file:
                # Write CSV header
                header = ",".join([f"Channel {ch}" for ch in range(self.low_chan, self.high_chan + 1)])
                file.write(header + "\n")

                write_chunk_size = self.ul_buffer_count // 10
                write_chunk_array = (c_double * write_chunk_size)()
                prev_count = 0
                prev_index = 0

                while self.recording:
                    status, curr_count, _ = ul.get_status(self.board_num, FunctionType.AIFUNCTION)
                    new_data_count = curr_count - prev_count
                    if new_data_count >= write_chunk_size:
                        if prev_index + write_chunk_size > self.ul_buffer_count:
                            first_chunk_size = self.ul_buffer_count - prev_index
                            second_chunk_size = write_chunk_size - first_chunk_size
                            ul.scaled_win_buf_to_array(self.memhandle, write_chunk_array, prev_index, first_chunk_size)
                            ul.scaled_win_buf_to_array(self.memhandle, cast(addressof(write_chunk_array) + first_chunk_size * sizeof(c_double), POINTER(c_double)), 0, second_chunk_size)
                        else:
                            ul.scaled_win_buf_to_array(self.memhandle, write_chunk_array, prev_index, write_chunk_size)

                        prev_count += write_chunk_size
                        prev_index += write_chunk_size
                        prev_index %= self.ul_buffer_count

                        # Write data to file
                        for i in range(write_chunk_size):
                            file.write(f"{write_chunk_array[i]:.5f},")
                            if (i + 1) % (self.high_chan - self.low_chan + 1) == 0:
                                file.write("\n")

                    if status == Status.IDLE:
                        break

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            ul.stop_background(self.board_num, FunctionType.AIFUNCTION)
            ul.win_buf_free(self.memhandle)
            self.recording = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_recording(self):
        self.recording = False

    def on_closing(self):
        self.stop_recording()
        self.destroy()
