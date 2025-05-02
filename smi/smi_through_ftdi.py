# type: ignore
import serial
import time
import codecs

import serial.tools
import serial.tools.list_ports
from interface.devcon import getPortFromInstance

SERIAL_PORT = getPortFromInstance(3, serial="!DEVELOP0000") 
BAUD_RATE = 2400 


# def find_smi_port(vid=None, pid=None, keyword=None):
#     ports = serial.tools.list_ports.comports()
#     for port in ports:
#         if vid and pid:
#             if (port.vid == vid and port.pid == pid):
#                 return port.device
#         elif keyword:
#             if keyword.lower() in port.description.lower():
#                 return port.device
#     return None


# ports = serial.tools.list_ports.comports()
# for port in ports:
#     print(f"Port: {port.device}")
#     print(f"  VID: {port.vid}, PID: {port.pid}")
#     print(f"  Serial Number: {port.serial_number}")
#     print(f"  Description: {port.description}")
#     print(f"  Interface: {port.interface}")  # Often indicates A/B/C/etc.
#     print()

try: 
    smi_ser = serial.Serial(port=SERIAL_PORT, baudrate=2400, timeout=5)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
    smi_ser.flush()
    smi_ser.reset_input_buffer()
    
    while True:
        data = smi_ser.read(1)
        data = codecs.encode(data, 'hex')
        if data == b'8b':
            smi_ser.write(b'\x70\x05\x8b')
            smi_ser.write(b'\xef\x45\x4b\xe9\x68')
            smi_ser.reset_input_buffer()

except KeyboardInterrupt:
    print("\nExiting on Ctrl+C")
    
except serial.SerialException as e:
    print(f"Serial error: {e}")

finally:
    if "smi_ser" in locals() and smi_ser.is_open:
        smi_ser.close()
        print("Serial port closed")