# type: ignore
from pyDAQ.UniversalIO import UniversalIO
from pyDAQ.UART import DAQ_UART
import re
import time


ansi_escape = re.compile(rb'\x1B\[[0-9;]*[A-Za-z]') 
new_line = re.compile(rb'\r\n')

class CPUConsole:
    def __init__(self, daq_uart:DAQ_UART):
        self._uart = daq_uart
    
    def read_until_prompt(self, prompt:str='#', timeout:int=60, verbose:bool=False) -> str:
        start_time = time.time()
        while time.time() - start_time < timeout:
            line_in_bytes = self._uart.read_untils(prompt, timeout=1)
            clean_response = ansi_escape.sub(b'', line_in_bytes)
            # clean_response = new_line.sub(b'', clean_response) 
            clean_response_str = clean_response.decode("ascii")
            if prompt in clean_response_str:
                if verbose:
                    print(clean_response_str)
                return clean_response_str
            time.sleep(0.1)
        raise RuntimeError(f"Could not reach prompt: {prompt}")

    def send(self, command:str) -> None:
        self._uart.write((command + '\n').encode())
        
    def close(self) -> None:
        self._uart.close()
        
    def wait_for_shell_prompt(self, current_dir:str) -> None:
        self.send("")
        if not self.read_until_prompt(f"{current_dir}#", timeout=3):
           raise TimeoutError(f"Shell prompt not detected: {current_dir}") 
       
    def wait_for_bootup(self):
        try:
            if self.read_until_prompt("Controller Service"):
                print("Controller online")
        except RuntimeError as e:
            raise RuntimeError(f"CPU Boot up timeout: {e}")
        
    def login(self) -> None:
        self.send("")
        if self.read_until_prompt("login:", timeout=2):
            self.send("root")
        
        if self.read_until_prompt("Password:", timeout=2):
            self.send("b%9P$MdeQP][")
        response = self.read_until_prompt("~#", timeout=2)
        if response:
            print("CPU login successful!")
            self.send("echo Hello")
            print(self.read_until_prompt("#"))

    def redirect(self, dest_dir) -> str:
            try:
                self.wait_for_shell_prompt("")
                self.send(f" cd {dest_dir}")
                if not self.read_until_prompt(f"{dest_dir}#", timeout=2):
                    raise TimeoutError(f"Timeout waiting for redirect to {dest_dir}")
            except Exception as e:
                raise RuntimeError(f"Failed to redirect to {dest_dir} with exception: {e}")
    
    def get_process_id(self, process_name:str) -> str:
        try:
            self.send("ps")
            ps_response = self.read_until_prompt("#", timeout=2)
            if not ps_response:
                raise RuntimeError("No response from ps command")
            for line in ps_response.splitlines():
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

    def kill_process(self, process_id:str) -> None:
        try:
            self.send(f"kill -9 {process_id}") 
            self.read_until_prompt("#")
        except Exception as e:
            raise RuntimeError(f"Failed to kill process {process_id}: {e}")
    

    def restart_bnserver(self) -> None:
        try:
            self.redirect("/usr/delta")
            self.wait_for_shell_prompt("/usr/delta")
            controller_pid = self.get_process_id("controller -service")
            self.kill_process(controller_pid)
            self.wait_for_shell_prompt("/usr/delta")
            bnserver_pid = self.get_process_id("bnserver -service") 
            self.kill_process(bnserver_pid)
            self.wait_for_shell_prompt("/usr/delta")
            self.send("rc-service bnserver stop")
            self.wait_for_shell_prompt("/usr/delta")
            self.send("rc-service bnserver start")
            self.wait_for_shell_prompt("/usr/delta")
            self.send("./start.sh")
            if not self.read_until_prompt("ControllerStartup: Starting UltraCap Monitoring", verbose=True):
                raise TimeoutError("Timeout during ./start.sh")
            self.send("")
            self.wait_for_shell_prompt("/usr/delta")
        except Exception as e:
            RuntimeError(f"Failed to restart bnserver with exception: {e}")
       

if __name__ == "__main__":
    daq = UniversalIO()
    uart = DAQ_UART(daq, "EXP4", baudrate=115200, timeout=120)
    cpu_console = CPUConsole(uart)