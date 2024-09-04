# Tweak register settings over I2C in a mysterious Novatek OLED DDIC

from ctypes import *
import math
import sys
import time

dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()

#dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) # 6 -> 1V8 Digital

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

ADDR = 0x4C
rgRX = rgRX = (c_ubyte*2)()
pNak = c_int(0)

dwf.FDwfDigitalI2cRateSet(hdwf, c_double(50000))
dwf.FDwfDigitalI2cSclSet(hdwf, c_int(0))
dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(1))
dwf.FDwfDigitalI2cStretchSet(hdwf, c_int(0)) # If you don't explicitly disable clock stretching, I2C RX data is just garbage!
dwf.FDwfDigitalI2cClear(hdwf, byref(pNak))
if pNak.value == 0:
    print("I2C bus error. Check the pull-ups.")
    dwf.FDwfDeviceCloseAll()
    sys.exit()

def read_reg(main, param):
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*2)(main, param), c_int(2), byref(pNak))
    dwf.FDwfDigitalI2cRead(hdwf, c_int(ADDR << 1), rgRX, c_int(2), byref(pNak))
    return rgRX[1]

print("0A 00:", read_reg(0x0A, 0x00))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*2)(0x28, 0x00), c_int(2), byref(pNak))
time.sleep(0.1)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*2)(0x10, 0x00), c_int(2), byref(pNak))
time.sleep(0.1)

print("0A 00:", read_reg(0x0A, 0x00))

print("80 00:", read_reg(0x80, 0x00))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0x80, 0x00, 0x00, 0x01), c_int(4), byref(pNak))
time.sleep(0.1)
print("80 00:", read_reg(0x80, 0x00))

dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*2)(0x11, 0x00), c_int(2), byref(pNak))
time.sleep(0.1)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*2)(0x29, 0x00), c_int(2), byref(pNak))
time.sleep(0.1)
print("0A 00:", read_reg(0x0A, 0x00))

dwf.FDwfDeviceCloseAll()
