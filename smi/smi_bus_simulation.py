# type: ignore
from pyDAQ.UniversalIO import UniversalIO, I2C
from pyDAQ.UART import DAQ_UART
from pyDAQ.Expanders import PCA9538A_GPIO
from interface.quattro.libQuattro import quattro
from dataclasses import dataclass
import threading
import codecs
import time 



@dataclass
class Config:
    command: str
    response: str
    repeat_count: int

    def encode(self):
        return f"{codecs.encode(self.command.encode(), 'hex').decode()} {codecs.encode(self.response.encode(), 'hex').decode()} {self.repeat_count}"

configs = (
    Config("foo", "foo test", 3),
    Config("bar", "bar test", 3),
)

bac = quattro()

daq = UniversalIO()
bottom_i2c = I2C(daq, "EXP2", frequency=100000)  
dut_power_control = PCA9538A_GPIO(bottom_i2c, 0x70, 7, mode='op') 
top_engagement_control = PCA9538A_GPIO(bottom_i2c, 0x71, 0, mode='op')
smi_selection = PCA9538A_GPIO(bottom_i2c, 0x70, 1, "op")
smi_ref = PCA9538A_GPIO(bottom_i2c, 0x71, 1, 'op')
smi_uart = DAQ_UART(daq, "EXP3", baudrate=2400, timeout=10)
daq.write(f"conf responder uartresponse {smi_uart.peripheral_name}")
# daq.write(f"set responder 70058B EF454BE998 3 1")

def cpu_power_on():
    daq['VOUT_enable'].value = 1

def cpu_power_off():
    daq['VOUT_enable'].value = 0
    
def dut_power_on():
    daq['VBUS_enable'].value = 1
    dut_power_control.value = 1
    daq['CAN_enable'].value = 1

def dut_power_off():
    daq['CAN_enable'].value = 0
    dut_power_control.value = 0
    daq['VBUS_enable'].value = 0
    
def select_smi():
    smi_selection.value = 1
    smi_ref.value = 1

def engage_top():
    top_engagement_control.value = 1
    
class SMIBusThread(threading.Thread):
    def __init__(self, jig_daq):
        threading.Thread.__init__(self)
        self._daq = jig_daq
        self.bus_emulation = True
    
    def run(self):
        print("Start emulating SMI drive")
        self._daq.flush()
        self._daq.reset_input_buffer()
        while self.bus_emulation:
            # self._daq.write(f"set responder 70058B 70058BEF454BE968 3 1")
            data = self._daq.read(1)
            data = codecs.encode(data, "hex")
            if data == b"8b":
                self._daq.write(b'\x70\x05\x8b')
                self._daq.write(b'\xef\x45\x4b\xe9\x98')
        print("SMI drive emulation stopped")
            
def stop_smi_emulation(smi_thread):
    smi_thread.bus_emulation = False
    smi_thread.join()

configs = (Config("70058B", "EF454BE998", 1), Config("3000D0", "FFFFFFE0FF", 1))
s = f"set responder 1 {' '.join(c.encode() for c in configs)}"


cpu_power_on()
dut_power_on()
engage_top()
select_smi()

# while True:
#     print(smi_uart.read(1))
#     time.sleep(0.1)