import tkinter as tk
from tkinter import simpledialog

def on_drag_start(event):
    widget = event.widget
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

def right_click_menu(event, widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Remove Block", command=widget.destroy)
    menu.add_command(label="Rename Block", command=lambda: rename_widget(widget))
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def rename_widget(widget):
    new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=widget)
    if new_name:
        if hasattr(widget, 'rename'):
            widget.rename(new_name)
        elif isinstance(widget, (tk.Label, tk.Button)):
            widget.config(text=f"{new_name}: {getattr(widget, 'value', '')}")
        elif isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=f"{new_name}: {getattr(widget, 'value', '')}")
