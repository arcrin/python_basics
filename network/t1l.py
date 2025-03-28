# type: ignore
from scapy.all import srp
from scapy.layers.l2 import arping, Ether, ARP, ARPingResult
from interface.Ethernet import get_jig_iface
from typing import Optional
from time import sleep


# def custom_arping(ip: str, iface: str, timeout: int = 2, retries: int=3) -> Optional[str]:
#     """
#     Custom arping function to send ARP requrests and capture responses.

#     Args:
#         ip (str): The target IP address to ping.
#         iface (str): The network interface to use for sending the packet.
#         timeout (int): How long to wait for a reply (in seconds)
#         retries (int): Number of retry attempts if no response is received.

#     Returns:
#         str: The MAC address of the target if successful, otherwise None. 
#     """
#     # Create an ARP request packet
#     arp_request = ARP(pdst=ip)
#     broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
#     packet = broadcast / arp_request

#     for attempt in range(retries):
#         # Send the ARP request and wait for a reply
#         ack, nack = srp(packet, timeout=timeout, iface=iface, verbose=False)

#         if ack:
#             for sent, received in ack:
#                 mac_address = received.hwsrc
#                 print(f"[Attempt {attempt+1}] Response from {ip}: {mac_address.upper()}") 
#                 return mac_address.upper()
        
#         # No response, wait and retry
#         print(f"[Attempt {attempt+1}] No response from {ip} retrying...")
#         sleep(1)

#     print(f"Failed to reach {ip} after {retries} attempts.")
#     return None



iface = get_jig_iface()

# print(custom_arping("169.254.107.3", iface))
while True:
    ack, nack = arping("169.254.107.3", timeout=1, iface=iface)
    print(ack[0][1].src.upper())
    sleep(1)
    