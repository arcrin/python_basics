from interface.quattro.libQuattro import quattro
from datetime import datetime
from interface.quattroHelpers import getProductInfo
import time

bac = quattro()

while True:
    bac.ReinitializeDescriptors()
    cpu_status = bac.DeviceExists(200, timeout=1)
    print(f"{datetime.now()}: {cpu_status}")
    time.sleep(1)