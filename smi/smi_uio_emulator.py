# type: ignore
import codecs
from dataclasses import dataclass

from pyDAQ.UniversalIO import UniversalIO
from pyDAQ.UART import DAQ_UART


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

daq = UniversalIO()
uart = DAQ_UART(daq, "EXP1", baudrate=115200)

daq.write(f"conf responder uartresponse {uart.peripheral_name}")
ignore_echo = 1
s = f"set responder {ignore_echo} {' '.join(c.encode() for c in configs)}"
daq.write(s)

while 1:
    r = daq.write(f"status responder")
    print(r)