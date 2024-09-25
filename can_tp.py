import can
import time 
import threading

from threading import Thread
from threading import Event
from abc import ABC, abstractmethod
from random import randrange

# CAN TP Frame Types
SINGLE_FRAME = 0x00
FIRST_FRAME = 0x10
CONSECUTIVE_FRAME = 0x20
FLOW_CONTROL = 0x30
 
# Flow Control Types
FC_CTS = 0x00  # Clear To Send
FC_WAIT = 0x10
FC_OVFLW = 0x20

# Padding Byte
PADDING = 0xC0

# List DLC
dlc = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]

class CAN_TP(can.Listener):

    # ------------------- OBSERVER ------------------- #
    # Observer method: Đối tượng quan sát, subscriber.
    # Thường sử dụng với Notifier, quản lý danh sách Observer, publisher
    class Observer(ABC):
        @abstractmethod
        # abstract method được định nghĩa bởi các lớp con
        def on_cantp_msg_received(self, data):
            pass

    # ------------------- NOTIFIER ------------------- #
    # Quản lý danh sách Observer, thông báo cho các Observer.
    # Observer nhận được thông báo sẽ tự chạy @abtract method
    # -- API for reading data - register as observer --

    # add Observer vào danh sách
    def addObserver(self, observer:Observer):
        self.observers.append(observer)

    # noti tới các Obs trong danh sách 
    def notify(self):
        payload = self.rx_data[:self.rx_data_size]
        # convert to hex 
        payload_str = " ".join(["{:02X}".format(byte) for byte in payload])
        print(f"CAN_TP::notify- {payload_str}")
        for observer in self.observers:
            observer.on_cantp_msg_received(payload)

    # ------------------- LISTENER ------------------- #

    # can.Listener Overrides
    def on_error(self, exc: Exception) -> None:
        print(f"CAN_TP::error : {exc}")
        return super().on_error(exc)
    
    def on_message_received(self, msg: can.Message) -> None:
        data = msg.data
        self.rx_dl = dlc[msg.dlc % 16] # Get Payload Length

        log_msg = "RX    -    ID: {:04X}    DL: {:02X}    Data: {}".format(msg.arbitration_id, msg.dlc, " ".join(["{:02X} ".format(byte) for byte in msg.data]))
        print(log_msg) 
        # check N_PCI
        if data[0] & 0xF0 == SINGLE_FRAME:
            self.readSingleFrame(data)
            return
        
        if data[0] & 0xF0 == FIRST_FRAME:
            self.arbitration_id = msg.arbitration_id
            self.received_blocks = 0
            self.readFirstFrame(data)

            self.rx_session = True
            self.sendFC()
            return

        if data[0] & 0xF0 == CONSECUTIVE_FRAME:
            if msg.arbitration_id == self.arbitration_id:
                self.received_blocks += 1
                self.readConsecutiveFrame(data)
                self.Ev_Cr.clear() 
                if not (self.received_blocks % self.BS_rx):
                    if(len(self.rx_data) < self.rx_data_size):
                        self.Ev_Cr.set()
                    else:
                        self.rx_session = False
            return
            
        if data[0] & 0xF0 == FLOW_CONTROL:
            self.readFlowControlFrame(data)
            return 
        
    # ------------------- CANTP STUFF ------------------- #
    # Init
    def __init__(self, bus, is_fd: bool, can_dl):
        # CAN TP protocols
        self.Ev_Bs = Event()
        self.Ev_Cr = Event()
        self.rx_session = False

        self.STmin_tx = 0x14 # 20ms
        self.STmin_rx = 0x14 # 20ms
        self.BS_tx = 4
        self.BS_rx = 4
        self.BS_max = 4096
        self.received_blocks = 0
        self.WFTmax = 5

        # Timming
        self.N_As = 1.000 # Time for transmission of the CAN frame (any N_PDU) on the sender side
        self.N_Ar = 1.000 # Time for transmission of the CAN frame (any N_PDU) on the receiver side
        self.N_Bs = 1.000 # Time until reception of the next FlowControl N_PDU
        self.N_Br = 0.100 # Time until transmission of the next FlowControl N_PDU, (N_Br + N_Ar) < (0,9 × N_Bs timeout)
        self.N_Cs = 0.000 # Time until transmission of the next ConsecutiveFrame N_PDU, = STmin, (N_Cs + N_As) < (0,9 × N_Cr timeout)
        self.N_Cr = 1.000 # Time until reception of the next Consecutive Frame N_PDU
    
        # Lower Layer
        self.bus = bus  
        self.is_fd = is_fd

        # Upper Layer
        self.rx_buffer_size = 80

        # N-PDU: 
        self.rx_data = []
        self.rx_data_size = 0
        self.arbitration_id = 0 #RxPduId

        # Observers List
        self.observers = []

        # Set Payload Length
        if  self.is_fd:
            self.tx_dl = dlc[can_dl % 16]
        else: 
            if can_dl % 16 >= 8:
                self.tx_dl = 8
            else:
                self.tx_dl = dlc[can_dl % 16]

    def check_buffer_status(self):
        # Giả lập việc quản lý buffer
        if (self.rx_buffer_size - len(self.rx_data)) <= (self.BS_rx * (self.rx_dl-1)):
            return FC_WAIT  # Buffer không đủ, yêu cầu tạm dừng
        elif self.rx_data_size >= self.rx_buffer_size:
            return FC_OVFLW  # Buffer không đáp ứng data_size
        else:
            return FC_CTS  # Buffer còn nhiều, tiếp tục gửi

    # Read Data
    def readSingleFrame(self, data):
        if self.rx_dl <= 8:
            self.rx_data_size = data[0]
            self.rx_data = [byte for byte in bytes(data[1:])]
        else:
            self.rx_data_size = data[1]
            self.rx_data = [byte for byte in bytes(data[2:])]
        self.notify()
    
    def readFirstFrame(self, data):
        self.rx_data_size = ((data[0] & 0x0F) << 8) | data[1]
        if self.rx_data_size == 0:
            self.rx_data_size = (((((data[2] << 8) | data[3]) << 8) | data[4]) << 8) | data[5]  
            self.rx_data = [byte for byte in bytes(data[6:])]
        else:
            self.rx_data = [byte for byte in bytes(data[2:])]

    def readConsecutiveFrame(self, data):
        self.rx_data += [byte for byte in bytes(data[1:])]
        if len(self.rx_data) >= self.rx_data_size:
            self.notify()

    def readFlowControlFrame(self, data):
    # Kiểm tra loại Flow Control: CTS, Wait, Overflow
        flow_status = data[0] & 0x0F

        if flow_status == FC_CTS:
            with threading.Lock():
                print("Received Flow Control: CTS (Continue to Send)")
            # if STmin < 127 => ms else => us
            self.STmin_rx = (data[2] / 10e3) if (data[2] <= 0x7F) else (self.STmin_rx + (data[2] / 10e6))
            self.N_Cs = self.STmin_rx
            # if BS = 0 => BS = BS_max => non flow ctrl 
            self.BS_tx = data[1] if data[1] else self.BS_max
            # Continue To Send
            self.Ev_Bs.set()

        elif flow_status == FC_WAIT:
            with threading.Lock():
                print("Received Flow Control: Wait (Temporarily pause transmission)")
            self.Ev_Bs.clear()

        elif flow_status == FC_OVFLW:
            with threading.Lock():
                print("Received Flow Control: Overflow (Buffer is full, stop transmission)")
            self.Ev_Bs.clear()
            raise Exception("Flow Control: Overflow - TX stopped due to RX buffer overflow")


    # Write Data
    def sendMessage(self, msg):
        msg = can.Message(arbitration_id=self.arbitration_id, data=msg, is_extended_id=False, is_fd=self.is_fd)
        self.bus.send(msg, timeout=self.N_As) #N_As

    def writeSingleFrame(self, data):
        data_len = len(data)
        if self.is_fd == False:
            msg = [data_len] + data
        else: 
            msg = [FIRST_FRAME & 0xF0] + [data_len & 0xFF] + data
        # padding if len < can_dl
        msg += [PADDING for i in range(self.tx_dl - len(msg))]
        self.sendMessage(msg)

    def writeFirstFrame(self, data):
        self.seq_num = 0
        data_len = len(data)
        if data_len > 4095:
            last_idx = self.tx_dl - 6
            msg = [FIRST_FRAME & 0xF0] + [0x00] + [data_len & 0xFFFFFFFF] + data[:last_idx]
        else:
            last_idx = self.tx_dl - 2
            msg = [FIRST_FRAME | ((data_len & 0xF00) >> 8) ] + [(data_len & 0xFF)] + data[:last_idx]
            self.sendMessage(msg)
        return data[last_idx:]
    
    def writeConsecutiveFrame(self, data):
        data_len = len(data)
        last_idx = (data_len % self.tx_dl) if (data_len < self.tx_dl) else (self.tx_dl - 1)
        self.seq_num = (self.seq_num + 1) % 16
        msg = [CONSECUTIVE_FRAME | self.seq_num] + data[:last_idx]
        msg += [PADDING for i in range(self.tx_dl-len(msg))]
        self.sendMessage(msg)
        return data[last_idx:]
    
    def writeFlowControlFrame(self):
        # Test different scenarios
        WFTcount = 0
        while self.rx_session:
            flow_status = self.check_buffer_status()
            msg = [FLOW_CONTROL | (flow_status >> 4), self.BS_rx, self.STmin_rx]
            msg += [PADDING for i in range(self.tx_dl-len(msg))]
            if flow_status == FC_CTS:
                self.sendMessage(msg)
                # self.rx_buffer_size = randrange(55, 65, 3)
                if self.Ev_Cr.wait(self.N_Cr):
                    self.rx_buffer_size = randrange(55, 65, 3) # change buffer length to test multiple scenarios
                else:
                    with threading.Lock():
                        print ("Can_TP::receiveConsecutiveFrame : Cr Timeout")
            elif flow_status == FC_OVFLW:   
                self.sendMessage(msg)
                self.rx_buffer_size = randrange(55, 65, 3) # change buffer length to test multiple scenarios
                self.rx_session = False                   
            else:
                self.sendMessage(msg)
                self.rx_buffer_size = randrange(55, 65, 3) # change buffer length to test multiple scenarios
                WFTcount += 1
                if WFTcount == self.WFTmax:
                    with threading.Lock():
                        print("Can_TP::reachMaxWaitFrameTimes : WFTmax")
                    self.rx_session = False
            time.sleep(self.N_Br)   

    def writeMultiFrame(self, data):
        # reset
        block_count = 0
        self.Ev_Bs.clear()
        # sent first reame 
        data = self.writeFirstFrame(data)
        data_len = len(data)
        timeout = 0

        while data_len:
            # wait for ctrl flow msg
            timeout = 0 if self.Ev_Bs.wait(self.N_Bs) else (timeout+1) #N_Bs
            
            if timeout == 0: 
                # send consecutive frame
                data = self.writeConsecutiveFrame(data)
                data_len = len(data)
                time.sleep(self.STmin_rx)
                block_count += 1
                #all blocks sent, wait for ctrl flow again 
                if block_count % self.BS_tx == 0:
                    self.Ev_Bs.clear()
                    block_count = 0

            elif timeout >= 1:
                with threading.Lock():
                    print("CAN_TP::writeMultiFrame : flow ctrl timeout")
                break

    # API for writing data
    def sendData(self, data, id):
        self.arbitration_id = id
        if len(data) < 8:
            self.writeSingleFrame(data)
        elif len(data) <= min(self.tx_dl,64) and self.is_fd == True:
            self.writeSingleFrame(data)
        else:
            th = Thread(target=self.writeMultiFrame(data))
            th.daemon = True
            th.start()

    def sendFC(self):
        th = Thread(target=self.writeFlowControlFrame)
        th.daemon = True
        th.start()

# ------------------- LISTENER ------------------- #
class DiagRx(CAN_TP.Observer):
    def on_cantp_msg_received(self, data):
        # print("notify : " + " ".join([hex(byte) for byte in data]))
        # Implementing the listener functionality
        pass


            


