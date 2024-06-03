import tkinter as tk
from tkinter import simpledialog

def on_drag_start(event):
    widget = event.widget
    if getattr(widget, 'locked', False):
        return
    widget._drag_start_x = event.x
    widget._drag_start_y = event.y

def on_drag_motion(event):
    widget = event.widget
    if getattr(widget, 'locked', False):
        return
    x = widget.winfo_x() - widget._drag_start_x + event.x
    y = widget.winfo_y() - widget._drag_start_y + event.y
    widget.place(x=x, y=y)

def right_click_menu(event, widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Remove Block", command=widget.destroy)
    menu.add_command(label="Rename Block", command=lambda: rename_widget(widget))
    menu.add_command(label="Lock in place", command=lambda: toggle_lock(widget))
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def rename_widget(widget):
    new_name = simpledialog.askstring("Rename Block", "Enter new name:", parent=widget)
    if new_name:
        if hasattr(widget, 'rename_widget'):
            widget.rename_widget(new_name)
        elif isinstance(widget, (tk.Label, tk.Button)):
            widget.config(text=f"{new_name}: {getattr(widget, 'value', '')}")
        elif isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=f"{new_name}: {getattr(widget, 'value', '')}")

def toggle_lock(widget):
    widget.locked = not getattr(widget, 'locked', False)
    lock_status = "Locked" if widget.locked else "Unlocked"
    print(f"Widget {lock_status}")
    
    if widget.locked:
        widget.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
    else:
        widget.config(highlightthickness=0)

