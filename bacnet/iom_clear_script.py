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
        
    def _reader(self) -> None:
        # [ ]: need exception handling
        while self.running:
            data = self.ser.read(self.ser.in_waiting or 1)
            if data:
                with self.lock:
                    self.buffer.extend(data)

    def read_until_prompt(self, prompt:str='#', timeout:int=60, verbose:bool=False) -> str:
        prompt_bytes = prompt.encode()
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                clean_response = ansi_escape.sub(b'', self.buffer)
                if prompt_bytes in clean_response:
                    index = clean_response.index(prompt_bytes)
                    output = clean_response[:index + len(prompt_bytes)] 
                    if verbose:
                        print(output.decode("ascii", errors="ignore"))
                    self.buffer.clear()
                    return output.decode("ascii", errors="ignore")
            time.sleep(0.1)
        raise RuntimeError(f"Wait {prompt} command timeout")

    def send(self, command:str) -> None:
        # [ ]: Need exception handling
        self.ser.write((command + '\n').encode())

    def close(self) -> None:
        self.running = False
        self.reader_thread.join()
        self.ser.close()

def wait_for_shell_prompt(console:SerialConsole, current_dir: str) -> None:
    console.send('')        
    if not console.read_until_prompt(f"{current_dir}#", timeout=3):
        raise TimeoutError(f"Shell prompt not detected for: {current_dir}") 

def wait_for_bootup(console: SerialConsole) -> None:
    if console.read_until_prompt('Controller Service is running'):
        print('Controller online')
   
def login(console: SerialConsole) -> None:
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
        

def get_process_id(console: SerialConsole, process_name: str) -> str:
    try:
        wait_for_shell_prompt(console, "/usr/delta")
        console.send('ps')
        ps_output = console.read_until_prompt('#', timeout=3)
        if not ps_output:
            raise RuntimeError("No response from ps command")
        for line in ps_output.splitlines():
            if process_name not in line:
                continue
            
            process_details = line.strip().split(None, 3)
            if len(process_details) >= 4:
                pid = process_details[0]
                if pid.isdigit():
                    return pid
        raise Exception(f"{process_name} id not found")

    except Exception as e:
        raise RuntimeError(f"Failed to find process {process_name}: {e}")
    
def kill_process(console: SerialConsole, process_id:str) -> None:
    try:
        wait_for_shell_prompt(console, "/usr/delta")
        console.send(f"kill -9 {process_id}")
        console.read_until_prompt('#', timeout=3)
    except Exception as e:
        raise RuntimeError(f"Failed to kill process {process_id}: {e}")

def redirect(console: SerialConsole, destination_dir: str) -> None:
    try:
        wait_for_shell_prompt(console, "/usr/delta")
        console.send(f"cd {destination_dir}")
        if not console.read_until_prompt(f"{destination_dir}#", timeout=3) :
            raise TimeoutError(f"Timeout waiting for redirect to {destination_dir}")
    except Exception as e:
        raise RuntimeError(f"Failed to redirect to {destination_dir} with exception: {e}")
    
def restart_bnserver(console: SerialConsole) -> None:
    redirect(console, "/usr/delta")
    controller_pid = get_process_id(console, "controller -service")
    bnserver_pid = get_process_id(console, "bnserver -service")
    kill_process(console, controller_pid)
    kill_process(console, bnserver_pid)
    try:
        wait_for_shell_prompt(console, "/usr/delta")
        console.send("rc-service bnserver stop")
        if not console.read_until_prompt("#", timeout=3):
            raise TimeoutError("Timeout during bnserver stop")
        console.send("rc-service bnserver start")
        if not console.read_until_prompt("#", timeout=3):
            raise TimeoutError("Timeout during bnserver start")
        redirect(console, "/usr/delta")
        console.send("./start.sh")
        if not console.read_until_prompt("ControllerStartup: Starting UltraCap Monitoring", verbose=True):
            raise TimeoutError("Timeout during ./start.sh")
        console.send('')
        wait_for_shell_prompt(console, "/usr/delta")
    except Exception as e:
        RuntimeError(f"Failed to restart bnserver with exception: {e}")



if __name__ == '__main__':
    console = SerialConsole("COM38")
