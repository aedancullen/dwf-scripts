import sys
import numpy as np

THRESH = 0.7

for filename in sys.argv[1:]:
    print(filename)
    with open(filename, 'r') as fh:
        lines = [line for line in fh if not line.startswith('#') and not line.startswith('\n')]
        data = np.loadtxt(lines, delimiter=',', skiprows=1)
    last_p = 0
    last_n = 0
    reg = 0b0
    count = None
    for i in range(data.shape[0]):
        p = data[i][1]
        n = data[i][2]
        if p > THRESH and last_p < THRESH:
            if count is not None:
                count += 1
            reg |= (0b1 << 8)
            reg >>= 1
        elif n > THRESH and last_n < THRESH:
            if count is not None:
                count += 1
            reg >>= 1

        if count is None and reg == 0b10000111:
            count = 0

        if count == 8:
            count = 0
            print(hex(reg), end=" ")
            reg = 0b0

        last_p = p
        last_n = n

    if count is not None:
        print()
