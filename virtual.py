from can_tp import CAN_TP
from can_tp import DiagRx
import time
import can

if __name__ == "__main__":

    rx = DiagRx()

    # Init Rx Node
    bus2 = can.Bus('test', interface='virtual')
    tp2 = CAN_TP(bus2, False, 8)
    can.Notifier(bus2, [tp2])
    tp2.addObserver(rx)

    # Init Tx Node
    bus1 = can.Bus('test', interface='virtual')
    tp1 = CAN_TP(bus1, False, 8)
    can.Notifier(bus1, [tp1])
    tp1.addObserver(rx)

    # Data Test
    data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]
    id = 0xC0FFEE

    while True:
        tp1.sendData(data, id)
        time.sleep(5)
