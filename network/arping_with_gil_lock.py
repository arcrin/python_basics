import threading
import time
from scapy.layers.l2 import arping
from interface.Ethernet import get_jig_iface


class GILBlocker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.daemon = True

    def run(self):
        while self.running:
            _ = sum(i * i for i in range(10000000))

    def stop(self):
        self.running = False 


def run_arping():
    target_ip = "169.254.107.3"
    iface = get_jig_iface()
    
    print("Starting arping() operation...")

    try:
        gil_blocker = GILBlocker()
        gil_blocker.start()

        ack, nack = arping(target_ip, timeout=1, iface=iface, verbose=False)

        if ack:
            response_mac = ack[0][1].src.upper()
            print(f"Response received: {response_mac}") 
        else:
            print("No response from device.")

    finally:
        gil_blocker.stop()
        gil_blocker.join()

    print("arping() operation completed.")


if __name__ == "__main__":
    run_arping() 