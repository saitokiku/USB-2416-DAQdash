# main.py
import analog_input as ai
import analog_output as ao
import digital_io as dio

def run_application():
    # Example of reading an analog input
    voltage = ai.read_analog_input()
    print(f"Voltage on AI channel: {voltage}")

    # Example of writing to an analog output
    ao.write_analog_output(channel=0, value=2.5)

    # Example of setting and reading a digital IO
    dio.configure_digital_channel(channel=0, direction=DigitalIODirection.OUT)
    dio.write_digital_channel(channel=0, state=1)
    state = dio.read_digital_channel(channel=1)
    print(f"State of DIO channel: {state}")

if __name__ == "__main__":
    run_application()
