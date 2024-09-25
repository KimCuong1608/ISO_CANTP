from tp_layer import CAN_TP
from tp_layer import DiagRx
import time
import can

rx = DiagRx()

# bus2 = can.Bus(interface='neovi', channel=1, bitrate=500000)
bus2 = can.Bus('test', interface='virtual')
tp2 = CAN_TP(bus2, False, 8)
# tp2.runFCThread()
can.Notifier(bus2, [tp2])
tp2.addObserver(rx)

bus1 = can.Bus('test', interface='virtual')
tp1 = CAN_TP(bus1, False, 8)
can.Notifier(bus1, [tp1])
tp1.addObserver(rx)

data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]
id = 0xC0FFEE

# tp1.sendData(data)
# data = [0x0a, 0x0b, 0x0c]
# tp1.sendData(data)

while True:
    tp1.sendData(data, id)
    time.sleep(5)
