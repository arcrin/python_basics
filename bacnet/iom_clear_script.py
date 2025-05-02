import serial
import threading
import time
import re

ansi_escape = re.compile(rb'\x1B\[[0-9;]*[A-Za-z]') 

class SerialConsole:
    def __init__(self, port:str, baudrate:int=115200, timeout:int=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout) 
        self.buffer = bytearray()
        self.lock = threading.Lock()
        self.running = True
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()
        
    def _reader(self):
        while self.running:
            data = self.ser.read(self.ser.in_waiting or 1)
            if data:
                with self.lock:
                    self.buffer.extend(data)

    def read_until_prompt(self, prompt:str='#', timeout=60):
        prompt_bytes = prompt.encode()
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                clean_response = ansi_escape.sub(b'', self.buffer)
                if prompt_bytes in clean_response:
                    index = clean_response.index(prompt_bytes)
                    output = clean_response[:index + len(prompt_bytes)] 
                    self.buffer = self.buffer[index + len(prompt_bytes):]
                    return output.decode('ascii', errors='ignore')
            time.sleep(0.1)
        raise Exception(f"Wait {prompt} command timeout")

    def send(self, command):
        self.ser.write((command + '\n').encode())

    def close(self):
        self.running = False
        self.reader_thread.join()
        self.ser.close()
        

def wait_for_bootup(console: SerialConsole):
    if console.read_until_prompt('Controller Service is running'):
        print('Controller online')
        return
   
def login(console: SerialConsole):
    console.send('')
    if console.read_until_prompt('login:', timeout=2):
        console.send('root')
    
    if console.read_until_prompt('Password:', timeout=2):
        console.send('b%9P$MdeQP][')
    output = console.read_until_prompt('~#', timeout=2)
    if output:
        print("Logged in!")
        console.send('echo Hello')
        print(console.read_until_prompt('#'))

    
        
if __name__ == '__main__':
    console = SerialConsole("COM38")

    # wait_for_bootup(console) # this step is necessary. We don't want to get into U-boot
    
    # log_in(console)

    # console.close()
