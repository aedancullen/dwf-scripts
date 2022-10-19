# Dump all registers over I2C from a mysterious Novatek OLED DDIC

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
rgRX = (c_ubyte*2)()
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

def dump(fh):
    for main in range(0x100):
        print(main)
        for param in range(16):
            res = read_reg(main, param).to_bytes(1, byteorder="little")
            fh.write(res)
        fh.write(main.to_bytes(1, byteorder="little"))

with open("dump_default.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x00, 0x00, 0xAA), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x01, 0x00, 0x10), c_int(4), byref(pNak))
with open("dump_cmd2p0.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x00, 0x00, 0xAA), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x01, 0x00, 0x11), c_int(4), byref(pNak))
with open("dump_cmd2p1.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x00, 0x00, 0xAA), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x01, 0x00, 0x12), c_int(4), byref(pNak))
with open("dump_cmd2p2.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x00, 0x00, 0xAA), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x01, 0x00, 0x13), c_int(4), byref(pNak))
with open("dump_cmd2p3.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x00, 0x00, 0xAA), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xF0, 0x01, 0x00, 0x14), c_int(4), byref(pNak))
with open("dump_cmd2p4.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xFF, 0x00, 0x00, 0x5A), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xFF, 0x01, 0x00, 0x80), c_int(4), byref(pNak))
with open("dump_cmd3p0.bin", "wb") as fh:
    dump(fh)
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xFF, 0x00, 0x00, 0x5A), c_int(4), byref(pNak))
dwf.FDwfDigitalI2cWrite(hdwf, c_int(ADDR << 1), (c_ubyte*4)(0xFF, 0x01, 0x00, 0x81), c_int(4), byref(pNak))
with open("dump_cmd3p1.bin", "wb") as fh:
    dump(fh)

dwf.FDwfDeviceCloseAll()
