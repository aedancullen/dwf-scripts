from ctypes import *
import math
import sys
import time

import os
import pty

dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()

#dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(6), byref(hdwf)) # 6 -> 1V8 Digital

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

cRX = c_int(0)
fParity = c_int(0)

dwf.FDwfDigitalUartRateSet(hdwf, c_double(115200))
dwf.FDwfDigitalUartTxSet(hdwf, c_int(0)) # TX = DIO-0
dwf.FDwfDigitalUartRxSet(hdwf, c_int(1)) # RX = DIO-1
dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 none, 1 odd, 2 even
dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length

dwf.FDwfDigitalUartTx(hdwf, None, c_int(0))# initialize TX, drive with idle level
dwf.FDwfDigitalUartRx(hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception

rgRX = create_string_buffer(1024)

m, s = pty.openpty()
print(os.ttyname(s))

os.set_blocking(m, False)

try:
    while True:
        time.sleep(0.001)
        dwf.FDwfDigitalUartRx(hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), byref(fParity))
        if cRX.value > 0:
            rgRX[cRX.value] = 0
            sz = rgRX.value
            os.write(m, sz)
        bts = None
        try:
            bts = os.read(m, 1024)
        except:
            pass
        if bts:
            rgTX = create_string_buffer(bts)
            dwf.FDwfDigitalUartTx(hdwf, rgTX, c_int(sizeof(rgTX)-1))

except KeyboardInterrupt: # Ctrl+C
    pass

dwf.FDwfDeviceCloseAll()
