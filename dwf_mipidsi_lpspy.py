# Decode MIPI DSI LP-mode commands on lane 0 from a set of scope or logic captures

import sys
import numpy as np
from numba import njit

THRESH = 0.7

@njit
def process_one_dataset(data):
    last_p = 0
    last_n = 0
    reg = 0b0
    count = -1
    out = []
    for i in range(data.shape[0]):
        p = data[i, 0]
        n = data[i, 1]
        if p > THRESH and last_p < THRESH:
            if count != -1:
                count += 1
            reg |= (0b1 << 8)
            reg >>= 1
        elif n > THRESH and last_n < THRESH:
            if count != -1:
                count += 1
            reg >>= 1

        if count == -1 and reg == 0b10000111:
            count = 0

        if count == 8:
            count = 0
            out.append(reg)
            reg = 0b0

        if count != -1 and p > THRESH and n > THRESH:
            count = -1
            out.append(-1)

        last_p = p
        last_n = n

    return out

for filename in sys.argv[1:]:
    print("Loading", filename)
    data = np.loadtxt(filename, delimiter=',', dtype=np.float32, usecols=range(0,2), skiprows=10)
    print("Processing", filename)
    out = process_one_dataset(data)
    for item in out:
        if item != -1:
            print(hex(item), end=" ")
        else:
            print()
