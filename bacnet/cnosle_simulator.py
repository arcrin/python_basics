import serial
import threading
import re

ansi_escape = re.compile(rb'\x1B\[[0-9;]*[A-Za-z]') 

def clean_response(data: bytes) -> bytes:
    return ansi_escape.sub(b'', data)

debug_uart = serial.Serial("COM38", baudrate=115200, timeout=2)

def read_from_port(ser):
    while True:
        response = debug_uart.read_until(b'#')
        response = clean_response(response)
        if response:
            print(response.decode('ascii', errors='ignore'), end='')

thread = threading.Thread(target=read_from_port, args=(debug_uart,), daemon=True)
thread.start()

print("Serial Console Started. Type your commands below:")
try:
    while True:
        command = input()
        debug_uart.write((command + '\r').encode()) 
except KeyboardInterrupt:
    print("\nExiting console.")
    debug_uart.close() 
