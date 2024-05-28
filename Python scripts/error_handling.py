# error_handling.py
from mcculw import ul

def handle_error(error_code):
    if error_code != 0:
        error_message = ul.get_error_message(error_code)
        print(f"Error {error_code}: {error_message}")
