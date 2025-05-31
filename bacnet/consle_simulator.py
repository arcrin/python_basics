from pyDAQ.UniversalIO import UniversalIO
from pyDAQ.UART import DAQ_UART
import serial
import threading
import re

ansi_escape = re.compile(rb'\x1B\[[0-9;]*[A-Za-z]') 

def clean_response(data: bytes) -> bytes:
    return ansi_escape.sub(b'', data)

debug_uart = serial.Serial("COM38", baudrate=115200, timeout=2)
# daq = UniversalIO()
# debug_uart = DAQ_UART(daq, "EXP4", baudrate=115200, timeout=60)

def read_from_port(ser:serial.Serial) -> None:
    while True:
        response = ser.read_until(b'#')
        response = clean_response(response)
        if response:
            print(response.decode('ascii', errors='ignore'), end='')

thread = threading.Thread(target=read_from_port, args=(debug_uart,), daemon=True)
thread.start()

print("Serial Console Started. Type your commands below:")
try:
    while True:
        command = input()
        debug_uart.write((command + '\n').encode()) 
except KeyboardInterrupt:
    print("\nExiting console.")
    debug_uart.close() 
