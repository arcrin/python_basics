import threading
from scapy.layers.l2 import arping
import time

def threaded_arping():
    ack, nack = arping("169.254.107.3", timeout=1, verbose=False)
    if ack:
        print("Response received: ", ack[0][1].hwsrc)
    else:
        print("No response.")
    time.sleep(1)


def heavy_computation():
    while True:
        [x**2 for x in range(10000)]



arping_thread = threading.Thread(target=threaded_arping) 
arping_thread.start()

cpu_thread = threading.Thread(target=heavy_computation)
cpu_thread.start()