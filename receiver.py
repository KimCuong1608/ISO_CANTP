from can_tp import CAN_TP
from can_tp import DiagRx
import time
import can

if __name__ == "__main__":

    rx = DiagRx()

    # Init Tx Node
    bus = can.Bus('test', interface='neovi', channel=1, bitrate=500000)
    tp = CAN_TP(bus, False, 8)
    can.Notifier(bus, [tp])
    tp.addObserver(rx)

    while True:
        pass